#!/bin/bash
# Double-click to run homeguard_system.py.
# macOS counterpart of run_homeguard.bat — Finder runs .command files on double-click.
# Author: Nnanyelugo Ahukannah

# Run from this file's own folder so data/ paths resolve correctly.
cd "$(dirname "$0")"

# Prefer the pinned labs venv (pandas 2.2.2 / sklearn 1.4.2), which is what the
# notebooks' "python3" kernel also points at. Fall back to whatever python3 exists.
PY="$HOME/.venvs/labs/bin/python"
[ -x "$PY" ] || PY="$(command -v python3)"

"$PY" homeguard_system.py
exitcode=$?

echo
if [ "$exitcode" -ne 0 ]; then
    echo "[ERROR] The script exited with code $exitcode."
    echo "Make sure the labs venv exists (see machine-setup/restore.sh)."
fi
echo "----------------------------------------"
echo "Script finished. Press any key to close."
read -n 1 -s
