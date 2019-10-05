# cloud-build-badge

![cloud build status](https://storage.googleapis.com/louis-garman-ci-badges/builds/cloud-build-badge/branches/master.svg)

Embed a badge in your repository's `README` that reflects the status of the latest build in Cloud Build:

* ![](./badges/queued.svg)
* ![](./badges/working.svg)
* ![](./badges/success.svg)
* ![](./badges/timeout.svg)
* ![](./badges/cancelled.svg)
* ![](./badges/failure.svg)
* ![](./badges/internal_error.svg)
* ![](./badges/status_unknown.svg)

## Summary

Deploy a Google Cloud Function to auto-update your repository's badge. The function subscribes to events published by Cloud Build. The events contain information on the status of the progress and completion of a build. The function copies a badge reflecting that status to a known URL, which can be hard-coded in a repository `README`.

## Installation

It's assumed you've already integrated your repository with Cloud Build. If not, the instructinons for doing so are [here](https://cloud.google.com/cloud-build/docs/running-builds/automate-builds).

The function supports the following integrations:

* Cloud Build Github App
* Github (mirrored)
* Bitbucket Cloud (mirrored)
* Cloud Source Repositories


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

## Customise Path

You can customise the path in the bucket at which the badge gets published, using a template string. The default is:

`builds/${repo}/branches/${branch}.svg`

Where `${repo}` and `${branch}` refer to the name of the repository and branch that triggered the build. Only these two variables are available.

Set the environment variable `TEMPLATE_PATH` accordingly when deploying the function in the next step.

## Deploy

Deploy the function. Note you can customise the path at which the badge gets produced, using a template string,

```bash
gcloud functions deploy cloud-build-badge \
    --source . \
    --runtime python37 \
    --entry-point build_badge \
    --service-account cloud-build-badge@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com \
    --trigger-topic=cloud-builds \
    --set-env-vars BADGES_BUCKET=${GOOGLE_CLOUD_PROJECT}-badges,TEMPLATE_PATH='builds/${repo}/branches/${branch}.svg'
```

## Use

Embed the badge in your README, replacing `${repo}` and `${branch}` with the name of your repository and the branch you want to show the latest status for:

```
![Cloud Build](https://storage.googleapis.com/${GOOGLE_CLOUD_PROJECT}-badges/builds/${repo}/branches/${branch})
```

If you've customised the path using `TEMPLATE_PATH`, ensure it is reflected in the URL above.

Now trigger a build in Cloud Build (e.g. by pushing a commit, or directly via the Google Cloud console). You should see the badge update to reflect the build status.

## Test

There is a `make` task for running integration tests against the deployed function:

```bash
make integration
```

Ensure the following environment variables are set first:

* `BADGES_BUCKET`: the name of the bucket containing the badges

You'll also need to install [jq](https://stedolan.github.io/jq/) and [xq](https://github.com/jeffbr13/xq).
