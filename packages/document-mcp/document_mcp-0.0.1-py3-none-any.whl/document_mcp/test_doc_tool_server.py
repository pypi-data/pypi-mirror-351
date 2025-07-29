import pytest
from pathlib import Path
import os
import shutil
import datetime

# Make sure to import the necessary functions and models from doc_tool_server
# Using relative imports since this test is now inside the package
from .doc_tool_server import (
    _get_document_path, _get_chapter_path, _is_valid_chapter_filename,
    _split_into_paragraphs, _count_words, _get_ordered_chapter_files,
    _read_chapter_content_details, _get_chapter_metadata,
    # Import Pydantic Models
    OperationStatus, ChapterMetadata, DocumentInfo, ParagraphDetail,
    ChapterContent, FullDocumentContent, StatisticsReport,
    # Import Tools
    list_documents, create_document, delete_document,
    list_chapters, create_chapter, delete_chapter,
    read_chapter_content, write_chapter_content,
    read_paragraph_content, modify_paragraph_content, append_paragraph_to_chapter,
    replace_text_in_chapter, replace_text_in_document,
    read_full_document, # create_document is already imported
    get_chapter_statistics, get_document_statistics,
    find_text_in_chapter, find_text_in_document,
    # Import the global mcp_server and DOCS_ROOT_PATH for manipulation if needed,
    # but it's better to override the path for tests.
    DOCS_ROOT_PATH as SERVER_DEFAULT_DOCS_ROOT_PATH 
)
from . import doc_tool_server # Import the module itself to modify its global

# --- Pytest Fixtures ---

@pytest.fixture
def temp_docs_root(tmp_path: Path) -> Path:
    """Create a temporary directory for docs and override server path."""
    test_root = tmp_path / "test_documents_storage"
    test_root.mkdir()
    
    original_path = doc_tool_server.DOCS_ROOT_PATH
    doc_tool_server.DOCS_ROOT_PATH = test_root
    
    yield test_root

    # Cleanup: Remove all created documents and restore original state
    try:
        # Remove all documents created during tests
        if test_root.exists():
            for item in test_root.iterdir():
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                else:
                    item.unlink(missing_ok=True)
            # Remove the test directory itself
            shutil.rmtree(test_root, ignore_errors=True)
    except Exception as e:
        print(f"Warning: Could not fully clean up test directory: {e}")

    doc_tool_server.DOCS_ROOT_PATH = original_path

# --- Helper Functions for Tests ---

def _assert_operation_success(status: OperationStatus, expected_message_part: str = None):
    assert status.success is True
    if expected_message_part:
        assert expected_message_part.lower() in status.message.lower()

def _assert_operation_failure(status: OperationStatus, expected_message_part: str = None):
    assert status.success is False
    if expected_message_part:
        assert expected_message_part.lower() in status.message.lower(), f"Expected '{expected_message_part}' to be in '{status.message}'"

# --- Test Cases ---

# Test Document Management Tools
def test_create_document_success(temp_docs_root: Path):
    doc_name = "my_test_document"
    status = create_document(document_name=doc_name)
    _assert_operation_success(status, "created successfully")
    assert (temp_docs_root / doc_name).is_dir()
    assert status.details["document_name"] == doc_name

def test_create_document_duplicate(temp_docs_root: Path):
    doc_name = "my_duplicate_doc"
    create_document(document_name=doc_name) # Create first time
    status = create_document(document_name=doc_name) # Attempt duplicate
    _assert_operation_failure(status, "already exists")

def test_list_documents_empty(temp_docs_root: Path):
    docs_list = list_documents()
    assert isinstance(docs_list, list)
    assert len(docs_list) == 0

def test_list_documents_with_one_doc(temp_docs_root: Path):
    doc_name = "listed_document"
    create_document(document_name=doc_name)
    # Create a dummy chapter to ensure it has metadata
    (temp_docs_root / doc_name / "01-intro.md").write_text("# Hello")
    
    docs_list = list_documents()
    assert len(docs_list) == 1
    doc_info = docs_list[0]
    assert isinstance(doc_info, DocumentInfo)
    assert doc_info.document_name == doc_name
    assert doc_info.total_chapters == 1 # Because we added one chapter

