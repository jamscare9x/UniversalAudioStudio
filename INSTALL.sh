#!/bin/bash
if command -v python3.10 &> /dev/null; then PY="python3.10"; else PY="python3"; fi
$PY -m pip install "audio-separator[cpu]==0.29.0"
$PY -m pip install -r requirements.txt
