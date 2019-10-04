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
              "REPO_NAME": "webapp"
        }
    }


@pytest.fixture
def env_vars(monkeypatch):
    monkeypatch.setenv('BADGES_BUCKET', 'my-badges-bucket')


@pytest.fixture
def patches(mocker):
    mocker.patch('main.copy_badge')


def test_mirrored_repo(mirrored_repo, env_vars, patches):
    main.build_badge(mirrored_repo, None)

    main.copy_badge.assert_called_once_with(
            'my-badges-bucket',
            'badges/success.svg',
            'builds/webapp.svg')


def test_github_app(github_app, env_vars, patches):
    main.build_badge(github_app, None)

    main.copy_badge.assert_called_once_with(
            'my-badges-bucket',
            'badges/success.svg',
            'builds/webapp.svg')


def test_cloud_source_repo(cloud_source_repo, env_vars, patches):
    main.build_badge(cloud_source_repo, None)

    main.copy_badge.assert_called_once_with(
            'my-badges-bucket',
            'badges/working.svg',
            'builds/webapp.svg')
