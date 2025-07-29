"""Command-line interface for Codexl."""

import click
import sys
from pathlib import Path
from typing import Optional


def infer_repo_name_from_url(url: str) -> str:
    """Infer repository name from a git URL."""
    name = url.rstrip('/').split('/')[-1]
    if name.endswith('.git'):
        name = name[:-4]
    return name

from .config import CodexlConfig
from .git_manager import GitManager
from .iterm_manager import ITermManager


@click.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True,
    help_option_names=['-h', '--help'],
))
@click.option('--init', is_flag=True, help='Initialize working directories')
@click.option('--num-dirs', '-n', default=5, help='Number of working directories to create (use with --init)')
@click.option('--add', '-a', is_flag=True, help='Add a git repository')
@click.option('--name', help='Repository name (use with --add)')
@click.option('--url', help='Repository URL (use with --add)')
@click.option('--list', 'list_repos', is_flag=True, help='List all repositories and working directories')
@click.option('--free', help='Mark a working directory as free/available')
@click.argument('task', required=False)
@click.pass_context
def main(ctx, init, num_dirs, add, name, url, list_repos, free, task):
    """Codexl - Manage multiple git repositories and working directories.
    
    Usage:
        codexl --init                      # Initialize working directories
        codexl --add                       # Add a git repository (interactive)
        codexl --add --name NAME --url URL # Add a git repository (direct)
        codexl --list                      # List repositories and directories
        codexl --free work1                # Free a working directory
        codexl 'do something'              # Execute command in a repository
    """
    
    # Handle --init
    if init:
        handle_init(num_dirs)
        return
    
    # Handle --add
    if add:
        handle_add(name, url)
        return
    
    # Handle --list
    if list_repos:
        handle_list()
        return
    
    # Handle --free
    if free:
        handle_free_workdir(free)
        return
    
    # Handle task execution
    if task:
        execute_task(task)
        return
    
    # If extra args exist, treat them as a task
    if ctx.args:
        task = ' '.join(ctx.args)
        execute_task(task)
        return
    
    # No arguments provided, show help
    click.echo(ctx.get_help())


def handle_init(num_dirs):
    """Handle the init functionality."""
    config = CodexlConfig()
    
    try:
        # Check OpenAI API key
        if not config.is_openai_api_key_configured():
            click.echo("🔑 OpenAI API key not found.")
            click.echo("Codexl uses the 'codex' command which requires an OpenAI API key.")
            
            try:
                api_key = click.prompt('Please enter your OpenAI API key')
                if api_key.strip():
                    config.set_openai_api_key(api_key.strip())
                    click.echo("✅ OpenAI API key saved to ~/.codexl/config.yaml")
                else:
                    click.echo("❌ No API key provided. Initialization cancelled.", err=True)
                    sys.exit(1)
            except click.Abort:
                click.echo("❌ API key input cancelled. Initialization cancelled.", err=True)
                sys.exit(1)
        else:
            click.echo("🔑 OpenAI API key found.")
        
        workdirs = config.init_workdirs(num_dirs)
        click.echo(f"✅ Initialized {num_dirs} working directories:")
        for workdir in workdirs:
            click.echo(f"   📁 {workdir}")
        
        click.echo(f"\n📍 Working directories created in: {config.work_base_dir}")
        click.echo(f"📝 Configuration saved to: {config.config_file}")
        
    except Exception as e:
        click.echo(f"❌ Error initializing directories: {e}", err=True)
        sys.exit(1)


def handle_add(name, url):
    """Handle the add functionality."""
    config = CodexlConfig()
    
    # Prompt for URL and infer name if missing
    if not url:
        url = click.prompt('Repository URL')
    if not name:
        name = infer_repo_name_from_url(url)
        click.echo(f"ℹ️  Inferred repository name '{name}' from URL")
    
    try:
        # Validate URL format (basic check)
        if not (url.startswith('http') or url.startswith('git@') or url.startswith('ssh://')):
            click.echo("⚠️  Warning: URL doesn't look like a standard git URL")
        
        config.add_repository(name, url)
        click.echo(f"✅ Added repository '{name}' with URL: {url}")
        
        # Show all repositories
        repos = config.get_repositories()
        if len(repos) > 1:
            click.echo(f"\n📚 All managed repositories:")
            for repo_name, repo_info in repos.items():
                click.echo(f"   • {repo_name}: {repo_info['url']}")
                
    except Exception as e:
        click.echo(f"❌ Error adding repository: {e}", err=True)
        sys.exit(1)


