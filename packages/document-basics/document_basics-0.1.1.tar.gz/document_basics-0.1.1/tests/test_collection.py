import pytest
from datetime import datetime
import networkx as nx

from doc_analytics.collections import DocumentList, DocumentFilter, DocumentGetter, Library
from doc_analytics.doc_organizer import BreadcrumbOrganizer
from doc_analytics.document import Document, Metadata

@pytest.fixture
def docs():
    # Create a more complex hierarchy with two root trees and multiple levels
    doc_root = Document(
        title="Root",
        markdown="root markdown",
        metadata=Metadata(breadcrumbs=["Root"])
    )
    doc_childA = Document(
        title="ChildA",
        markdown="childA markdown",
        metadata=Metadata(breadcrumbs=["Root", "ChildA"])
    )
    doc_childB = Document(
        title="ChildB",
        markdown="childB markdown",
        metadata=Metadata(breadcrumbs=["Root", "ChildB"])
    )
    doc_grandA1 = Document(
        title="GrandA1",
        markdown="grandA1 markdown",
        metadata=Metadata(breadcrumbs=["Root", "ChildA", "GrandA1"])
    )
    doc_grandA2 = Document(
        title="GrandA2",
        markdown="grandA2 markdown",
        metadata=Metadata(breadcrumbs=["Root", "ChildA", "GrandA2"])
    )
    doc_greatGrandA1 = Document(
        title="GreatGrandA1",
        markdown="greatGrandA1 markdown",
        metadata=Metadata(breadcrumbs=["Root", "ChildA", "GrandA1", "GreatGrandA1"])
    )
    # Second root tree
    doc_otherRoot = Document(
        title="OtherRoot",
        markdown="otherRoot markdown",
        metadata=Metadata(breadcrumbs=["OtherRoot"])
    )
    doc_otherChild = Document(
        title="OtherChild",
        markdown="otherChild markdown",
        metadata=Metadata(breadcrumbs=["OtherRoot", "OtherChild"])
    )
    return [
        doc_root,
        doc_childA,
        doc_childB,
        doc_grandA1,
        doc_grandA2,
        doc_greatGrandA1,
        doc_otherRoot,
        doc_otherChild,
    ]

@pytest.fixture
def doc_list(docs):
    return DocumentList(items=docs)

def test_document_list_basics(doc_list, docs):
    # Length, iteration, indexing, and slicing
    assert len(doc_list) == 8
    assert [d.title for d in doc_list] == [
        "Root",
        "ChildA",
        "ChildB",
        "GrandA1",
        "GrandA2",
        "GreatGrandA1",
        "OtherRoot",
        "OtherChild",
    ]
    assert doc_list[0].title == "Root"
    sliced = doc_list[1:4]
    assert isinstance(sliced, DocumentList)
    assert len(sliced) == 3

    # __add__ with another DocumentList or list
    combined = doc_list + docs[:2]
    assert isinstance(combined, DocumentList)
    assert len(combined) == 10

def test_docIds_titles_markdowns(doc_list):
    # .docIds, .titles, .markdowns
    assert isinstance(doc_list.docIds, list)
    assert isinstance(doc_list.titles, list)
    assert isinstance(doc_list.markdowns, list)
    assert doc_list.titles == [
        "Root",
        "ChildA",
        "ChildB",
        "GrandA1",
        "GrandA2",
        "GreatGrandA1",
        "OtherRoot",
        "OtherChild",
    ]
    assert doc_list.markdowns == [
        "root markdown",
        "childA markdown",
        "childB markdown",
        "grandA1 markdown",
        "grandA2 markdown",
        "greatGrandA1 markdown",
        "otherRoot markdown",
        "otherChild markdown",
    ]

def test_gather(doc_list):
    # Should gather metadata attributes across all docs
    breadcrumbs = doc_list.gather("breadcrumbs")
    expected = [
        ["Root"],
        ["Root", "ChildA"],
        ["Root", "ChildB"],
        ["Root", "ChildA", "GrandA1"],
        ["Root", "ChildA", "GrandA2"],
        ["Root", "ChildA", "GrandA1", "GreatGrandA1"],
        ["OtherRoot"],
        ["OtherRoot", "OtherChild"],
    ]
    assert breadcrumbs == expected

def test_filter_by_ids(doc_list):
    flt_single = doc_list.filter.by_ids(doc_list.items[2].docId)
    assert isinstance(flt_single, type(doc_list.items[2]))
    assert flt_single.title == "ChildB"

    flt_multiple = doc_list.filter.by_ids(
        doc_list.items[1].docId,
        doc_list.items[3].docId
    )
    assert isinstance(flt_multiple, DocumentList)
    assert {d.title for d in flt_multiple} == {"ChildA", "GrandA1"}

    assert doc_list.filter.by_ids("nonexistent") is None

def test_filter_by_identifier_and_identifiers(doc_list):
    # by_identifier returns a single Document or None
    d = doc_list.filter.by_identifier("GrandA2")
    assert isinstance(d, Document)
    assert d.title == "GrandA2"
    assert doc_list.filter.by_identifier("Nope") is None

    # by_identifiers returns a DocumentList
    multi = doc_list.filter.by_identifiers("Root", "OtherChild")
    assert isinstance(multi, DocumentList)
    assert {d.title for d in multi} == {"Root", "OtherChild"}

def test_filter_by_keyword_and_title(doc_list):
    # Keyword search on markdown
    flt = doc_list.filter.by_keyword("grand")
    assert isinstance(flt, DocumentList)
    assert {d.title for d in flt} == {"GrandA1", "GrandA2", "GreatGrandA1"}

    # Case-insensitive title search
    flt_title = doc_list.filter.by_title("other")
    assert isinstance(flt_title, DocumentList)
    assert {d.title for d in flt_title} == {"OtherRoot", "OtherChild"}

def test_filter_by_breadcrumbs(doc_list):
    flt = doc_list.filter.by_breadcrumbs(["Root", "ChildA"])
    assert isinstance(flt, DocumentList)
    assert [d.title for d in flt] == ["ChildA"]
    flt_other = doc_list.filter.by_breadcrumbs(["OtherRoot"])
    assert [d.title for d in flt_other] == ["OtherRoot"]

def test_getter_by_id_and_identifier(doc_list):
    getter = doc_list.get
    # by_id
    g1 = getter.by_id(doc_list.items[3].docId)
    assert g1.title == "GrandA1"
    with pytest.raises(ValueError):
        getter.by_id("nonexistent")

    # by_identifier
    g2 = getter.by_identifier("ChildA")
    assert g2.title == "ChildA"
    with pytest.raises(ValueError):
        getter.by_identifier("Nope")

def test_getter_by_title_and_breadcrumbs(doc_list):
    getter = doc_list.get
    # by_title
    g = getter.by_title("ChildB")
    assert g.title == "ChildB"
    with pytest.raises(ValueError):
        getter.by_title("Nope")

    # by_breadcrumbs
    g_b = getter.by_breadcrumbs(["Root"])
    assert g_b.title == "Root"
    with pytest.raises(ValueError):
        getter.by_breadcrumbs(["Nope"])