def test_delete_document_success(temp_docs_root: Path):
    doc_name = "to_be_deleted_doc"
    create_document(document_name=doc_name)
    (temp_docs_root / doc_name / "file.md").write_text("content") # Add a file to it
    
    status = delete_document(document_name=doc_name)
    _assert_operation_success(status, "deleted successfully")
    assert not (temp_docs_root / doc_name).exists()

def test_delete_document_non_existent(temp_docs_root: Path):
    status = delete_document(document_name="non_existent_doc")
    _assert_operation_failure(status, "not found")

# Test Chapter Management Tools
def test_create_chapter_success(temp_docs_root: Path):
    doc_name = "doc_for_chapters"
    chapter_name = "01-my_chapter.md"
    initial_content = "# Chapter Title"
    create_document(document_name=doc_name)
    
    status = create_chapter(document_name=doc_name, chapter_name=chapter_name, initial_content=initial_content)
    _assert_operation_success(status, "created successfully")
    chapter_path = temp_docs_root / doc_name / chapter_name
    assert chapter_path.is_file()
    assert chapter_path.read_text() == initial_content
    assert status.details["document_name"] == doc_name
    assert status.details["chapter_name"] == chapter_name

def test_create_chapter_invalid_name(temp_docs_root: Path):
    doc_name = "doc_invalid_chapter_name"
    create_document(document_name=doc_name)
    status = create_chapter(document_name=doc_name, chapter_name="chapter_no_md", initial_content="")
    _assert_operation_failure(status, "invalid chapter name")
    
    status_manifest = create_chapter(document_name=doc_name, chapter_name="_manifest.json", initial_content="")
    _assert_operation_failure(status_manifest, "invalid chapter name")


def test_create_chapter_in_non_existent_document(temp_docs_root: Path):
    status = create_chapter(document_name="non_existent_doc_for_chapter", chapter_name="01-chap.md")
    _assert_operation_failure(status, "not found")

def test_create_chapter_duplicate(temp_docs_root: Path):
    doc_name = "doc_for_duplicate_chapter"
    chapter_name = "01-dupe.md"
    create_document(document_name=doc_name)
    create_chapter(document_name=doc_name, chapter_name=chapter_name) # First one
    status = create_chapter(document_name=doc_name, chapter_name=chapter_name) # Duplicate
    _assert_operation_failure(status, "already exists")

def test_list_chapters_empty(temp_docs_root: Path):
    doc_name = "doc_empty_chapters"
    create_document(document_name=doc_name)
    chapters_list = list_chapters(document_name=doc_name)
    assert isinstance(chapters_list, list)
    assert len(chapters_list) == 0

def test_list_chapters_non_existent_doc(temp_docs_root: Path):
    chapters_list = list_chapters(document_name="non_existent_doc_for_list_chapters")
    assert chapters_list is None

def test_list_chapters_with_multiple_chapters(temp_docs_root: Path):
    doc_name = "doc_with_chapters"
    create_document(document_name=doc_name)
    ch1_name = "01-first.md"
    ch2_name = "02-second.md"
    ch3_name = "00-zeroth.md" # To test ordering
    
    (temp_docs_root / doc_name / ch1_name).write_text("Content 1")
    (temp_docs_root / doc_name / ch2_name).write_text("Content 2")
    (temp_docs_root / doc_name / ch3_name).write_text("Content 0")
    # Add a non-md file, should be ignored
    (temp_docs_root / doc_name / "notes.txt").write_text("ignore this")


    chapters_list = list_chapters(document_name=doc_name)
    assert len(chapters_list) == 3
    assert isinstance(chapters_list[0], ChapterMetadata)
    assert chapters_list[0].chapter_name == ch3_name # "00-zeroth.md"
    assert chapters_list[1].chapter_name == ch1_name # "01-first.md"
    assert chapters_list[2].chapter_name == ch2_name # "02-second.md"
    
    # Check some metadata
    assert chapters_list[0].word_count == 2 # "Content 0"
    assert chapters_list[0].paragraph_count == 1


