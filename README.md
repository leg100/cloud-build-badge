# cloud-build-badge

A Cloud Function that generates Cloud Build badges.

## Installation

### Upload Badges

You'll need a Cloud Storage bucket in which to store the badges (it's a good idea to prefix the name of the bucket with your Cloud project name, to ensure it's unique):

```bash
gsutil mb gs://${GOOGLE_CLOUD_PROJECT}-badges/
```

Next enable anyone on the internet to be able to read the badges (necessary if you're going to embed them in your README).

```bash
gsutil defacl ch -u AllUsers:R gs://${GOOGLE_CLOUD_PROJECT}-badges/
```

Then upload the pre-generated badges in `./badges` to the bucket. Ensure they go into a directory on the bucket named `badges/`. Disable caching to ensure the latest updates to a badge are visible to end-users.

```bash
gsutil -m -h "Cache-Control:no-cache,max-age=0" \
  cp ./badges/*.svg gs://${GOOGLE_CLOUD_PROJECT}-badges/badges/
```

Note: the `-m` flag uploads the badges in parallel, speeding it up.

### Configure IAM

Create a new service account for use by the Cloud Function:

```bash
gcloud iam service-accounts create cloud-build-badge
```

Grant permissions to read and write to the bucket:

```bash
gsutil iam ch serviceAccount:cloud-build-badge@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com:legacyBucketReader,legacyObjectReader,legacyBucketWriter gs://${GOOGLE_CLOUD_PROJECT}-badges/
```

## Deploy

Deploy the function:

```bash
gcloud functions deploy cloud-build-badge \
    --source . \
    --runtime python37 \
    --entry-point build_badge \
    --service-account cloud-build-badge@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com \
    --trigger-topic=cloud-builds \
    --set-env-vars BADGES_BUCKET=${GOOGLE_CLOUD_PROJECT}-badges
```

## Test

There is a `make` task for running integration tests against the deployed function:

```bash
make integration
```

Ensure the following environment variables are set first:

* `BADGES_BUCKET`: the name of the bucket containing the badges

You'll also need to install [jq](https://stedolan.github.io/jq/) and [xq](https://github.com/jeffbr13/xq).
