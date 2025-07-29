"""iTerm2 integration for Codexl."""

import subprocess
import os
from pathlib import Path


class ITermManager:
    """Manages iTerm2 operations for Codexl."""
    
    @staticmethod
    def open_new_tab_and_run(workdir_path: Path, repo_name: str, command: str):
        """Open a new iTerm2 tab, cd to workdir/repo, and run the command."""
        repo_path = workdir_path / repo_name
        
        # AppleScript to create new iTerm2 tab and run commands
        applescript = f'''
        tell application "iTerm2"
            activate
            tell current window
                create tab with default profile
                tell current session
                    write text "cd '{repo_path}'"
                    write text "{command}"
                end tell
            end tell
        end tell
        '''
        
        try:
            # Execute the AppleScript
            subprocess.run(['osascript', '-e', applescript], check=True)
            print(f"Opened new iTerm2 tab in {repo_path}")
            print(f"Running command: {command}")
        except subprocess.CalledProcessError as e:
            print(f"Error opening iTerm2 tab: {e}")
            # Fallback: print instructions for manual execution
            print(f"Please manually:")
            print(f"1. Open a new terminal tab")
            print(f"2. cd {repo_path}")
            print(f"3. Run: {command}")
        except FileNotFoundError:
            print("osascript not found. Are you running on macOS?")
            # Fallback: print instructions for manual execution
            print(f"Please manually:")
            print(f"1. Open a new terminal tab")
            print(f"2. cd {repo_path}")
            print(f"3. Run: {command}")
    
    @staticmethod
    def is_iterm_available() -> bool:
        """Check if iTerm2 is available on the system."""
        try:
            # Check if iTerm2 is installed
            result = subprocess.run(['osascript', '-e', 'tell application "System Events" to exists application process "iTerm2"'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    @staticmethod
    def open_simple_terminal(workdir_path: Path, repo_name: str, command: str):
        """Fallback method to open terminal using macOS Terminal app."""
        repo_path = workdir_path / repo_name
        
        applescript = f'''
        tell application "Terminal"
            activate
            do script "cd '{repo_path}' && {command}"
        end tell
        '''
        
        try:
            subprocess.run(['osascript', '-e', applescript], check=True)
            print(f"Opened new Terminal window in {repo_path}")
            print(f"Running command: {command}")
        except subprocess.CalledProcessError as e:
            print(f"Error opening Terminal window: {e}")
            print(f"Please manually:")
            print(f"1. Open a new terminal tab")
            print(f"2. cd {repo_path}")
            print(f"3. Run: {command}")
    
    @staticmethod
    def open_terminal_and_run(workdir_path: Path, repo_name: str, command: str):
        """Open terminal (iTerm2 preferred, fallback to Terminal) and run command."""
        if ITermManager.is_iterm_available():
            ITermManager.open_new_tab_and_run(workdir_path, repo_name, command)
        else:
            print("iTerm2 not available, using Terminal app...")
            ITermManager.open_simple_terminal(workdir_path, repo_name, command) 