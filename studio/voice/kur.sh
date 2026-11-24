#!/usr/bin/env bash
# Türkçe seslendirme modelini indirir (repoya dahil değil, ~60 MB).
set -euo pipefail
cd "$(dirname "$0")"
pip install -q piper-tts
for f in tr_TR-dfki-medium.onnx tr_TR-dfki-medium.onnx.json; do
  [ -f "$f" ] || curl -sSL -o "$f" \
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/tr/tr_TR/dfki/medium/$f"
done
echo "hazir"
