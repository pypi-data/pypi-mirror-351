"""Configuration management for Codexl."""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional


class CodexlConfig:
    """Manages Codexl configuration and state."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".codexl"
        self.config_file = self.config_dir / "config.yaml"
        self.work_base_dir = Path.home() / "work" / "codexl"
        self.max_workdirs = 5
        self._config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from file."""
        if not self.config_file.exists():
            return {
                "repositories": {},
                "workdirs": {},
                "max_workdirs": self.max_workdirs,
                "openai_api_key": None
            }

        with open(self.config_file, 'r') as f:
            config = yaml.safe_load(f) or {}
            # Ensure openai_api_key field exists
            if "openai_api_key" not in config:
                config["openai_api_key"] = None
            return config
    
    def _save_config(self):
        """Save configuration to file."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            yaml.dump(self._config, f, default_flow_style=False)

    def get_openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key from environment or config."""
        # First check environment variable
        env_key = os.getenv('OPENAI_API_KEY')
        if env_key:
            return env_key

        # Then check saved config
        return self._config.get('openai_api_key')

    def set_openai_api_key(self, api_key: str):
        """Set OpenAI API key in config."""
        self._config['openai_api_key'] = api_key
        self._save_config()

    def is_openai_api_key_configured(self) -> bool:
        """Check if OpenAI API key is available."""
        return self.get_openai_api_key() is not None
    
    def init_workdirs(self, num_dirs: int = 5):
        """Initialize working directories."""
        self.max_workdirs = num_dirs
        self._config["max_workdirs"] = num_dirs
        
        # Create work directories
        for i in range(1, num_dirs + 1):
            workdir = self.work_base_dir / f"work{i}"
            workdir.mkdir(parents=True, exist_ok=True)
            
            # Initialize workdir state if not exists
            if f"work{i}" not in self._config.get("workdirs", {}):
                if "workdirs" not in self._config:
                    self._config["workdirs"] = {}
                self._config["workdirs"][f"work{i}"] = {
                    "path": str(workdir),
                    "in_use": False,
                    "current_repo": None
                }
        
        self._save_config()
        return [self.work_base_dir / f"work{i}" for i in range(1, num_dirs + 1)]
    
    def add_repository(self, name: str, url: str):
        """Add a repository to the managed list."""
        if "repositories" not in self._config:
            self._config["repositories"] = {}
        
        self._config["repositories"][name] = {
            "url": url,
            "last_used": None
        }
        self._save_config()
    
    def get_repositories(self) -> Dict[str, Dict]:
        """Get all managed repositories."""
        return self._config.get("repositories", {})
    
    def get_available_workdir(self) -> Optional[str]:
        """Get an available working directory."""
        workdirs = self._config.get("workdirs", {})
        for workdir_name, info in workdirs.items():
            if not info.get("in_use", False):
                return workdir_name
        return None
    
    def mark_workdir_in_use(self, workdir_name: str, repo_name: str):
        """Mark a working directory as in use."""
        if "workdirs" not in self._config:
            self._config["workdirs"] = {}
        
        if workdir_name not in self._config["workdirs"]:
            workdir_path = self.work_base_dir / workdir_name
            self._config["workdirs"][workdir_name] = {
                "path": str(workdir_path),
                "in_use": False,
                "current_repo": None
            }
        
        self._config["workdirs"][workdir_name]["in_use"] = True
        self._config["workdirs"][workdir_name]["current_repo"] = repo_name
        self._save_config()
    
    def mark_workdir_free(self, workdir_name: str):
        """Mark a working directory as free."""
        if workdir_name in self._config.get("workdirs", {}):
            self._config["workdirs"][workdir_name]["in_use"] = False
            self._config["workdirs"][workdir_name]["current_repo"] = None
            self._save_config()
    
    def get_workdir_path(self, workdir_name: str) -> Path:
        """Get the path for a working directory."""
        return self.work_base_dir / workdir_name
    
    def get_workdir_info(self, workdir_name: str) -> Optional[Dict]:
        """Get information about a working directory."""
        return self._config.get("workdirs", {}).get(workdir_name) 