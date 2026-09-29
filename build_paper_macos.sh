#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This .app build must run on a Mac."
  exit 1
fi

# Use the hardware architecture even when Terminal itself runs under Rosetta.
native_arch="x86_64"
if [[ "$(sysctl -n hw.optional.arm64 2>/dev/null || true)" == "1" ]]; then
  native_arch="arm64"
fi
arch_runner=(/usr/bin/arch "-$native_arch")
echo "Mac CPU: $native_arch"

# Try native Homebrew and python.org first, then the current PATH. A wrong-CPU
# interpreter is skipped before venv/pip/PyInstaller can fail cryptically.
candidates=()
if [[ "$native_arch" == "arm64" ]]; then
  candidates+=("/opt/homebrew/bin/python3")
fi
candidates+=("/Library/Frameworks/Python.framework/Versions/Current/bin/python3")
for candidate in /Library/Frameworks/Python.framework/Versions/3.*/bin/python3; do
  [[ -e "$candidate" ]] && candidates+=("$candidate")
done
candidates+=("$(command -v python3 || true)" "/usr/local/bin/python3" "/usr/bin/python3")
selected_python=""
for candidate in "${candidates[@]}"; do
  if [[ -n "$candidate" && -x "$candidate" ]] &&
     "${arch_runner[@]}" "$candidate" -c 'import sys, tkinter; assert sys.version_info >= (3, 11)' >/dev/null 2>&1; then
    selected_python="$candidate"
    break
  fi
done
if [[ -z "$selected_python" ]]; then
  echo
  echo "Python 3.11+ with Tkinter for this Mac ($native_arch) was not found."
  echo "Install the macOS 64-bit universal2 Python from python.org,"
  echo "reopen Terminal, and run this .command again."
  echo "https://www.python.org/downloads/macos/"
  exit 1
fi
echo "Using Python: $selected_python"
"${arch_runner[@]}" "$selected_python" -c 'import sys, platform; print(sys.version.split()[0], platform.machine())'

venv_dir=".venv-$native_arch"
"${arch_runner[@]}" "$selected_python" -m venv --clear "$venv_dir"
"${arch_runner[@]}" "$venv_dir/bin/python" -m pip install --upgrade pip
"${arch_runner[@]}" "$venv_dir/bin/python" -m pip install -r requirements.txt 'pyinstaller>=6.0,<7'
"${arch_runner[@]}" "$venv_dir/bin/python" -m PyInstaller --noconfirm --clean --onedir --windowed \
  --name ChannelCircuitPaperLab \
  --target-arch "$native_arch" \
  --collect-all pypdfium2 \
  --osx-bundle-identifier org.channelcircuitlab.paper \
  paper_app.py

echo
echo "Built: $(pwd)/dist/ChannelCircuitPaperLab.app"
echo "Open that .app in Finder. Results save to your selected folder."
