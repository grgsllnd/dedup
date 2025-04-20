#!/usr/bin/env bash
# This script generates test files for the `diff` command.
# It creates a directory structure with various test cases for the `diff` command.
# The script creates the following directory structure:
# Usage: ./generate_test_files.sh [output_directory]
# $ sh generate_test_files.sh 

set -e

ROOT="${1:-./test_data}"

mkdir -p \
  "$ROOT"/{same_name_same_content,same_name_diff_content,diff_name_same_content,diff_name_diff_content} \
  "$ROOT"/nested/{same_name_same_content,same_name_diff_content,diff_name_same_content,diff_name_diff_content}

echo "Hello Duplicate" > "$ROOT"/same_name_same_content/file.txt
echo "Hello Duplicate" > "$ROOT"/nested/same_name_same_content/file.txt

echo "Root Version"    > "$ROOT"/same_name_diff_content/file.txt
echo "Nested Version"  > "$ROOT"/nested/same_name_diff_content/file.txt

echo "Common Content"  > "$ROOT"/diff_name_same_content/a.txt
echo "Common Content"  > "$ROOT"/nested/diff_name_same_content/b.txt

echo "Content A"       > "$ROOT"/diff_name_diff_content/a.txt
echo "Content B"       > "$ROOT"/nested/diff_name_diff_content/b.txt

mkdir -p \
  "$ROOT"/{same_name_same_content,same_name_diff_content,diff_name_same_content,diff_name_diff_content} \
  "$ROOT"/nested/{same_name_same_content,same_name_diff_content,diff_name_same_content,diff_name_diff_content} \
  "$ROOT"/nested/nested2/{same_name_same_content,same_name_diff_content,diff_name_same_content,diff_name_diff_content} \
  "$ROOT"/target/ 

# Root-level
echo "Hello Duplicate" > "$ROOT"/same_name_same_content/file.txt
echo "Root Version"    > "$ROOT"/same_name_diff_content/file.txt
echo "Common Content"  > "$ROOT"/diff_name_same_content/a.txt
echo "Content A"       > "$ROOT"/diff_name_diff_content/a.txt

# First nested level
echo "Hello Duplicate" > "$ROOT"/nested/same_name_same_content/file.txt
echo "Nested Version"  > "$ROOT"/nested/same_name_diff_content/file.txt
echo "Common Content"  > "$ROOT"/nested/diff_name_same_content/b.txt
echo "Content B"       > "$ROOT"/nested/diff_name_diff_content/b.txt

# Second nested level
echo "Hello Duplicate" > "$ROOT"/nested/nested2/same_name_same_content/file.txt
echo "Nested2 Version" > "$ROOT"/nested/nested2/same_name_diff_content/file.txt
echo "Common Content"  > "$ROOT"/nested/nested2/diff_name_same_content/b.txt
echo "Content B2"      > "$ROOT"/nested/nested2/diff_name_diff_content/b.txt

echo "Test files generated under $ROOT"