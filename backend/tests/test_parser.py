import unittest
from io import BytesIO
from backend.parser import ParserFactory, DocxParser, TxtParser


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


# class TestDocxParser(unittest.TestCase):
#     def test_read_docx(self):
#         # Mock a .docx file-like object
#         file_like_object = BytesIO(b"Mock .docx file content")

#         # Create a DocxParser instance
#         parser = DocxParser(file_like_object)

#         # Read and parse the content
#         parsed_content = parser.read()

#         # Assert the parsed content matches the expected result
#         self.assertEqual(parsed_content, "Mock .docx file content")


# class TestTxtParser(unittest.TestCase):
#     def test_read_txt(self):
#         # Mock a .txt file-like object
#         file_like_object = BytesIO(b"Mock .txt file content")

#         # Create a TxtParser instance
#         parser = TxtParser(file_like_object)

#         # Read and parse the content
#         parsed_content = parser.read()

#         # Assert the parsed content matches the expected result
#         self.assertEqual(parsed_content, "Mock .txt file content")
