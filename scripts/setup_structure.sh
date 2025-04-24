#!/usr/bin/env bash
# run with sh ./scripts/setup_structure.sh
set -e

# Determine project root two levels above this script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Array of directories to ensure exist
dirs=(
  "$BASE_DIR/dedup/data"
  "$BASE_DIR/dedup/logs"
  "$BASE_DIR/dedup/processing"
  "$BASE_DIR/dedup/settings"
  "$BASE_DIR/dedup/ui"
)

# Create directories if they don't exist
for d in "${dirs[@]}"; do
  if [ -d "$d" ]; then
    echo "Exists: $d"
  else
    mkdir -p "$d"
    echo "Created: $d"
  fi
done

# Array of __init__.py files to ensure exist (only package folders)
inits=(
  "$BASE_DIR/dedup/processing/__init__.py"
  "$BASE_DIR/dedup/settings/__init__.py"
  "$BASE_DIR/dedup/ui/__init__.py"
)

#
# Touch init files if missing, without overriding existing content
for f in "${inits[@]}"; do
  if [ -e "$f" ]; then
    echo "Exists: $f"
  else
    touch "$f"
    echo "Created: $f"
  fi
done


# Ensure data files exist
data_files=(
  "$BASE_DIR/dedup/data/dedup.settings"
  "$BASE_DIR/dedup/data/destination_files.json"
)
for df in "${data_files[@]}"; do
  if [ -e "$df" ]; then
    echo "Exists: $df"
  else
    touch "$df"
    echo "Created: $df"
  fi
done

# Ensure processing module files exist
processing_files=(
  "$BASE_DIR/dedup/processing/hashing.py"
  "$BASE_DIR/dedup/processing/walker.py"
  "$BASE_DIR/dedup/processing/indexer.py"
  "$BASE_DIR/dedup/processing/mover.py"
  "$BASE_DIR/dedup/processing/orchestrator.py"
  "$BASE_DIR/dedup/processing/logger.py"
)
for pf in "${processing_files[@]}"; do
  if [ -e "$pf" ]; then
    echo "Exists: $pf"
  else
    cat > "$pf" << 'EOF'
# Auto-generated stub for $(basename "$pf")
# TODO: implement functionality
EOF
    echo "Created stub: $pf"
  fi
done

# Ensure settings module file exist
settings_files=(
  "$BASE_DIR/dedup/settings/state.py"
)
for sf in "${settings_files[@]}"; do
  if [ -e "$sf" ]; then
    echo "Exists: $sf"
  else
    cat > "$sf" << 'EOF'
# Auto-generated stub for $(basename "$sf")
# TODO: implement settings/state functionality
EOF
    echo "Created stub: $sf"
  fi
done

echo "Project structure ensured."