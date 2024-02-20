from docx import Document
from abc import ABC, abstractmethod


class ParserFactory:
    def __init__(self, file_like_object, file_extension):
        self.file_like_object = file_like_object
        self.file_extension = file_extension

    def build(self):
        if self.file_extension == "docx":
            return DocxParser(self.file_like_object)
        elif self.file_extension == "txt":
            return TxtParser(self.file_like_object)
        else:
            raise NotImplementedError


class Parser(ABC):
    def __init__(self, file_like_object):
        self.file_like_object = file_like_object

    @abstractmethod
    def read(self):
        raise NotImplementedError


class DocxParser(Parser):
    def read(self):
        doc = Document(self.file_like_object)

        # Initialize an empty list to store the text
        text = []
        page_text = []

        # Iterate over paragraphs in the document
        for paragraph in doc.paragraphs:
            page_text.append(paragraph.text)

            # Check if a new page begins (based on section information)
            if paragraph._element.tag.endswith("sectPr"):
                text.append(f"Page {page_num}:\n{' '.join(page_text)}")
                page_text = []

        # Append the last page
        if page_text:
            text.append(f"Page {page_num}:\n{' '.join(page_text)}")

        # Join the list of text into a single string
        parsed_text = "\n\n".join(text)

        return parsed_text

class TxtParser(Parser):
    def read(self):
        return self.file_like_object.decode()