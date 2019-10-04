#!/usr/bin/env bash

declare -A statuses
statuses['status_unknown']='inactive'
statuses['queued']='yellow'
statuses['working']='yellow'
statuses['success']='green'
statuses['failure']='critical'
statuses['cancelled']='red'
statuses['internal_error']='red'
statuses['timeout']='red'

mkdir -p badges

for status in "${!statuses[@]}"
do
  curl -sS \
    https://img.shields.io/badge/cloud_build-${status}-${statuses[$status]} \
    -o badges/$status.svg
done
