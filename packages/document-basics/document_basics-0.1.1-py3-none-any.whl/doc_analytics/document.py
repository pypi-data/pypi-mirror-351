from structlog import get_logger

logger = get_logger()

import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from pydantic import AnyUrl, BaseModel, Field, FilePath

from doc_analytics.utils import cast, to_valid_filename


class Metadata(BaseModel):
    breadcrumbs: Optional[List[str]] = Field(default_factory=list)
    file_path: Optional[FilePath] = None
    url: Optional[AnyUrl] = None
    date_crawled: datetime = Field(default_factory=datetime.now)
    crawled_by: Optional[str] = None
    source: Optional[str] = None  # e.g., 'web', 'filesystem', 'api'
    extra: dict = Field(default_factory=dict)  # any additional metadata


class NotYetPrompted(BaseModel):
    pass


class GeneratedContent(BaseModel):
    keywords: List[str] | NotYetPrompted = Field(default_factory=NotYetPrompted)
    summary: str | NotYetPrompted = Field(default_factory=NotYetPrompted)
    extra: dict[str, str] = Field(default_factory=dict)


class Document(BaseModel):
    docId: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    markdown: str
    metadata: Metadata = Field(default_factory=Metadata)
    parent: Optional["Document"] = Field(
        default=None,
        init=False,
        repr=False,
        exclude=True,
        description="This attribute is set by the library, if the doc is used in a collection / hierarchy",
    )

    @property
    def identifier(self) -> str:
        return self.title

    def save(self, base_path: str | Path, overwrite=False):

        if not self.metadata.file_path:

            base_path = cast(base_path, Path)
            filename = to_valid_filename(self.identifier)
            file_path = base_path / filename

            if file_path.exists() and not overwrite:
                raise ValueError(
                    f"File path {file_path} already exists. Set overwrite=True to overwrite."
                )

            self.metadata.file_path = str(file_path)


        try:
            with open(base_path / filename, "w", encoding="utf-8") as f:
                f.write(self.model_dump_json(indent=2))
            return True
        except OSError as e:
            self.metadata.file_path = None
            logger.warning(
                "Could not save document", docId=self.docId, title=self.title
            )
            return False

    @classmethod
    def load(cls, file_path: str | Path) -> "Document":
        """
        Load a Document from a JSON file on disk.

        - file_path: path to the JSON file previously written by .save()
        - Returns: a Document instance with metadata.file_path set.
        - Raises ValueError on I/O or parse errors.
        """
        # coerce to Path
        file_path = cast(file_path, Path)

        try:
            # read the raw JSON
            raw = file_path.read_text(encoding="utf-8")
            # parse into a Document
            doc = cls.model_validate_json(raw)
            # update metadata to reflect where it came from
            # doc.metadata.file_path = file_path
            return doc

        except OSError as e:
            logger.warning(
                "Could not load document", file_path=str(file_path), error=str(e)
            )
            raise ValueError(f"Could not load document from {file_path}: {e}") from e

        except Exception as e:
            # e.g. JSON parse / validation errors
            logger.warning(
                "Failed to parse document JSON",
                file_path=str(file_path),
                error=str(e),
            )
            raise ValueError(f"Invalid document JSON in {file_path}: {e}") from e

