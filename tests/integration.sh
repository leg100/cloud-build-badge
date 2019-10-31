set -e

event() {
  echo {} | \
  jq -r \
  --arg status $1 \
  '.status = $status | .substitutions.REPO_NAME = "test-repo" | .substitutions.BRANCH_NAME = "master" | @base64 | {"data": . }'
}

run_test() {
  for status in cancelled failure internal_error queued status_unknown success timeout working
  do
    echo testing build status \"$status\"
    gcloud functions call cloud-build-badge --data "$(event $status)"
    curl -sS \
      https://storage.googleapis.com/${BADGES_BUCKET}/builds/test-repo/branches/master.svg | \
      xq -e \
      --arg status "${status//_/ }" \
      '.svg.g[] | select(.text) | .text[] | select(."#text" == $status)'
  done
}
