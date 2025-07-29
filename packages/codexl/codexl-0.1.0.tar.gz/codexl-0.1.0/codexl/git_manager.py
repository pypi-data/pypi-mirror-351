"""Git repository management for Codexl."""

import os
import subprocess
from pathlib import Path
from typing import Optional
import git
from git.exc import GitCommandError, InvalidGitRepositoryError


class GitManager:
    """Manages git operations for Codexl."""
    
    @staticmethod
    def is_git_repo(path: Path) -> bool:
        """Check if a directory is a git repository."""
        try:
            git.Repo(path)
            return True
        except (InvalidGitRepositoryError, git.exc.NoSuchPathError):
            return False
    
    @staticmethod
    def clone_repo(repo_url: str, target_dir: Path, repo_name: str) -> bool:
        """Clone a repository to the target directory."""
        try:
            # Create target directory if it doesn't exist
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Full path where the repo will be cloned
            repo_path = target_dir / repo_name
            
            # If repo already exists, just return True
            if repo_path.exists() and GitManager.is_git_repo(repo_path):
                print(f"Repository {repo_name} already exists in {repo_path}")
                return True
            
            # Clone the repository
            print(f"Cloning {repo_url} to {repo_path}...")
            git.Repo.clone_from(repo_url, repo_path)
            print(f"Successfully cloned {repo_name}")
            return True
            
        except GitCommandError as e:
            print(f"Error cloning repository: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False
    
    @staticmethod
    def get_repo_name_from_url(repo_url: str) -> str:
        """Extract repository name from URL."""
        # Handle various URL formats
        if repo_url.endswith('.git'):
            repo_url = repo_url[:-4]
        
        # Extract name from URL
        repo_name = repo_url.split('/')[-1]
        return repo_name
    
    @staticmethod
    def pull_latest(repo_path: Path) -> bool:
        """Pull latest changes from the repository."""
        try:
            if not GitManager.is_git_repo(repo_path):
                print(f"Not a git repository: {repo_path}")
                return False
            
            repo = git.Repo(repo_path)
            origin = repo.remotes.origin
            origin.pull()
            print(f"Pulled latest changes for {repo_path.name}")
            return True
            
        except GitCommandError as e:
            print(f"Error pulling repository: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False
    
    @staticmethod
    def get_current_branch(repo_path: Path) -> Optional[str]:
        """Get the current branch of the repository."""
        try:
            if not GitManager.is_git_repo(repo_path):
                return None
            
            repo = git.Repo(repo_path)
            return repo.active_branch.name
            
        except Exception:
            return None
    
    @staticmethod
    def get_repo_status(repo_path: Path) -> dict:
        """Get status information about the repository."""
        try:
            if not GitManager.is_git_repo(repo_path):
                return {"error": "Not a git repository"}
            
            repo = git.Repo(repo_path)
            
            return {
                "branch": repo.active_branch.name,
                "is_dirty": repo.is_dirty(),
                "untracked_files": repo.untracked_files,
                "modified_files": [item.a_path for item in repo.index.diff(None)],
                "staged_files": [item.a_path for item in repo.index.diff("HEAD")]
            }
            
        except Exception as e:
            return {"error": str(e)} 