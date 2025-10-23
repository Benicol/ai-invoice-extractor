from pdf2image import convert_from_path, pdfinfo_from_path
import os, io

from pdf2image.exceptions import PDFInfoNotInstalledError


class Ticket:
    _pdf_path: str

    def __init__(self, pdf_path):
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"File {pdf_path} does not exist")
        if pdfinfo_from_path(pdf_path)['Pages'] > 1:
            raise ValueError("PDF has more than one page")
        self._pdf_path = pdf_path


    @property
    def pdf_path(self) -> str:
        return self._pdf_path

    @pdf_path.setter
    def pdf_path(self, value):
        if not os.path.exists(value):
                        raise FileNotFoundError(f"File {value} does not exist")
        if pdfinfo_from_path(value)['Pages'] > 1:
            raise Exception("PDF has more than one page")
        self._pdf_path = value

    def get_png_data(self) -> bytes:
        try:
            pdf_images = convert_from_path(self._pdf_path)
        except PDFInfoNotInstalledError as e:
            raise PDFInfoNotInstalledError("poppler is not installed and add it to the PATH.") from e
        buffer = io.BytesIO()
        pdf_images[0].save(buffer, 'PNG')
        return buffer.getvalue()