def test_delete_chapter_success(temp_docs_root: Path):
    doc_name = "doc_for_deleting_chapter"
    chapter_name = "ch_to_delete.md"
    create_document(document_name=doc_name)
    create_chapter(document_name=doc_name, chapter_name=chapter_name)
    assert (temp_docs_root / doc_name / chapter_name).exists()
    
    status = delete_chapter(document_name=doc_name, chapter_name=chapter_name)
    _assert_operation_success(status, "deleted successfully")
    assert not (temp_docs_root / doc_name / chapter_name).exists()

def test_delete_chapter_non_existent(temp_docs_root: Path):
    doc_name = "doc_for_deleting_non_existent_chapter"
    create_document(document_name=doc_name)
    status = delete_chapter(document_name=doc_name, chapter_name="ghost_chapter.md")
    _assert_operation_failure(status, "not found")

def test_delete_chapter_invalid_name(temp_docs_root: Path):
    doc_name = "doc_delete_invalid_chapter"
    create_document(document_name=doc_name)
    status = delete_chapter(document_name=doc_name, chapter_name="not_a_md_file.txt")
    _assert_operation_failure(status, "not a valid chapter")

# --- Test Read/Write Content Tools ---

def test_read_chapter_content_success(temp_docs_root: Path):
    doc_name = "doc_read_content"
    chapter_name = "readable_chapter.md"
    content = "# Title\nHello World\n\nThis is a paragraph."
    create_document(document_name=doc_name)
    (temp_docs_root / doc_name / chapter_name).write_text(content)

    chapter_obj = read_chapter_content(document_name=doc_name, chapter_name=chapter_name)
    assert chapter_obj is not None
    assert isinstance(chapter_obj, ChapterContent)
    assert chapter_obj.document_name == doc_name
    assert chapter_obj.chapter_name == chapter_name
    assert chapter_obj.content == content
    assert chapter_obj.word_count == 8 # Adjusted: "# Title Hello World This is a paragraph." (was 7)
    assert chapter_obj.paragraph_count == 2 # "# Title\nHello World" and "This is a paragraph."

def test_read_chapter_content_non_existent_chapter(temp_docs_root: Path):
    doc_name = "doc_read_non_existent_chap"
    create_document(document_name=doc_name)
    chapter_obj = read_chapter_content(document_name=doc_name, chapter_name="no_such_chapter.md")
    assert chapter_obj is None

def test_write_chapter_content_overwrite(temp_docs_root: Path):
    doc_name = "doc_write_content"
    chapter_name = "writable_chapter.md"
    initial_content = "Old content."
    new_content = "# New Content\nThis is fresh."
    create_document(document_name=doc_name)
    (temp_docs_root / doc_name / chapter_name).write_text(initial_content)

    status = write_chapter_content(document_name=doc_name, chapter_name=chapter_name, new_content=new_content)
    _assert_operation_success(status, "overwritten successfully")
    assert (temp_docs_root / doc_name / chapter_name).read_text() == new_content
    assert status.details["content"] == new_content

def test_write_chapter_content_create_new(temp_docs_root: Path):
    doc_name = "doc_write_new_chap"
    chapter_name = "newly_written_chapter.md"
    new_content = "Content for a new chapter."
    create_document(document_name=doc_name)

    status = write_chapter_content(document_name=doc_name, chapter_name=chapter_name, new_content=new_content)
    _assert_operation_success(status, "overwritten successfully") # Message might be generic
    assert (temp_docs_root / doc_name / chapter_name).read_text() == new_content

