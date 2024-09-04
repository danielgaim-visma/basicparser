class HRProcessorError(Exception):
    """Base exception class for HR Processor errors."""
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class FileProcessingError(HRProcessorError):
    """Raised when there's an error processing a file."""
    pass

class APIError(HRProcessorError):
    """Raised when there's an error with API calls."""
    pass

