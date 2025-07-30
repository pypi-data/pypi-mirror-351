#!/bin/bash
# Bash completion for dstack-yaml-manager

_dstack_yaml_manager_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    opts="--help --config --reset-config --restore-state --version"

    case ${prev} in
        --restore-state)
            # Complete with .json files
            COMPREPLY=( $(compgen -f -X "!*.json" -- ${cur}) )
            return 0
            ;;
        *)
            ;;
    esac

    if [[ ${cur} == -* ]] ; then
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi

    # Complete with directories for path argument
    COMPREPLY=( $(compgen -d -- ${cur}) )
}

complete -F _dstack_yaml_manager_completion dstack-yaml-manager