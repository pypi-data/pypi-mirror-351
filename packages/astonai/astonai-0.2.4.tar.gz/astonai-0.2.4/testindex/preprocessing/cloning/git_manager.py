from pathlib import Path
from typing import Optional, Dict, Any
import git
from testindex.core.config import ConfigModel
from testindex.core.logging import get_logger
from testindex.core.exceptions import TestIntelligenceError

class GitError(TestIntelligenceError):
    """Base exception for git operations."""
    error_code_prefix = "GIT"
    
class CloneError(GitError):
    """Exception raised when cloning fails."""
    error_code = "GIT001"
    
class UpdateError(GitError):
    """Exception raised when updating a repository fails."""
    error_code = "GIT002"
    
class CheckoutError(GitError):
    """Exception raised when checkout operation fails."""
    error_code = "GIT003"

class GitManager:
    """Manages git repository operations."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the GitManager with configuration.
        
        Args:
            config: Configuration dictionary containing Git settings
        """
        self.logger = get_logger("git-manager")
        self.config = config
        self.logger.info("GitManager initialized")
        
    def clone_repository(self, url: str, target_dir: Path, 
                         branch: Optional[str] = None) -> git.Repo:
        """Clone a git repository to the target directory.
        
        Args:
            url: The Git repository URL
            target_dir: Path to clone the repository to
            branch: Optional branch to checkout after cloning
            
        Returns:
            git.Repo: The cloned repository object
            
        Raises:
            CloneError: If cloning fails
        """
        self.logger.info(f"Cloning repository {url} to {target_dir}")
        
        try:
            # Create target directory if it doesn't exist
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Clone the repository
            repo = git.Repo.clone_from(url, target_dir)
            
            # Checkout specific branch if specified
            if branch:
                self.checkout_reference(repo, branch)
                
            self.logger.info(f"Repository cloned successfully: {url}")
            return repo
            
        except git.GitCommandError as e:
            error_msg = f"Failed to clone repository: {e}"
            self.logger.error(error_msg)
            raise CloneError(error_msg, details={"url": url, "target_dir": str(target_dir)})
        except Exception as e:
            error_msg = f"Unexpected error during clone: {e}"
            self.logger.error(error_msg)
            raise CloneError(error_msg, details={"url": url, "target_dir": str(target_dir)})
        
    def update_repository(self, repo_path: Path) -> bool:
        """Update an existing repository (git pull).
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            bool: True if update successful, False otherwise
            
        Raises:
            UpdateError: If updating fails
        """
        self.logger.info(f"Updating repository at {repo_path}")
        
        try:
            # Open the repository
            repo = git.Repo(repo_path)
            
            # Check if repository is dirty
            if repo.is_dirty():
                warning_msg = f"Repository at {repo_path} has uncommitted changes"
                self.logger.warning(warning_msg)
                
            # Pull from the remote
            origin = repo.remotes.origin
            origin.pull()
            
            self.logger.info(f"Repository updated successfully: {repo_path}")
            return True
            
        except git.GitCommandError as e:
            error_msg = f"Failed to update repository: {e}"
            self.logger.error(error_msg)
            raise UpdateError(error_msg, details={"repo_path": str(repo_path)})
        except git.NoSuchPathError:
            error_msg = f"Repository path does not exist: {repo_path}"
            self.logger.error(error_msg)
            raise UpdateError(error_msg, details={"repo_path": str(repo_path)})
        except Exception as e:
            error_msg = f"Unexpected error during update: {e}"
            self.logger.error(error_msg)
            raise UpdateError(error_msg, details={"repo_path": str(repo_path)})
        
    def checkout_reference(self, repo: git.Repo, reference: str) -> bool:
        """Checkout a specific branch, tag or commit.
        
        Args:
            repo: Repository object
            reference: Branch, tag, or commit hash to checkout
            
        Returns:
            bool: True if checkout successful
            
        Raises:
            CheckoutError: If checkout fails
        """
        self.logger.info(f"Checking out reference: {reference}")
        
        try:
            repo.git.checkout(reference)
            self.logger.info(f"Successfully checked out {reference}")
            return True
            
        except git.GitCommandError as e:
            error_msg = f"Failed to checkout reference {reference}: {e}"
            self.logger.error(error_msg)
            raise CheckoutError(error_msg, details={"reference": reference})
        except Exception as e:
            error_msg = f"Unexpected error during checkout: {e}"
            self.logger.error(error_msg)
            raise CheckoutError(error_msg, details={"reference": reference})

    def get_latest_commit(self, repo: git.Repo) -> Dict[str, Any]:
        """Get information about the latest commit.
        
        Args:
            repo: Repository object
            
        Returns:
            Dict: Information about the latest commit
        """
        try:
            commit = repo.head.commit
            return {
                "hash": commit.hexsha,
                "author": commit.author.name,
                "email": commit.author.email,
                "date": commit.committed_datetime.isoformat(),
                "message": commit.message.strip(),
            }
        except Exception as e:
            self.logger.error(f"Failed to get latest commit: {e}")
            return {
                "hash": None,
                "error": str(e)
            }
