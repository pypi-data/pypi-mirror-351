"""Custom exception classes for the WordProcessor module."""

class WordProcessorError(Exception):
    """Base exception for WordProcessor errors."""
    pass

class DocumentNotFoundError(WordProcessorError):
    """Exception raised when the specified document file is not found."""
    def __init__(self, filepath: str, message="Document file not found"):
        self.filepath = filepath
        self.message = f"{message}: {filepath}"
        super().__init__(self.message)

class InvalidDocumentError(WordProcessorError):
    """Exception raised when the document is not a valid .docx file or is corrupt."""
    def __init__(self, filepath: str, message="Invalid .docx file or corrupt package"):
        self.filepath = filepath
        self.message = f"{message}: {filepath}"
        super().__init__(self.message)

class DocumentLoadingError(WordProcessorError):
    """Exception raised for general errors during document loading."""
    def __init__(self, filepath: str, original_exception: Exception = None, message="Failed to load document"):
        self.filepath = filepath
        self.original_exception = original_exception
        self.message = f"{message}: {filepath}"
        if original_exception:
            self.message += f" (Original error: {original_exception})"
        super().__init__(self.message)

class DocumentSavingError(WordProcessorError):
    """Exception raised for errors during document saving."""
    def __init__(self, filepath: str, original_exception: Exception = None, message="Failed to save document"):
        self.filepath = filepath
        self.original_exception = original_exception
        self.message = f"{message}: {filepath}"
        if original_exception:
            self.message += f" (Original error: {original_exception})"
        super().__init__(self.message)

class XMLParsingError(WordProcessorError):
    """Exception raised for errors during XML parsing of document parts."""
    def __init__(self, part_name: str, original_exception: Exception = None, message="Failed to parse XML part"):
        self.part_name = part_name
        self.original_exception = original_exception
        self.message = f"{message}: {part_name}"
        if original_exception:
            self.message += f" (Original error: {original_exception})"
        super().__init__(self.message)

class DocumentNotLoadedError(WordProcessorError):
    """Exception raised when an operation is attempted on a document that has not been loaded."""
    def __init__(self, message="Document not loaded. Call load_document() first."):
        self.message = message
        super().__init__(self.message)
