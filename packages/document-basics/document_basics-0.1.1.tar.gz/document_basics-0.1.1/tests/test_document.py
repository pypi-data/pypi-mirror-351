import json
from pathlib import Path
import uuid
from datetime import datetime
import pytest

from pydantic import AnyUrl, ValidationError
from doc_analytics.utils import to_valid_filename, cast
from doc_analytics.document import Metadata, NotYetPrompted, GeneratedContent, Document

def test_metadata_defaults_and_types():
    m = Metadata()
    assert m.breadcrumbs == []
    assert m.file_path is None
    assert m.url is None
    assert isinstance(m.date_crawled, datetime)
    assert m.crawled_by is None
    assert m.source is None
    assert isinstance(m.extra, dict)
    # default extra is an empty dict and is unique per instance
    m2 = Metadata()
    assert m.extra is not m2.extra

def test_metadata_url_validation():
    with pytest.raises(ValidationError):
        Metadata(url="not-a-valid-url")

def test_not_yet_prompted_is_empty_model():
    n = NotYetPrompted()
    # should have no fields
    assert n.model_dump() == {}

def test_generated_content_defaults():
    gc = GeneratedContent()
    assert isinstance(gc.keywords, NotYetPrompted)
    assert isinstance(gc.summary, NotYetPrompted)
    assert gc.extra == {}
    # can override with real values
    gc2 = GeneratedContent(
        keywords=["foo", "bar"],
        summary="A short summary",
        extra={"k": "v"}
    )
    assert gc2.keywords == ["foo", "bar"]
    assert gc2.summary == "A short summary"
    assert gc2.extra == {"k": "v"}

def test_document_defaults_and_identifier():
    doc = Document(title="Test Title", markdown="## hi")
    # identifier property
    assert doc.identifier == "Test Title"
    # docId is a uuid4 string
    uuid.UUID(doc.docId)  # will raise if not valid

def test_save_creates_file_and_sets_metadata(tmp_path):
    doc = Document(title="simple", markdown="content")
    # ensure title yields a safe filename
    filename = to_valid_filename(doc.identifier)
    target_dir = tmp_path / "out"
    target_dir.mkdir()
    result = doc.save(base_path=target_dir)
    assert result is True
    saved_file = target_dir / filename
    assert saved_file.exists()
    # metadata.file_path is set correctly
    assert doc.metadata.file_path == str(saved_file)
    # content is valid JSON with our markdown
    content = saved_file.read_text(encoding="utf-8")
    assert '"markdown": "content"' in content

def test_save_raises_if_exists_and_no_overwrite(tmp_path):
    doc = Document(title="dup", markdown="hello")
    filename = to_valid_filename(doc.identifier)
    target_dir = tmp_path
    file_path = target_dir / filename
    # pre-create file
    file_path.write_text("junk")
    with pytest.raises(ValueError) as exc:
        doc.save(base_path=target_dir, overwrite=False)
    assert "already exists" in str(exc.value)

def test_save_overwrites_if_exists_and_overwrite_true(tmp_path):
    doc = Document(title="dup2", markdown="first")
    filename = to_valid_filename(doc.identifier)
    target_dir = tmp_path
    file_path = target_dir / filename
    file_path.write_text("old")
    # should succeed and replace content
    result = doc.save(base_path=target_dir, overwrite=True)
    assert result is True
    new_content = file_path.read_text(encoding="utf-8")
    assert '"markdown": "first"' in new_content

def test_load_success(tmp_path):
    # Arrange: create and save a Document
    doc1 = Document(title="LoadTest", markdown="**bold**")

    # write it using save()
    doc1.save(base_path=tmp_path)
    dest = doc1.metadata.file_path

    # Act: load it back
    doc2 = Document.load(dest)

    # Assert: fields match
    assert isinstance(doc2, Document)
    assert doc2.title == doc1.title
    assert doc2.markdown == doc1.markdown
    # docId round-trips
    assert doc2.docId == doc1.docId
    # metadata was repopulated and file_path set
    assert isinstance(doc2.metadata, Metadata)
    assert doc2.metadata.file_path == Path(dest)

def test_load_nonexistent_raises(tmp_path):
    missing = tmp_path / "no_such_file.json"
    with pytest.raises(ValueError) as exc:
        Document.load(missing)
    assert "Could not load document" in str(exc.value)

def test_load_invalid_json_raises(tmp_path):
    # Arrange: create a file with invalid JSON
    bad = tmp_path / "bad.json"
    bad.write_text("not valid json", encoding="utf-8")

    with pytest.raises(ValueError) as exc:
        Document.load(bad)
    msg = str(exc.value)
    # ensure it's the JSON/parse branch
    assert "Invalid document JSON" in msg

def test_load_invalid_schema_raises(tmp_path):
    # Arrange: valid JSON but missing required fields (title/markdown)
    bad = tmp_path / "schema_fail.json"
    bad.write_text(json.dumps({"foo": "bar"}), encoding="utf-8")

    with pytest.raises(ValueError) as exc:
        Document.load(bad)
    msg = str(exc.value)
    # Pydantic validation on missing title/markdown should end up here
    assert "Invalid document JSON" in msg
