import fitz  # PyMuPDF
from fastapi import UploadFile
import io

async def extract_text_from_pdf(upload_file: UploadFile) -> str:
    """Extracts text content from a PDF UploadFile."""
    try:
        content = await upload_file.read()
        pdf_document = fitz.open(stream=content, filetype="pdf")
        text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
        return text
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")
