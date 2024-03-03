from docx import Document
from abc import ABC, abstractmethod
import io


class ParserFactory:
    """
    Factory class to create parsers based on file extension.
    """

    def __init__(self, file_like_object, file_extension):
        """
        Initialize the ParserFactory with a file-like object and its extension.

        Args:
            file_like_object: The file-like object to be parsed.
            file_extension (str): The extension of the file to determine the parser type.
        """

        self.file_like_object = file_like_object
        self.file_extension = file_extension

    def build(self):
        """
        Build and return the appropriate parser based on the file extension.

        Returns:
            Parser: An instance of the appropriate parser based on the file extension.

        Raises:
            NotImplementedError: If the file extension is not supported.
        """

        if self.file_extension == "docx":
            return DocxParser(self.file_like_object)
        elif self.file_extension == "txt":
            return TxtParser(self.file_like_object)
        else:
            raise NotImplementedError


class Parser(ABC):
    """
    Abstract base class for file parsers.
    """

    def __init__(self, file_like_object):
        """
        Initialize the Parser with a file-like object.

        Args:
            file_like_object: The file-like object to be parsed.
        """
        self.file_like_object = file_like_object

    @abstractmethod
    def read(self):
        """
        Abstract method to read and parse the file content.
        """
        raise NotImplementedError


class DocxParser(Parser):
    """
    Parser class for .docx files.
    """

    def read(self):
        """
        Read and parse the content of a .docx file.

        Returns:
            str: The parsed text content of the .docx file.
        """
        file_stream = io.BytesIO(self.file_like_object)
        doc = Document(file_stream)
        text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
        return text


class TxtParser(Parser):
    """
    Parser class for .txt files.
    """

    def read(self):
        """
        Read and parse the content of a .txt file.

        Returns:
            str: The parsed text content of the .txt file.
        """
        return self.file_like_object.decode()
