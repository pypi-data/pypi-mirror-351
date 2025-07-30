# Shell Auto-Completion Setup

## Basic Command Recognition

If `dstack-yaml-manager` command is not auto-completing at all:

### 1. **Refresh Shell**
```bash
# Restart terminal OR run:
hash -r        # bash
rehash         # zsh
```

### 2. **Check Installation**
```bash
which dstack-yaml-manager
pip show dstack-yaml-manager
```

### 3. **Fix PATH** (if command not found)
```bash
# Check if pip install location is in PATH
echo $PATH
python -m site --user-base

# Add to ~/.bashrc or ~/.zshrc if needed:
export PATH="$PATH:$(python -m site --user-base)/bin"
```

## Advanced Auto-Completion (Arguments & Options)

For better tab completion of command arguments:

### Bash Completion

1. **Install completion file:**
```bash
# System-wide (requires sudo)
sudo cp completions/dstack-yaml-manager-completion.bash /etc/bash_completion.d/

# OR User-specific
mkdir -p ~/.local/share/bash-completion/completions
cp completions/dstack-yaml-manager-completion.bash ~/.local/share/bash-completion/completions/dstack-yaml-manager
```

2. **Enable in ~/.bashrc:**
```bash
# Add to ~/.bashrc
if [ -f ~/.local/share/bash-completion/completions/dstack-yaml-manager ]; then
    source ~/.local/share/bash-completion/completions/dstack-yaml-manager
fi
```

3. **Reload:**
```bash
source ~/.bashrc
```

### Zsh Completion

1. **Install completion file:**
```bash
# Create completions directory
mkdir -p ~/.zsh/completions

# Copy completion file
cp completions/dstack-yaml-manager-completion.zsh ~/.zsh/completions/_dstack-yaml-manager
```

2. **Enable in ~/.zshrc:**
```bash
# Add to ~/.zshrc
fpath=(~/.zsh/completions $fpath)
autoload -U compinit
compinit
```

3. **Reload:**
```bash
source ~/.zshrc
```

### Fish Completion

Fish automatically handles completions for installed packages, but you can create custom ones:

```bash
# Create completion file
mkdir -p ~/.config/fish/completions

# Create basic completion
cat > ~/.config/fish/completions/dstack-yaml-manager.fish << 'EOF'
complete -c dstack-yaml-manager -l help -d "Show help message"
complete -c dstack-yaml-manager -l config -d "Show configuration"
complete -c dstack-yaml-manager -l reset-config -d "Reset configuration"
complete -c dstack-yaml-manager -l version -d "Show version"
complete -c dstack-yaml-manager -l restore-state -d "Restore state file" -r
EOF
```

## Test Completion

After setup, test with:
```bash
dstack-yaml-manager <TAB>
dstack-yaml-manager --<TAB>
```

## Aliases (Alternative)

If auto-completion still doesn't work, create aliases:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias dsm='dstack-yaml-manager'
alias dstack-mgmt='dstack-yaml-manager'
```

## Troubleshooting

**Command not found:**
- Check `which dstack-yaml-manager`
- Verify PATH includes pip install location
- Try `python -m dstack_mgmt.cli` as alternative

**Completion not working:**
- Restart terminal
- Run `hash -r` (bash) or `rehash` (zsh)
- Check shell completion is enabled

**Permission issues:**
- Use user-specific completion directories
- Don't use `sudo pip install` (use `--user` flag instead)