from structlog import get_logger

from doc_analytics.search import DocumentSearchEngine

logger = get_logger()


import json
from functools import cached_property
from pathlib import Path
from typing import Iterator, List, Literal, Optional, Tuple, Type, Union

from attrs import define, field
from pydantic import BaseModel, Field, ValidationError

from doc_analytics.document import Document


class DocumentList(BaseModel):
    items: List[Document] = Field(default_factory=list)

    @cached_property
    def filter(self) -> 'DocumentFilter':
        return DocumentFilter(self)

    @cached_property
    def get(self) -> 'DocumentGetter':
        """
        A strict API: always returns a single Document,
        or raises ValueError if none or multiple found.
        """
        return DocumentGetter(self) 

    def __add__(self, other: Union['DocumentList', List[Document]]) -> 'DocumentList':
        if isinstance(other, DocumentList):
            return DocumentList(items=self.items + other.items)
        elif isinstance(other, list):
            return DocumentList(items=self.items + other)
        raise TypeError(f"Unsupported operand type(s) for +: 'DocumentList' and '{type(other).__name__}'")
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, DocumentList):
            return self.items == other.items
        if isinstance(other, list):
            return self.items == other
        return NotImplemented

    def __getitem__(self, index: Union[int, slice]) -> Union[Document, 'DocumentList']:
        if isinstance(index, slice):
            return DocumentList(items=self.items[index])
        return self.items[index]

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self) -> Iterator[Document]:
        return iter(self.items)

    def __str__(self) -> str:
        return f"DocumentList({len(self)} items)"

    def __repr__(self) -> str:
        titles = ', '.join(repr(doc.title) for doc in self.items[:3])
        more = '...' if len(self.items) > 3 else ''
        return f"DocumentList([{len(self)} docs: {titles}{more}])"

    @property
    def docIds(self) -> List[str]:
        return [doc.docId for doc in self.items]

    @property
    def titles(self) -> List[str]:
        return [doc.title for doc in self.items]

    @property
    def markdowns(self) -> List[str]:
        return [doc.markdown for doc in self.items]
    
    def gather(self, attribute: str):
        return [getattr(d.metadata, attribute, None) for d in self.items]
    
    def summary(self) -> str:
        return f"{len(self.items)} document(s): " + "\n- ".join(self.titles)

    def append(self, doc: Document) -> None:
        if not isinstance(doc, Document):
            raise ValueError(f'Can only add documents to Documentlist. You passed type {type(doc)}.')
        return self.items.append(doc)


@define
class DocumentFilter:

    docs: DocumentList

    @property
    def items(self) -> List[Document]:
        return self.docs.items

    def by_ids(self, *doc_ids: str) -> Optional[Document] | DocumentList:
        matches = [doc for doc in self.items if doc.docId in doc_ids]    
        if not matches:
            logger.info('Document not found', docIds=doc_ids)
            return None
        elif len(matches) == 1:
            return matches[0]
        else:
            return DocumentList(items=matches)
        
    def by_identifier(self, identifier: str) -> Optional[Document]:
        return next((d for d in self.docs if d.identifier == identifier), None)
    
    def by_identifiers(self, *identifiers: Tuple[str]) -> DocumentList:
        matches = [self.by_identifier(i) for i in identifiers]
        return DocumentList(items=matches)

    def by_keyword(self, keyword: str, on_field: Literal['markdown', 'title', 'instruction'] = 'markdown') -> DocumentList:
        filtered = [
            doc for doc in self.docs
            if keyword.lower() in getattr(doc, on_field, '').lower()
        ]
        return DocumentList(items=filtered)

    def by_title(self, title: str) -> DocumentList:
        filtered = [doc for doc in self.docs if title.lower() in doc.title.lower()]
        return DocumentList(items=filtered)

    def by_breadcrumbs(self, breadcrumbs: List[str]) -> DocumentList:
        """
        Return documents whose .breadcrumbs exactly match the provided list.
        """
        matches = [doc for doc in self.docs if doc.metadata.breadcrumbs == breadcrumbs]
        return DocumentList(items=matches)


@define
class DocumentGetter:
    """
    Like DocumentFilter, but ensures exactly one match.
    """

    docs: DocumentList

    def _unwrap(self, matches: List[Document], description: str) -> Document:
        if not matches:
            raise ValueError(f"No document found for {description}")
        if len(matches) > 1:
            titles = ', '.join(repr(d.title) for d in matches)
            raise ValueError(f"Multiple documents found for {description}: {titles}")
        return matches[0]

    def by_id(self, doc_id: str) -> Document:
        """
        Strict lookup by .docId
        """
        matches = [d for d in self.docs if d.docId == doc_id]
        return self._unwrap(matches, f"docId={doc_id}")

    def by_identifier(self, identifier: str) -> Document:
        """
        Strict lookup by .identifier
        """
        matches = [d for d in self.docs if d.identifier == identifier]
        return self._unwrap(matches, f"identifier={identifier}")

    def by_title(self, title_substr: str) -> Document:
        """
        Strict lookup on title containing substring (case-insensitive)
        """
        matches = [d for d in self.docs if title_substr.lower() in d.title.lower()]
        return self._unwrap(matches, f"title contains '{title_substr}'")
    
    def by_breadcrumbs(self, breadcrumbs: List[str]) -> Document:
        """
        Return document whose .breadcrumbs exactly match the provided list.
        """
        matches = [doc for doc in self.docs if doc.metadata.breadcrumbs == breadcrumbs]
        return self._unwrap(matches, f"breadcrumbs='{breadcrumbs}'")

@define
class Library:
    docs: DocumentList
    _organizer: Optional['BaseOrganizer'] = field(default=None, alias='organizer')

    def __attrs_post_init__(self):
        if isinstance(self.docs, list):
            self.docs = DocumentList(items=self.docs)
        if not isinstance(self.docs, DocumentList):
            raise ValueError(f'docs in library must be DocumentList, you passed {type(self.docs)}')

    @cached_property
    def search(self) -> DocumentSearchEngine:
        # weight title more heavily than body, include metadata lightly
        weights = {'title': 2.0, 'markdown': 1.0, 'metadata': 0.3}
        engine = DocumentSearchEngine(
            field_weights=weights,
            stop_words="english",
            max_df=0.9,
        )
        engine.fit(self.docs)
        return engine

    @cached_property
    def organizer(self):
        return self._organizer(self.docs)

    @property
    def filter(self):
        return self.docs.filter

    @property
    def get(self):
        return self.docs.get

    @classmethod
    def load(cls, path: str):
        documents = DocumentList()
        base_path = Path(path)

        for file_path in base_path.glob("**/*.json"):
            try:
                with file_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    d = Document(**data)
                    documents.append(d)
            except (UnicodeDecodeError, json.JSONDecodeError, ValidationError) as e:
                logger.warning('failed to load file', file=str(file_path), error_type=type(e), error=e)

        return cls(docs=documents)
    
