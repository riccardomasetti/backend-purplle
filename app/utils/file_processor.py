import os
from pypdf import PdfReader
import docx
# Correct imports for odfpy
from odf.opendocument import load
from odf.text import P
from odf.teletype import extractText


def extract_text_from_file(file_path):
    """
    Extract text content from various file formats

    Args:
        file_path (str): Path to the file

    Returns:
        str: Extracted text content
    """
    file_extension = os.path.splitext(file_path)[1].lower()

    try:
        # Text files
        if file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()

        # PDF files
        elif file_extension == '.pdf':
            text = ""
            pdf = PdfReader(file_path)
            for page in pdf.pages:
                text += page.extract_text() + "\n"
            return text

        # Word documents
        elif file_extension == '.docx':
            doc = docx.Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])

        # ODT files (OpenDocument Text)
        elif file_extension == '.odt':
            # Using odfpy directly with correct imports
            textdoc = load(file_path)
            paragraphs = textdoc.getElementsByType(P)
            return "\n".join([extractText(paragraph) for paragraph in paragraphs])

        else:
            return f"Unsupported file format: {file_extension}"

    except Exception as e:
        return f"Error extracting text from {file_path}: {str(e)}"