def test_read_paragraph_content_success(temp_docs_root: Path):
    doc_name = "doc_read_para"
    chapter_name = "chapter_with_paras.md"
    paras = ["Paragraph 0.", "Paragraph 1.", "Paragraph 2."]
    content = "\n\n".join(paras)
    create_document(document_name=doc_name)
    (temp_docs_root / doc_name / chapter_name).write_text(content)

    para_obj = read_paragraph_content(document_name=doc_name, chapter_name=chapter_name, paragraph_index_in_chapter=1)
    assert para_obj is not None
    assert isinstance(para_obj, ParagraphDetail)
    assert para_obj.content == "Paragraph 1."
    assert para_obj.paragraph_index_in_chapter == 1
    assert para_obj.word_count == 2

def test_read_paragraph_content_out_of_bounds(temp_docs_root: Path):
    doc_name = "doc_read_para_oob"
    chapter_name = "chapter_few_paras.md"
    content = "Para1\n\nPara2"
    create_document(document_name=doc_name)
    (temp_docs_root / doc_name / chapter_name).write_text(content)

    para_obj = read_paragraph_content(document_name=doc_name, chapter_name=chapter_name, paragraph_index_in_chapter=5)
    assert para_obj is None

CONTENT_FOR_MODIFY_PARA = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."

def test_modify_paragraph_content_replace(temp_docs_root: Path):
    doc_name = "doc_mod_para_replace"
    chapter_name = "chap_mod_replace.md"
    create_document(document_name=doc_name)
    (temp_docs_root / doc_name / chapter_name).write_text(CONTENT_FOR_MODIFY_PARA)

    status = modify_paragraph_content(doc_name, chapter_name, 1, "Replaced second paragraph.", "replace")
    _assert_operation_success(status)
    expected_content = "First paragraph.\n\nReplaced second paragraph.\n\nThird paragraph."
    assert (temp_docs_root / doc_name / chapter_name).read_text() == expected_content
    assert status.details["content"] == expected_content

def test_modify_paragraph_content_insert_before(temp_docs_root: Path):
    doc_name = "doc_mod_para_insert_before"
    chapter_name = "chap_mod_insert_b.md"
    create_document(document_name=doc_name)
    (temp_docs_root / doc_name / chapter_name).write_text(CONTENT_FOR_MODIFY_PARA)

    status = modify_paragraph_content(doc_name, chapter_name, 1, "Inserted before second.", "insert_before")
    _assert_operation_success(status)
    expected_content = "First paragraph.\n\nInserted before second.\n\nSecond paragraph.\n\nThird paragraph."
    assert (temp_docs_root / doc_name / chapter_name).read_text() == expected_content

def test_modify_paragraph_content_insert_after(temp_docs_root: Path):
    doc_name = "doc_mod_para_insert_after"
    chapter_name = "chap_mod_insert_a.md"
    create_document(document_name=doc_name)
    (temp_docs_root / doc_name / chapter_name).write_text(CONTENT_FOR_MODIFY_PARA)

    status = modify_paragraph_content(doc_name, chapter_name, 1, "Inserted after second.", "insert_after")
    _assert_operation_success(status)
    expected_content = "First paragraph.\n\nSecond paragraph.\n\nInserted after second.\n\nThird paragraph."
    assert (temp_docs_root / doc_name / chapter_name).read_text() == expected_content

def test_modify_paragraph_content_delete(temp_docs_root: Path):
    doc_name = "doc_mod_para_delete"
    chapter_name = "chap_mod_delete.md"
    create_document(document_name=doc_name)
    (temp_docs_root / doc_name / chapter_name).write_text(CONTENT_FOR_MODIFY_PARA)

    status = modify_paragraph_content(doc_name, chapter_name, 1, "", "delete") # content irrelevant for delete
    _assert_operation_success(status)
    expected_content = "First paragraph.\n\nThird paragraph."
    assert (temp_docs_root / doc_name / chapter_name).read_text() == expected_content

def test_modify_paragraph_content_invalid_mode(temp_docs_root: Path):
    doc_name = "doc_mod_para_invalid_mode"
    chapter_name = "chap_mod_invalid.md"
    create_document(document_name=doc_name)
    (temp_docs_root / doc_name / chapter_name).write_text("Some content.")
    status = modify_paragraph_content(doc_name, chapter_name, 0, "Content", "uppercut")
    _assert_operation_failure(status, "invalid mode")

