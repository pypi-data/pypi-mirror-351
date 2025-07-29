"""
AST parsing utilities for Python code analysis.
"""
import ast
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any, Type

from testindex.core.logging import get_logger
from testindex.core.exceptions import TestIntelligenceError
from testindex.core.config import ConfigModel

# Define exceptions
class ParsingError(TestIntelligenceError):
    """Base exception for parsing errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize a parsing error."""
        super().__init__(message=message, error_code="PARSE000", details=details)

class FileParsingError(ParsingError):
    """Exception raised when parsing a file fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize a file parsing error."""
        super().__init__(message=message, details=details)

class ASTParsingError(ParsingError):
    """Exception raised when AST parsing fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize an AST parsing error."""
        super().__init__(message=message, details=details)

class FrameworkDetectionError(ParsingError):
    """Exception raised when framework detection fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize a framework detection error."""
        super().__init__(message=message, details=details)

class ASTParser:
    """Base class for parsing Python files into AST."""
    
    def __init__(self, config: ConfigModel):
        """Initialize the AST parser.
        
        Args:
            config: Configuration object
        """
        self.logger = get_logger("ast-parser")
        self.config = config
        self.cache: Dict[str, ast.AST] = {}
        
    def parse_file(self, file_path: Union[str, Path]) -> ast.Module:
        """Parse a Python file into an AST.
        
        Args:
            file_path: Path to the Python file to parse
            
        Returns:
            ast.Module: The parsed AST
            
        Raises:
            FileParsingError: If the file cannot be read
            ASTParsingError: If the file cannot be parsed
        """
        file_path = Path(file_path)
        abs_path = str(file_path.absolute())
        
        # Check cache
        if abs_path in self.cache:
            self.logger.debug(f"Using cached AST for {file_path}")
            return self.cache[abs_path]
        
        self.logger.debug(f"Parsing {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
        except Exception as e:
            error_msg = f"Failed to read file {file_path}: {e}"
            self.logger.error(error_msg)
            raise FileParsingError(error_msg, details={"file": str(file_path)})
        
        return self.parse_source(source, file_path=abs_path)
    
    def parse_source(self, source: str, file_path: Optional[str] = None) -> ast.Module:
        """Parse Python source code into an AST.
        
        Args:
            source: The source code to parse
            file_path: Optional file path for caching
            
        Returns:
            ast.Module: The parsed AST
            
        Raises:
            ASTParsingError: If the source code cannot be parsed
        """
        try:
            tree = ast.parse(source)
            
            # Cache if file_path is provided
            if file_path:
                self.cache[file_path] = tree
                
            return tree
        except SyntaxError as e:
            error_msg = f"Syntax error in {'source' if not file_path else file_path}: {e}"
            self.logger.error(error_msg)
            raise ASTParsingError(error_msg, details={
                "file": file_path,
                "line": e.lineno,
                "column": e.offset,
                "text": e.text
            })
        except Exception as e:
            error_msg = f"Failed to parse {'source' if not file_path else file_path}: {e}"
            self.logger.error(error_msg)
            raise ASTParsingError(error_msg, details={"file": file_path})
    
    def clear_cache(self) -> None:
        """Clear the parser cache."""
        self.cache.clear()
        
    def parse_directory(self, dir_path: Union[str, Path], 
                       recursive: bool = True,
                       ignore_errors: bool = False) -> Dict[str, ast.Module]:
        """Parse all Python files in a directory.
        
        Args:
            dir_path: Directory path to parse
            recursive: Whether to parse subdirectories
            ignore_errors: Whether to ignore parsing errors
            
        Returns:
            Dict[str, ast.Module]: Dictionary mapping file paths to ASTs
        """
        dir_path = Path(dir_path)
        result: Dict[str, ast.Module] = {}
        
        self.logger.info(f"Parsing directory: {dir_path}")
        
        try:
            files = self._get_python_files(dir_path, recursive)
            
            for file_path in files:
                try:
                    ast_module = self.parse_file(file_path)
                    result[str(file_path)] = ast_module
                except (FileParsingError, ASTParsingError) as e:
                    if not ignore_errors:
                        raise
                    self.logger.warning(f"Ignoring error in {file_path}: {e}")
            
            self.logger.info(f"Parsed {len(result)} Python files in {dir_path}")
            return result
        
        except Exception as e:
            error_msg = f"Failed to parse directory {dir_path}: {e}"
            self.logger.error(error_msg)
            raise ParsingError(error_msg, details={"directory": str(dir_path)})
    
    def _get_python_files(self, dir_path: Path, recursive: bool = True) -> List[Path]:
        """Get all Python files in a directory.
        
        Args:
            dir_path: Directory path
            recursive: Whether to include subdirectories
            
        Returns:
            List[Path]: List of Python file paths
        """
        files = []
        
        if recursive:
            # Walk through all subdirectories
            for root, _, filenames in os.walk(dir_path):
                for filename in filenames:
                    if filename.endswith('.py'):
                        files.append(Path(root) / filename)
        else:
            # Only get files in the current directory
            for item in dir_path.iterdir():
                if item.is_file() and item.name.endswith('.py'):
                    files.append(item)
        
        return files

    def visit_file_with_visitor(self, file_path: Union[str, Path], 
                                visitor_class: Type[ast.NodeVisitor],
                                visitor_args: Optional[Dict[str, Any]] = None) -> ast.NodeVisitor:
        """Parse a file and apply a visitor to its AST.
        
        Args:
            file_path: Path to the Python file
            visitor_class: AST visitor class to use
            visitor_args: Optional arguments to pass to the visitor constructor
            
        Returns:
            ast.NodeVisitor: The visitor instance after traversal
        """
        file_path = Path(file_path)
        visitor_args = visitor_args or {}
        
        try:
            tree = self.parse_file(file_path)
            visitor = visitor_class(file_path=str(file_path), **visitor_args)
            visitor.visit(tree)
            return visitor
        except Exception as e:
            error_msg = f"Failed to visit AST for {file_path}: {e}"
            self.logger.error(error_msg)
            raise ParsingError(error_msg, details={"file": str(file_path)})
    
    def detect_framework(self, file_path: Union[str, Path]) -> str:
        """Detect testing framework used in a Python file.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            str: Detected framework name or "unknown"
        """
        # This functionality is implemented in framework_detector.py
        from testindex.preprocessing.parsing.frameworks.framework_detector import detect_framework
        
        try:
            return detect_framework(self, file_path)
        except Exception as e:
            error_msg = f"Framework detection failed for {file_path}: {e}"
            self.logger.error(error_msg)
            raise FrameworkDetectionError(error_msg, details={"file": str(file_path)}) 