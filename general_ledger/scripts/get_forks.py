import requests
from urllib.parse import urlparse

from git import Repo
from rich import inspect


def get_fork_urls_and_orgs(owner, repo):
    base_url = f"https://api.github.com/repos/{owner}/{repo}/forks"
    forks_info = []
    page = 1

    while True:
        response = requests.get(f"{base_url}?page={page}")
        if response.status_code == 200:
            forks = response.json()
            if not forks:
                break
            for fork in forks:
                url = fork['html_url']
                org = urlparse(url).path.split('/')[1]
                forks_info.append({'url': url, 'org': org})
            page += 1
        else:
            print(f"Error: {response.status_code}")
            break

    return forks_info

owner = "jseutter"
repo = "ofxparse"

gitrepo = Repo(".")

# inspect(repo)

#
forks_info = get_fork_urls_and_orgs(owner, repo)
for info in forks_info:
    print(f"Organization: {info['org']}, URL: {info['url']}")
    gitrepo.create_remote(info['org'].lower(), info['url'])
