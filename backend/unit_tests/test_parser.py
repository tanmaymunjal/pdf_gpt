import unittest
from io import BytesIO
from backend.parser import ParserFactory, DocxParser, TxtParser


def open_file_binary_str(file_path: str):
    with open(file_path, "rb") as file:
        byte_content = file.read()
    return byte_content


class TestParserFactory(unittest.TestCase):
    def test_build_docx_parser(self):
        file_like_object = BytesIO(b"")
        file_extension = "docx"
        factory = ParserFactory(file_like_object, file_extension)
        parser = factory.build()
        self.assertIsInstance(parser, DocxParser)

    def test_build_txt_parser(self):
        file_like_object = BytesIO(b"")
        file_extension = "txt"
        factory = ParserFactory(file_like_object, file_extension)
        parser = factory.build()
        self.assertIsInstance(parser, TxtParser)

    def test_build_unsupported_extension(self):
        file_like_object = BytesIO(b"")
        file_extension = "pdf"
        factory = ParserFactory(file_like_object, file_extension)
        with self.assertRaises(NotImplementedError):
            parser = factory.build()


class TestTxtParser(unittest.TestCase):
    def test_parse_txt(self):
        file_like_object = open_file_binary_str("unit_tests/test.txt")
        file_extension = "txt"
        factory = ParserFactory(file_like_object, file_extension)
        parser = factory.build()
        text = parser.read().strip()
        assert text == "Hey"


class TestDocxParser(unittest.TestCase):
    def test_parse_docx(self):
        file_like_object = open_file_binary_str("unit_tests/test.docx")
        file_extension = "docx"
        factory = ParserFactory(file_like_object, file_extension)
        parser = factory.build()
        text = parser.read().strip()
        assert text == "Hello"
