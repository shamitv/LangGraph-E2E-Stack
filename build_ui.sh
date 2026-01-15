#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
frontend_dir="$repo_root/frontend"
backend_ui_dir="$repo_root/backend/agent_demo_framework/ui"

printf "Building frontend UI...\n"
cd "$frontend_dir"
npm install
npm run build

printf "Copying UI artifacts into package...\n"
mkdir -p "$backend_ui_dir/dist" "$backend_ui_dir/src"
cp -R "$frontend_dir/dist/." "$backend_ui_dir/dist/"
cp -R "$frontend_dir/src/." "$backend_ui_dir/src/"

printf "Done.\n"
