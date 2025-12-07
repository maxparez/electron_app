#!/usr/bin/env bash
# Synchronizes the windows-install branch with a curated subset of files.
set -euo pipefail

BRANCH="${1:-windows-install}"
BASE_REF="${2:-origin/main}"
ROOT_DIR="$(git rev-parse --show-toplevel)"
INCLUDE_FILE="$ROOT_DIR/config/windows_branch_include.txt"
WORKTREE_DIR="$ROOT_DIR/.windows-install-worktree"

if [[ ! -f "$INCLUDE_FILE" ]]; then
  echo "Include file $INCLUDE_FILE not found." >&2
  exit 1
fi

if ! git diff --quiet --ignore-submodules --exit-code; then
  echo "Working tree has uncommitted changes. Commit or stash before syncing." >&2
  exit 1
fi

mapfile -t INCLUDE_PATHS < <(grep -Ev '^\s*(#|$)' "$INCLUDE_FILE")
MISSING_PATHS=()
for rel in "${INCLUDE_PATHS[@]}"; do
  if [[ ! -e "$ROOT_DIR/$rel" ]]; then
    MISSING_PATHS+=("$rel")
  fi
done

if [[ ${#MISSING_PATHS[@]} -gt 0 ]]; then
  echo "The following include paths are missing from repository:" >&2
  printf '  - %s\n' "${MISSING_PATHS[@]}" >&2
  exit 1
fi

echo ">>> Preparing worktree for branch $BRANCH (base: $BASE_REF)"
if git worktree list | awk '{print $1}' | grep -Fx "$WORKTREE_DIR" >/dev/null 2>&1; then
  git worktree remove --force "$WORKTREE_DIR"
fi

if git show-ref --quiet "refs/heads/$BRANCH"; then
  git worktree add --force "$WORKTREE_DIR" "$BRANCH"
else
  git worktree add -B "$BRANCH" "$WORKTREE_DIR" "$BASE_REF"
fi

echo ">>> Copying whitelisted files"
rsync -av --delete --prune-empty-dirs --files-from="$INCLUDE_FILE" "$ROOT_DIR"/ "$WORKTREE_DIR"/

pushd "$WORKTREE_DIR" >/dev/null

SYNC_SOURCE_COMMIT="$(git -C "$ROOT_DIR" rev-parse HEAD)"
if ! git diff --quiet --ignore-submodules --exit-code; then
  git add -A
  git commit -m "[release] Sync windows artifacts from $SYNC_SOURCE_COMMIT"
  git push origin "$BRANCH"
  echo "Synced windows branch from $SYNC_SOURCE_COMMIT"
else
  echo "No changes detected for $BRANCH"
fi

popd >/dev/null