def handle_list():
    """Handle the list functionality."""
    config = CodexlConfig()
    
    # Show repositories
    repos = config.get_repositories()
    if repos:
        click.echo("📚 Managed repositories:")
        for name, info in repos.items():
            click.echo(f"   • {name}: {info['url']}")
    else:
        click.echo("📚 No repositories configured. Use 'codexl --add' to add some.")
    
    # Show working directories
    click.echo(f"\n📁 Working directories in {config.work_base_dir}:")
    workdirs = config._config.get("workdirs", {})
    if workdirs:
        for workdir_name, info in workdirs.items():
            status = "🔴 In use" if info.get("in_use") else "🟢 Available"
            current_repo = info.get("current_repo", "None")
            click.echo(f"   • {workdir_name}: {status} (Current repo: {current_repo})")
    else:
        click.echo("   No working directories found. Run 'codexl --init' first.")


def handle_free_workdir(workdir_name):
    """Handle the free functionality."""
    config = CodexlConfig()
    
    workdir_info = config.get_workdir_info(workdir_name)
    if not workdir_info:
        click.echo(f"❌ Working directory '{workdir_name}' not found.", err=True)
        sys.exit(1)
    
    config.mark_workdir_free(workdir_name)
    click.echo(f"✅ Marked '{workdir_name}' as available.")


def select_repository(config: CodexlConfig) -> Optional[str]:
    """Prompt user to select a repository."""
    repos = config.get_repositories()
    
    if not repos:
        click.echo("📚 No repositories configured yet.")
        click.echo("Let's add one now!")

        # Prompt for repository URL and infer name
        url = click.prompt('Repository URL')
        name = infer_repo_name_from_url(url)
        try:
            # Validate URL format (basic check)
            if not (url.startswith('http') or url.startswith('git@') or url.startswith('ssh://')):
                click.echo("⚠️  Warning: URL doesn't look like a standard git URL")

            config.add_repository(name, url)
            click.echo(f"✅ Added repository '{name}' with URL: {url}")
            return name

        except Exception as e:
            click.echo(f"❌ Error adding repository: {e}", err=True)
            return None
    
    if len(repos) == 1:
        repo_name = list(repos.keys())[0]
        click.echo(f"📦 Using repository: {repo_name}")
        return repo_name
    
    # Multiple repositories - let user choose
    click.echo("📦 Select a repository:")
    repo_list = list(repos.keys())
    for i, repo_name in enumerate(repo_list, 1):
        repo_url = repos[repo_name]['url']
        click.echo(f"   {i}. {repo_name} ({repo_url})")
    
    while True:
        try:
            choice = click.prompt("Enter repository number", type=int)
            if 1 <= choice <= len(repo_list):
                selected_repo = repo_list[choice - 1]
                click.echo(f"✅ Selected: {selected_repo}")
                return selected_repo
            else:
                click.echo(f"Please enter a number between 1 and {len(repo_list)}")
        except (ValueError, click.Abort):
            click.echo("❌ Operation cancelled.")
            return None


def execute_task(task: str):
    """Execute a task in a selected repository."""
    config = CodexlConfig()
    
    # Check if working directories are initialized
    workdirs = config._config.get("workdirs", {})
    if not workdirs:
        click.echo("❌ No working directories found. Run 'codexl --init' first.", err=True)
        sys.exit(1)
    
    # Select repository
    repo_name = select_repository(config)
    if not repo_name:
        sys.exit(1)
    
    # Get repository info
    repos = config.get_repositories()
    repo_info = repos[repo_name]
    repo_url = repo_info['url']
    
    # Find available working directory
    available_workdir = config.get_available_workdir()
    if not available_workdir:
        click.echo("❌ No available working directories. All are currently in use.", err=True)
        click.echo("💡 You can free up a directory using: codexl --free <workdir_name>")
        sys.exit(1)
    
    # Get working directory path
    workdir_path = config.get_workdir_path(available_workdir)
    repo_path = workdir_path / repo_name
    
    click.echo(f"📁 Using working directory: {available_workdir}")
    click.echo(f"📦 Repository: {repo_name}")
    click.echo(f"🎯 Task: {task}")
    
    # Mark working directory as in use
    config.mark_workdir_in_use(available_workdir, repo_name)
    
    # Clone repository if it doesn't exist
    if not repo_path.exists() or not GitManager.is_git_repo(repo_path):
        click.echo(f"📥 Cloning repository...")
        if not GitManager.clone_repo(repo_url, workdir_path, repo_name):
            click.echo("❌ Failed to clone repository.", err=True)
            config.mark_workdir_free(available_workdir)
            sys.exit(1)
    else:
        click.echo(f"📂 Repository already exists, pulling latest changes...")
        GitManager.pull_latest(repo_path)
    
    # Prepare the command to run
    command = f"codex '{task}'"
    
    # Open new iTerm2 window and run the command
    click.echo(f"🚀 Opening new terminal tab...")
    ITermManager.open_terminal_and_run(workdir_path, repo_name, command)
    
    click.echo(f"✅ Task started in {repo_path}")
    click.echo(f"💡 When done, free the working directory with: codexl --free {available_workdir}")


if __name__ == '__main__':
    main() 