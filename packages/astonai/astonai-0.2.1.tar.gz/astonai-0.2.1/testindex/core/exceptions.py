"""
Exception handling framework for the Test Intelligence Engine.

This module defines a hierarchy of custom exceptions used throughout the application.
Each exception type includes an error code and standardized message format to
provide consistent error reporting and handling.
"""
from typing import Any, Dict, Optional


class TestIntelligenceError(Exception):
    """Base exception class for all application-specific exceptions."""
    
    def __init__(
        self, 
        message: str,
        error_code: str = "E000",
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new TestIntelligenceError.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code (default: "E000")
            details: Additional details about the error (default: None)
        """
        self.error_code = error_code
        self.details = details or {}
        self.message = message
        super().__init__(f"[{error_code}] {message}")


class BaseException(TestIntelligenceError):
    """Base exception for domain-specific error hierarchies."""
    
    error_code_prefix = "BASE"
    error_code = "BASE000"
    
    def __init__(
        self, 
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new BaseException.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code (default: cls.error_code)
            details: Additional details about the error (default: None)
        """
        actual_error_code = error_code or self.error_code
        super().__init__(message=message, error_code=actual_error_code, details=details)


class ConfigurationError(TestIntelligenceError):
    """Exception raised for configuration-related errors."""
    
    def __init__(
        self, 
        message: str,
        error_code: str = "E100",
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new ConfigurationError.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code (default: "E100")
            details: Additional details about the error (default: None)
        """
        super().__init__(message=message, error_code=error_code, details=details)


class StorageError(TestIntelligenceError):
    """Exception raised for storage-related errors."""
    
    def __init__(
        self, 
        message: str,
        error_code: str = "E200",
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new StorageError.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code (default: "E200")
            details: Additional details about the error (default: None)
        """
        super().__init__(message=message, error_code=error_code, details=details)


class CLIError(TestIntelligenceError):
    """Exception raised for CLI-related errors."""
    
    def __init__(
        self, 
        message: str,
        error_code: str = "E300",
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new CLIError.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code (default: "E300")
            details: Additional details about the error (default: None)
        """
        super().__init__(message=message, error_code=error_code, details=details)


class LoggingError(TestIntelligenceError):
    """Exception raised for logging-related errors."""
    
    def __init__(
        self, 
        message: str,
        error_code: str = "E400",
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new LoggingError.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code (default: "E400")
            details: Additional details about the error (default: None)
        """
        super().__init__(message=message, error_code=error_code, details=details)


class ValidationError(TestIntelligenceError):
    """Exception raised for data validation errors."""
    
    def __init__(
        self, 
        message: str,
        error_code: str = "E500",
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new ValidationError.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code (default: "E500")
            details: Additional details about the error (default: None)
        """
        super().__init__(message=message, error_code=error_code, details=details)
