from __future__ import annotations

import re

import requests
from typing_extensions import TypedDict


class GithubRepository(TypedDict):
    """https://docs.github.com/en/rest/repos/repos#get-a-repository"""

    name: str
    full_name: str
    description: str


def request_github_api(url: str) -> GithubRepository:
    match = re.match(".*github\\.com/([^/]*/[^/]*).*", url)
    if not match:
        raise Exception("Wrong github URL.")
    response = requests.get("https://api.github.com/repos/{}".format(match[1]))
    response.raise_for_status()
    return response.json()
