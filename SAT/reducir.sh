#!/usr/bin/env bash

# Please Use Google Shell Style: https://google.github.io/styleguide/shell.xml

# ---- Start unofficial bash strict mode boilerplate
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -o errexit  # always exit on error
set -o errtrace # trap errors in functions as well
set -o pipefail # don't ignore exit codes when piping output
set -o posix    # more strict failures in subshells
# set -x          # enable debugging

IFS="$(printf "\n\t")"
# ---- End unofficial bash strict mode boilerplate

XSAT=$1

git ls-files | (grep -E '(^|/)InstanciasSAT/sc14-crafted' || true) | {
    while IFS= read -r file_path; do
        echo -n "reducing ${file_path}..."
        python Reductor/reductor.py ${XSAT} "${file_path}" > "./X-SAT/${file_path##*/}.txt"
        echo -n "success..."
        echo ✓
    done
}
