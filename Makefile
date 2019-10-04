SHELL := /bin/bash

deploy:
	gcloud functions deploy \
		cloud-build-badge \
		--source . \
		--runtime python37 \
		--entry-point build_badge \
		--service-account cloud-build-badge@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com \
		--set-env-vars BADGES_BUCKET=${BADGES_BUCKET} \
		--trigger-topic=cloud-builds

unit:
	python -m pytest -W ignore::DeprecationWarning -v

integration:
	source tests/integration.sh && \
		run_test