def test_append_paragraph_to_chapter_success(temp_docs_root: Path):
    doc_name = "doc_append_para"
    chapter_name = "chap_append.md"
    initial_content = "First line.\n\nSecond line."
    appended_para = "Third line, appended."
    create_document(document_name=doc_name)
    (temp_docs_root / doc_name / chapter_name).write_text(initial_content)

    status = append_paragraph_to_chapter(doc_name, chapter_name, appended_para)
    _assert_operation_success(status)
    expected_content = initial_content + "\n\n" + appended_para
    assert (temp_docs_root / doc_name / chapter_name).read_text() == expected_content

def test_append_paragraph_to_empty_chapter(temp_docs_root: Path):
    doc_name = "doc_append_para_empty"
    chapter_name = "chap_append_empty.md"
    appended_para = "Only line."
    create_document(document_name=doc_name)
    (temp_docs_root / doc_name / chapter_name).write_text("") # Empty chapter

    status = append_paragraph_to_chapter(doc_name, chapter_name, appended_para)
    _assert_operation_success(status)
    assert (temp_docs_root / doc_name / chapter_name).read_text() == appended_para

def test_replace_text_in_chapter_success(temp_docs_root: Path):
    doc_name = "doc_replace_text_chap"
    chapter_name = "chap_replace.md"
    content = "Old text is old. Another old occurrence."
    create_document(document_name=doc_name)
    (temp_docs_root / doc_name / chapter_name).write_text(content)

    status = replace_text_in_chapter(doc_name, chapter_name, "old", "new")
    _assert_operation_success(status, "replaced")
    expected_content = "Old text is new. Another new occurrence."
    assert (temp_docs_root / doc_name / chapter_name).read_text() == expected_content
    assert status.details["content"] == expected_content # Check content in details

def test_replace_text_in_chapter_no_occurrence(temp_docs_root: Path):
    doc_name = "doc_replace_text_chap_no_op"
    chapter_name = "chap_replace_no_op.md"
    content = "Some text without the target."
    create_document(document_name=doc_name)
    (temp_docs_root / doc_name / chapter_name).write_text(content)

    status = replace_text_in_chapter(doc_name, chapter_name, "missing_text", "replacement")
    _assert_operation_success(status, "not found in chapter") # Success, but no change
    assert (temp_docs_root / doc_name / chapter_name).read_text() == content # Should be unchanged

# Test reading full document
def test_read_full_document_success(temp_docs_root: Path):
    doc_name = "full_doc_read"
    create_document(document_name=doc_name)
    ch1_content = "# Chapter 1\nContent of chapter one."
    ch2_content = "## Chapter 2\nSome more text here."
    (temp_docs_root / doc_name / "01_ch1.md").write_text(ch1_content)
    (temp_docs_root / doc_name / "02_ch2.md").write_text(ch2_content)

    full_doc_obj = read_full_document(document_name=doc_name)
    assert full_doc_obj is not None
    assert isinstance(full_doc_obj, FullDocumentContent)
    assert full_doc_obj.document_name == doc_name
    assert len(full_doc_obj.chapters) == 2
    assert full_doc_obj.chapters[0].content == ch1_content
    assert full_doc_obj.chapters[1].content == ch2_content
    assert full_doc_obj.total_word_count == 14 # Corrected: ch1 (7) + ch2 (7)
    assert full_doc_obj.total_paragraph_count == 2 # "# Chapter 1\nContent of chapter one." is 1 para. "## Chapter 2\nSome more text here." is 1 para.

def test_read_full_document_empty_doc(temp_docs_root: Path):
    doc_name = "empty_doc_for_full_read"
    create_document(document_name=doc_name)
    full_doc_obj = read_full_document(document_name=doc_name)
    assert full_doc_obj is not None
    assert len(full_doc_obj.chapters) == 0
    assert full_doc_obj.total_word_count == 0

