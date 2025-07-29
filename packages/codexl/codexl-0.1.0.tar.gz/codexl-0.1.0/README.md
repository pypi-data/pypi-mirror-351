# Codexl - Git Repository and Working Directory Manager

Codexl is a command-line tool that helps you manage multiple git repositories across multiple working directories. It automatically handles cloning, directory management, and opens new iTerm2 tabs to execute commands in the appropriate repository context.

## Features

- 🏗️ **Initialize multiple working directories** (`~/work/codexl/work1` to `~/work/codexl/workN`)
- 📦 **Manage multiple git repositories** with simple add/remove commands
- 🎯 **Execute commands in repository context** with automatic setup
- 🖥️ **iTerm2 integration** - opens new tabs automatically
- 🔄 **Automatic git operations** - cloning and pulling latest changes
- 📊 **Working directory tracking** - knows which directories are in use
- 🚀 **Smart repository setup** - prompts for repository details if none configured

## Installation

1. Clone this repository or download the source code
2. Navigate to the project directory
3. Install in development mode:

```bash
pipx install -e .
```

This will install the `codexl` command globally on your system.

## Quick Start

### 1. Initialize Working Directories

```bash
codexl --init
```

This creates 5 working directories by default: `~/work/codexl/work1` through `~/work/codexl/work5`

You can specify a different number:
```bash
codexl --init --num-dirs 10
```

### 2. Add Git Repositories (Optional)

```bash
codexl --add
# You'll be prompted for:
# Repository name: my-project
# Repository URL: https://github.com/user/my-project.git
```

Or specify directly:
```bash
codexl --add --name my-project --url https://github.com/user/my-project.git
```

Short form:
```bash
codexl -a
```

**Note:** If no repositories are configured when you run a task, Codexl will automatically prompt you to add one.

### 3. Execute Commands

```bash
codexl "implement user authentication"
```

This will:
1. Prompt you to add a repository if none are configured
2. Prompt you to select a repository (if multiple are configured)
3. Find an available working directory
4. Clone the repository if not already present (or pull latest changes)
5. Open a new iTerm2 tab
6. Navigate to the repository directory
7. Execute `codex "implement user authentication"`

## Commands

### `codexl --init [--num-dirs N]`
Initialize working directories. Creates N directories (default: 5) in `~/work/codexl/`.

### `codexl --add [--name NAME] [--url URL]` or `codexl -a`
Add a git repository to Codexl's management. If name/url not provided, you'll be prompted.

### `codexl --list`
Show all managed repositories and working directory status.

### `codexl --free <workdir_name>`
Mark a working directory as available (free it up for use).

### `codexl "your task description"`
Execute a task in a repository. This is the main command that:
- Prompts to add a repository if none configured
- Lets you select a repository if multiple exist
- Finds an available working directory
- Sets up the repository
- Opens iTerm2 tab and runs `codex "your task description"`

## Configuration

Codexl stores its configuration in `~/.codexl/config.yaml`. This includes:
- List of managed repositories
- Working directory status
- Configuration settings

Example configuration:
```yaml
max_workdirs: 5
repositories:
  my-project:
    url: https://github.com/user/my-project.git
    last_used: null
  another-repo:
    url: git@github.com:user/another-repo.git
    last_used: null
workdirs:
  work1:
    path: /Users/username/work/codexl/work1
    in_use: false
    current_repo: null
  work2:
    path: /Users/username/work/codexl/work2
    in_use: true
    current_repo: my-project
```

## Requirements

- Python 3.7+
- macOS (for iTerm2 integration)
- Git
- iTerm2 (recommended) or Terminal app

## Dependencies

- `click` - Command-line interface
- `gitpython` - Git operations
- `pyyaml` - Configuration management

## How It Works

1. **Working Directory Management**: Codexl maintains N working directories and tracks which ones are in use
2. **Repository Management**: Stores repository URLs and metadata
3. **Automatic Setup**: When you run a task, Codexl automatically:
   - Prompts for repository details if none configured
   - Finds an available working directory
   - Clones the repository if needed
   - Pulls latest changes if repository exists
   - Marks the directory as "in use"
4. **iTerm2 Integration**: Opens a new iTerm2 tab and executes your command
5. **Cleanup**: You manually free directories when done with `codexl --free <workdir>`

## Example Workflow

```bash
# Setup
codexl --init

# Work on tasks (will prompt for repo if none configured)
codexl "add login page"
# Prompts for repository details, uses work1, opens iTerm2 tab

codexl "fix database connection"
# Uses existing repo or prompts to select, uses work2, opens iTerm2 tab

# Add more repositories
codexl --add --name backend --url https://github.com/company/backend.git

# Check status
codexl --list

# Free up directories when done
codexl --free work1
codexl --free work2
```

## Troubleshooting

### iTerm2 not opening
- Ensure iTerm2 is installed
- Grant necessary permissions for AppleScript (System Preferences > Security & Privacy > Privacy > Automation)
- Codexl will fall back to Terminal app if iTerm2 is unavailable

### Repository clone failures
- Check your git credentials
- Verify repository URLs
- Ensure you have network connectivity

### Permission issues
- Make sure you have write permissions to `~/work/codexl/`
- Check that `~/.codexl/` directory is writable

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details. 