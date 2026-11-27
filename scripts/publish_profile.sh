#!/usr/bin/env bash
# Called only after default-branch dispatch/schedule; fixed output ref, fast-forward only.
set -euo pipefail
: "${RUNNER_TEMP:?}"
: "${PROFILE_SOURCE_REF:?}"
: "${PROFILE_DEFAULT_REF:?}"
if [[ "$PROFILE_SOURCE_REF" != "$PROFILE_DEFAULT_REF" ]]; then
  echo 'Publishing requires the default branch; preview artifacts are available instead.' >&2
  exit 1
fi
set +e
git ls-remote --exit-code --heads origin refs/heads/profile-assets > "$RUNNER_TEMP/profile-ref"
status=$?
set -e
if [[ "$status" -eq 0 ]]; then
  git fetch --depth=1 origin refs/heads/profile-assets
  git checkout -B profile-assets FETCH_HEAD
elif [[ "$status" -eq 2 ]]; then
  git switch --orphan profile-assets
else
  echo 'Cannot inspect output branch; refusing publication.' >&2
  exit "$status"
fi
# Only these generated paths may be committed. No existing output is deleted.
mkdir -p assets/profile
cp "$RUNNER_TEMP/profile/"*.svg assets/profile/
cp "$RUNNER_TEMP/profile/snapshot.json" "$RUNNER_TEMP/profile/snapshot.md" assets/profile/
git add -- assets/profile
if git diff --cached --quiet; then exit 0; fi
git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git commit -m 'Update public profile snapshot'
git push origin HEAD:refs/heads/profile-assets