def test_read_full_document_non_existent(temp_docs_root: Path):
    full_doc_obj = read_full_document(document_name="no_doc_here_for_full_read")
    assert full_doc_obj is None

# Test replacing text across document
def test_replace_text_in_document_success(temp_docs_root: Path):
    doc_name = "doc_replace_global"
    create_document(document_name=doc_name)
    ch1_content = "Global old term, chapter 1. Another old one."
    ch2_content = "Chapter 2, no target. But old is here!"
    ch3_content = "Only fresh new terms."
    (temp_docs_root / doc_name / "01_ch1.md").write_text(ch1_content)
    (temp_docs_root / doc_name / "02_ch2.md").write_text(ch2_content)
    (temp_docs_root / doc_name / "03_ch3.md").write_text(ch3_content)

    status = replace_text_in_document(doc_name, "old", "new")
    _assert_operation_success(status, "replacement completed")
    assert status.details["chapters_modified_count"] == 2
    assert status.details["total_occurrences_replaced"] == 3 # 2 in ch1, 1 in ch2

    assert (temp_docs_root / doc_name / "01_ch1.md").read_text() == "Global new term, chapter 1. Another new one."
    assert (temp_docs_root / doc_name / "02_ch2.md").read_text() == "Chapter 2, no target. But new is here!"
    assert (temp_docs_root / doc_name / "03_ch3.md").read_text() == ch3_content # Unchanged

# --- Test Analyze and Retrieval Tools ---

def test_get_chapter_statistics_success(temp_docs_root: Path):
    doc_name = "doc_stats_chap"
    chapter_name = "chap_for_stats.md"
    content = "# Stats Test\nThis chapter has five words.\n\nAnd two paragraphs total."
    create_document(document_name=doc_name)
    (temp_docs_root / doc_name / chapter_name).write_text(content)

    stats = get_chapter_statistics(document_name=doc_name, chapter_name=chapter_name)
    assert stats is not None
    assert isinstance(stats, StatisticsReport)
    assert stats.scope == f"chapter: {doc_name}/{chapter_name}"
    # Content: "# Stats Test\nThis chapter has five words.\n\nAnd two paragraphs total."
    # "#", "Stats", "Test", "This", "chapter", "has", "five", "words", "And", "two", "paragraphs", "total" = 12 words
    assert stats.word_count == 12 # Adjusted (was 11)
    assert stats.paragraph_count == 2 # Correct: "# Stats Test\nThis chapter has five words." AND "And two paragraphs total."

def test_get_chapter_statistics_non_existent(temp_docs_root: Path):
    doc_name = "doc_stats_chap_ne"
    create_document(document_name=doc_name)
    stats = get_chapter_statistics(document_name=doc_name, chapter_name="no_chap.md")
    assert stats is None

def test_get_document_statistics_success(temp_docs_root: Path):
    doc_name = "doc_stats_full"
    create_document(document_name=doc_name)
    (temp_docs_root / doc_name / "01.md").write_text("Chapter one has four words.") # 5 words
    (temp_docs_root / doc_name / "02.md").write_text("Chapter two has four words too.") # 6 words
    (temp_docs_root / doc_name / "03_non_md.txt").write_text("Ignore me.")

    stats = get_document_statistics(document_name=doc_name)
    assert stats is not None
    assert isinstance(stats, StatisticsReport)
    assert stats.scope == f"document: {doc_name}"
    assert stats.chapter_count == 2
    assert stats.word_count == (5 + 6)
    assert stats.paragraph_count == (1 + 1)

def test_get_document_statistics_empty_doc(temp_docs_root: Path):
    doc_name = "doc_stats_empty"
    create_document(document_name=doc_name)
    stats = get_document_statistics(document_name=doc_name)
    assert stats is not None
    assert stats.chapter_count == 0
    assert stats.word_count == 0
    assert stats.paragraph_count == 0

def test_get_document_statistics_non_existent_doc(temp_docs_root: Path):
    stats = get_document_statistics(document_name="doc_does_not_exist_for_stats")
    assert stats is None

