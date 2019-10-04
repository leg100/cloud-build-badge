import base64
import json
import pytest

import main


def event(func):
    def wrapper():
        data = func()
        encoded = base64.b64encode(json.dumps(data).encode())
        return {'data': encoded}

    return wrapper


@pytest.fixture
@event
def cloud_source_repo():
    return {
        "status": "WORKING",
        "source": {
            "repoSource": {
                "projectId": "louis-garman-ci",
                "repoName": "webapp",
                "branchName": "master"
            }
        }
    }


@pytest.fixture
@event
def mirrored_repo():
    return {
        "status": "SUCCESS",
        "source": {
            "repoSource": {
                "projectId": "louis-garman-ci",
                "repoName": "bitbucket_garman_webapp",
                "branchName": "feature/fish"
            }
        }
    }


@pytest.fixture
@event
def github_app():
    return {
        "status": "SUCCESS",
        "substitutions": {
              "REPO_NAME": "webapp",
              "BRANCH_NAME": "feature/fish"
        }
    }


@pytest.fixture
def badges_bucket(monkeypatch):
    monkeypatch.setenv('BADGES_BUCKET', 'my-badges-bucket')


@pytest.fixture
def custom_template_path(monkeypatch):
    monkeypatch.setenv('TEMPLATE_PATH', 'builds/${repo}-${branch}.svg')


@pytest.fixture
def patches(mocker):
    mocker.patch('main.copy_badge')


def test_mirrored_repo(mirrored_repo, badges_bucket, patches):
    main.build_badge(mirrored_repo, None)

    main.copy_badge.assert_called_once_with(
            'my-badges-bucket',
            'badges/success.svg',
            'builds/webapp/branches/feature/fish.svg')


def test_github_app(github_app, badges_bucket, patches):
    main.build_badge(github_app, None)

    main.copy_badge.assert_called_once_with(
            'my-badges-bucket',
            'badges/success.svg',
            'builds/webapp/branches/feature/fish.svg')


def test_cloud_source_repo(cloud_source_repo, badges_bucket, patches):
    main.build_badge(cloud_source_repo, None)

    main.copy_badge.assert_called_once_with(
            'my-badges-bucket',
            'badges/working.svg',
            'builds/webapp/branches/master.svg')


def test_custom_template_path(cloud_source_repo, badges_bucket,
        custom_template_path, patches):

    main.build_badge(cloud_source_repo, None)

    main.copy_badge.assert_called_once_with(
            'my-badges-bucket',
            'badges/working.svg',
            'builds/webapp-master.svg')
