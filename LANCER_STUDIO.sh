#!/bin/bash
if command -v python3.10 &> /dev/null; then PY="python3.10"; else PY="python3"; fi
$PY app.py
