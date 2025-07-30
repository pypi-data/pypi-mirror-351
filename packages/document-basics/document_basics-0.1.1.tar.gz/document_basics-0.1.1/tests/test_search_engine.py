from doc_analytics.search import DocumentSearchEngine
from doc_analytics.document import Document, Metadata


def make_doc(
    title: str,
    markdown: str,
    breadcrumbs=None,
    source=None,
    crawled_by=None,
    extra=None
) -> Document:
    """
    Helper to create a Document with minimal metadata.
    """
    metadata = Metadata(
        breadcrumbs=breadcrumbs or [],
        source=source,
        crawled_by=crawled_by,
        extra=extra or {}
    )
    return Document(title=title, markdown=markdown, metadata=metadata)


def test_no_docs_returns_empty_list():
    engine = DocumentSearchEngine()
    results = engine("anything")
    assert results == []


def test_single_document_match():
    doc = make_doc("Hello", "world")
    engine = DocumentSearchEngine()
    engine.fit([doc])
    results = engine("world")
    assert len(results) == 1
    found_doc, score = results[0]
    assert found_doc is doc
    assert score > 0.0


def test_markdown_default_field_weighting():
    # Default only indexes markdown
    doc1 = make_doc("Title1", "apple banana cherry")
    doc2 = make_doc("Title2", "dog cat mouse")
    engine = DocumentSearchEngine()
    engine.fit([doc1, doc2])
    results = engine("cat")
    # Should find doc2 first because its markdown contains 'cat'
    assert results[0][0] is doc2


def test_field_weights_influence_order():
    # doc1 matches in title, doc2 matches in markdown
    doc1 = make_doc("apple", "banana")
    doc2 = make_doc("banana", "apple")

    # Using default (markdown only): apple -> doc2
    engine_default = DocumentSearchEngine()
    engine_default.fit([doc1, doc2])
    results_default = engine_default("apple")
    assert results_default[0][0] is doc2

    # Boost title: apple -> doc1
    engine_title_boost = DocumentSearchEngine(field_weights={"title": 2.0, "markdown": 1.0})
    engine_title_boost.fit([doc1, doc2])
    results_title_boost = engine_title_boost("apple")
    assert results_title_boost[0][0] is doc1


def test_top_k_limits_number_of_results():
    docs = [make_doc(str(i), str(i)) for i in ['apple', 'orange', 'cucumber', 'banana']]
    engine = DocumentSearchEngine()
    engine.fit(docs)
    top_3 = engine("apple", top_k=3)
    assert len(top_3) == 3
    # Best match for '2' should be the doc with markdown '2'
    assert top_3[0][0].markdown == "apple"


def test_zero_weight_fields_produce_zero_scores():
    doc1 = make_doc("apple", "apple")
    doc2 = make_doc("apple", "apple")
    engine = DocumentSearchEngine(field_weights={"markdown": 0.0})
    engine.fit([doc1, doc2])
    results = engine("apple")
    # All scores must be zero
    assert all(score == 0.0 for _, score in results)


def test_metadata_field_search():
    # Search within metadata.breadcrumbs and other metadata fields
    doc1 = make_doc("Doc1", "", breadcrumbs=["alpha", "beta"], source="srcA")
    doc2 = make_doc("Doc2", "", breadcrumbs=["gamma"], source="srcB")
    engine = DocumentSearchEngine(field_weights={"metadata": 1.0})
    engine.fit([doc1, doc2])
    results = engine("alpha")
    assert results[0][0] is doc1


def test_specific_metadata_attribute_field():
    # Index a specific metadata attribute (e.g., 'source')
    doc1 = make_doc("Doc1", "", source="news")
    doc2 = make_doc("Doc2", "", source="blog")
    engine = DocumentSearchEngine(field_weights={"source": 1.0})
    engine.fit([doc1, doc2])
    results = engine("blog")
    assert results[0][0] is doc2
