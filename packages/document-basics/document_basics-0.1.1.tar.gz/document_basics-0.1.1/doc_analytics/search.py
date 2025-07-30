from typing import List, Tuple, Dict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import numpy as np

from doc_analytics.document import Document  # adjust import to your project structure


class DocumentSearchEngine:
    def __init__(
        self,
        field_weights: Dict[str, float] = None,
        **vectorizer_kwargs
    ):
        """
        A search engine that weights different Document fields.

        field_weights: mapping of field names to weights, e.g.
            {'title': 2.0, 'markdown': 1.0, 'metadata': 0.5}
        vectorizer_kwargs: passed to every TfidfVectorizer
        """
        # Default to indexing only the markdown body
        self.field_weights = field_weights or {'markdown': 1.0}
        self.vectorizer_kwargs = vectorizer_kwargs
        self.docs: List[Document] = []
        self.vectorizers: Dict[str, TfidfVectorizer] = {}
        self.matrices: Dict[str, any] = {}

    def _get_field_text(self, doc: Document, field: str) -> str:
        """
        Extracts text for the given field from a Document.
        Supported fields: 'markdown', 'title', 'metadata', or any metadata attr.
        """
        if field == 'markdown':
            return doc.markdown or ''
        if field == 'title':
            return doc.title or ''
        if field == 'metadata':
            meta = doc.metadata
            parts: List[str] = []
            parts.extend(meta.breadcrumbs or [])
            if meta.source:
                parts.append(meta.source)
            if meta.crawled_by:
                parts.append(meta.crawled_by)
            parts.extend(str(v) for v in meta.extra.values())
            return ' '.join(parts)
        # fallback: individual metadata attribute
        val = getattr(doc.metadata, field, None)
        if isinstance(val, str):
            return val
        if isinstance(val, list):
            return ' '.join(val)
        return ''

    def fit(self, docs: List[Document]) -> None:
        """
        Indexes all provided documents across configured fields.

        docs: list of Document instances
        """
        self.docs = docs
        n = len(docs)
        for field, weight in self.field_weights.items():
            corpus = [self._get_field_text(doc, field) for doc in docs]
            vec = TfidfVectorizer(**self.vectorizer_kwargs)
            mat = vec.fit_transform(corpus)
            self.vectorizers[field] = vec
            self.matrices[field] = mat

    def __call__(self, query: str, top_k: int = 10) -> List[Tuple[Document, float]]:
        """
        Returns the top_k Documents most similar to `query`, scoring each field
        by its configured weight. Higher weight => stronger influence.

        Score is the weighted sum of cosine similarities across fields.
        """
        if not self.docs:
            return []
        n = len(self.docs)
        total_sims = np.zeros(n)
        for field, weight in self.field_weights.items():
            vec = self.vectorizers.get(field)
            mat = self.matrices.get(field)
            if vec is None or weight == 0:
                continue
            q_vec = vec.transform([query])
            sims = linear_kernel(q_vec, mat).flatten()
            total_sims += weight * sims

        # rank documents by descending score
        top_idxs = np.argsort(total_sims)[::-1][:top_k]
        return [(self.docs[i], float(total_sims[i])) for i in top_idxs]
