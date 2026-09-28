#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if bash ./build_paper_macos.sh && open ./dist/ChannelCircuitPaperLab.app; then
  echo "ChannelCircuitPaperLab.app opened. Next time, open the app in dist."
else
  echo "Build or launch failed. See the error above."
  if [[ -t 0 ]]; then
    read -r -p "Press Return to close: " _
  fi
  exit 1
fi