def test_find_text_in_chapter_success_case_insensitive(temp_docs_root: Path):
    doc_name = "doc_find_chap_ci"
    chapter_name = "find_chap_ci.md"
    # Simplified content to avoid complex string issues with linter
    content = 'First paragraph with Target.\n\nSecond one has target too.\n\nNo match here.'
    create_document(document_name=doc_name)
    (temp_docs_root / doc_name / chapter_name).write_text(content)

    results = find_text_in_chapter(doc_name, chapter_name, "target", case_sensitive=False)
    assert len(results) == 2
    assert isinstance(results[0], ParagraphDetail)
    assert results[0].paragraph_index_in_chapter == 0
    assert "Target" in results[0].content
    assert results[1].paragraph_index_in_chapter == 1
    assert "target" in results[1].content

def test_find_text_in_chapter_success_case_sensitive(temp_docs_root: Path):
    doc_name = "doc_find_chap_cs"
    chapter_name = "find_chap_cs.md"
    content = 'First paragraph with Target.\n\nSecond one has target (lowercase).\n\nNo match for Target here.'
    create_document(document_name=doc_name)
    (temp_docs_root / doc_name / chapter_name).write_text(content)

    results = find_text_in_chapter(doc_name, chapter_name, "Target", case_sensitive=True)
    assert len(results) == 2 # Corrected: "Target" is in para 0 and para 2
    assert results[0].paragraph_index_in_chapter == 0
    assert "Target" in results[0].content 
    assert results[1].paragraph_index_in_chapter == 2 # Check second occurrence details
    assert "Target" in results[1].content

def test_find_text_in_chapter_no_match(temp_docs_root: Path):
    doc_name = "doc_find_chap_none"
    chapter_name = "find_chap_none.md"
    content = 'Nothing to find here.'
    create_document(document_name=doc_name)
    (temp_docs_root / doc_name / chapter_name).write_text(content)
    results = find_text_in_chapter(doc_name, chapter_name, "missing")
    assert len(results) == 0

def test_find_text_in_document_success(temp_docs_root: Path):
    doc_name = "doc_find_global_text"
    create_document(document_name=doc_name)
    # Simplified content
    (temp_docs_root / doc_name / "01_ch_a.md").write_text('Unique keyword in chapter A.\nAnother line.')
    (temp_docs_root / doc_name / "02_ch_b.md").write_text('Chapter B is here.\n\nAlso has unique keyword.')
    (temp_docs_root / doc_name / "03_ch_c.md").write_text('Chapter C, no keyword.')

    results = find_text_in_document(doc_name, "unique keyword", case_sensitive=False)
    assert len(results) == 2
    # Check basic presence, detailed content check can be tricky if original formatting is lost
    found_in_a = any(res.chapter_name == "01_ch_a.md" and "keyword in chapter A".lower() in res.content.lower() for res in results)
    found_in_b = any(res.chapter_name == "02_ch_b.md" and "unique keyword".lower() in res.content.lower() for res in results)
    assert found_in_a
    assert found_in_b

def test_find_text_in_document_no_match(temp_docs_root: Path):
    doc_name = "doc_find_global_none"
    create_document(document_name=doc_name)
    (temp_docs_root / doc_name / "any_chap.md").write_text('Content without search term.')
    results = find_text_in_document(doc_name, "super_secret_text")
    assert len(results) == 0

# Cleanup function to ensure all test artifacts are removed
def pytest_sessionfinish(session, exitstatus):
    """Clean up any remaining test artifacts after all tests complete."""
    try:
        # Ensure doc_tool_server path is restored to default
        if hasattr(doc_tool_server, 'DOCS_ROOT_PATH'):
            default_path = Path.cwd() / "documents_storage"
            doc_tool_server.DOCS_ROOT_PATH = default_path
            
    except Exception as e:
        print(f"Warning: Could not fully clean up after tests: {e}")

# Will be added incrementally (This comment can be removed if all tests are done for this file) 