#!/bin/bash
# Helper script to generate next sequential tag number

type=$1
if [ -z "$type" ]; then
  echo "Usage: ./next-tag.sh [feat|fix|refactor|test|docs|style|perf|build|ci|chore]"
  echo ""
  echo "Types:"
  echo "  feat     - New functionality"
  echo "  fix      - Bug fix"
  echo "  refactor - Code refactoring"
  echo "  test     - Adding or updating tests"
  echo "  docs     - Documentation"
  echo "  style    - Formatting (not CSS)"
  echo "  perf     - Performance optimization"
  echo "  build    - Build system changes"
  echo "  ci       - CI/CD changes"
  echo "  chore    - Maintenance, minor changes"
  exit 1
fi

# Find last number for given type
last_num=$(git log --oneline --grep="\[$type-[0-9]\{3\}\]" | head -1 | grep -o "\[$type-[0-9]\{3\}\]" | grep -o "[0-9]\{3\}")

if [ -z "$last_num" ]; then
  next_num="001"
else
  # Remove leading zeros and increment
  next_num=$(printf "%03d" $((10#$last_num + 1)))
fi

echo "[$type-$next_num]"