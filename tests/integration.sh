event() {
  echo {} | \
  jq -r \
  --arg status $1 \
  '.status = $status | .substitutions.REPO_NAME = "test-repo" | @base64 | {"data": . }'
}

run_test() {
  for status in cancelled failure internal_error queued status_unknown success timeout working
  do
    gcloud functions call cloud-build-badge --data "$(event $status)"
    gsutil cp gs://${BADGES_BUCKET}/builds/test-repo.svg - | \
      xq -e \
      --arg status $status \
      '.svg.g[] | select(.text) | .text[] | select(."#text" == $status)'
  done
}
