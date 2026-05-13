"""Tests for OCR helpers."""
from app.services.ocr import extract_text_from_file


def test_extract_text_from_plain_utf8():
    text = extract_text_from_file("note.txt", "text/plain", b"hello world")
    assert text == "hello world"


def test_extract_text_from_non_utf8_falls_back():
    text = extract_text_from_file("blob.bin", "application/octet-stream", b"\xff\xfeh\x00i\x00")
    assert text

