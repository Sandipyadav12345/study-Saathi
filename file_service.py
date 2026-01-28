import os
import pypdf
import docx

def read_file_content(file_path: str) -> str:
    """
    Reads content from a PDF or DOCX file.
    Returns the extracted text.
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    if ext == ".pdf":
        return _read_pdf(file_path)
    elif ext == ".docx":
        return _read_docx(file_path)
    elif ext == ".txt":
        return _read_txt(file_path)
    elif ext in [".jpg", ".jpeg", ".png"]:
        return _read_image(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

def _read_image(file_path: str) -> str:
    """Read text from image using OCR"""
    try:
        from PIL import Image
        import pytesseract
        
        # Point to Tesseract if needed (Windows often needs this)
        # Assuming standard install path or PATH is set
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        text = pytesseract.image_to_string(Image.open(file_path))
        return text if text.strip() else "OCR extracted no text."
    except ImportError:
        return "[Error] Python libraries 'Pillow' or 'pytesseract' not installed. Cannot read images."
    except Exception as e:
        print(f"Error reading Image: {e}")
        return f"[Error] OCR Failed. Ensure Tesseract is installed and in your PATH. (Details: {str(e)})"


def _read_pdf(file_path: str) -> str:
    text = ""
    try:
        reader = pypdf.PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""
    return text

def _read_docx(file_path: str) -> str:
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return ""
    return text

def _read_txt(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading TXT: {e}")
        return ""
