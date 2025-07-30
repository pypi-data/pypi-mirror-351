from .converter_core import (
    convert_markdown,             # Core text-to-bytes function
    convert_file_to_pdf,          # Helper for file-to-PDF
    convert_file_to_docx,         # Helper for file-to-DOCX
    BASE_PDF_CSS,                 # Constant: Base CSS for PDF
    PANDOC_PATH_ENV_VAR,          # Constant: Name of the env var for Pandoc path
    REFERENCE_DOCX_PATH_ENV_VAR   # Constant: Name of the env var for Reference DOCX path
)

__version__ = "0.1.1"


__all__ = [
    "convert_markdown",
    "convert_file_to_pdf",
    "convert_file_to_docx",
    "BASE_PDF_CSS",
    "PANDOC_PATH_ENV_VAR",
    "REFERENCE_DOCX_PATH_ENV_VAR",
    "__version__",
]
