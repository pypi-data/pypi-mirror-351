#compdef dstack-yaml-manager

_dstack_yaml_manager() {
    local context state line
    typeset -A opt_args

    _arguments -C \
        '(--help -h)'{--help,-h}'[Show help message]' \
        '--config[Show configuration information]' \
        '--reset-config[Reset configuration to defaults]' \
        '--restore-state[Restore from saved state file]:state file:_files -g "*.json"' \
        '--version[Show version number]' \
        '*:directory:_directories'
}

_dstack_yaml_manager "$@"