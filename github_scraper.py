import os
import requests
import time
import csv

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

def is_github_token_present() -> bool:
    """Verifies if the GITHUB_TOKEN variable is set."""
    try:
        os.environ["GITHUB_TOKEN"]
        print("GITHUB_TOKEN found")
        return True
    except KeyError:
        print("Error: GITHUB_TOKEN is not set. Please add it as an environment variable.")
    return False


def get_github_token() -> str:
    """Get the GITHUB_TOKEN environment variable."""
    if is_github_token_present():
        return os.environ["GITHUB_TOKEN"]
    return ""


def search_github_repositories(keyword: str, github_token: str, max_results: int = 500, per_page: int = 100, start_page: int = 1, sort_by: str = "stars") -> list:
    repositories: list = []

    transport = AIOHTTPTransport(
        url="https://api.github.com/graphql",
        headers={"Authorization": f"bearer {github_token}"}
    )
    client = Client(transport=transport)

    headers = {
        "Authorization": f"bearer {github_token}"
    }

    query = f"""
        query {{
            search(type:REPOSITORY, query:"{keyword}", first:100) {{
                repositoryCount
                edges {{
                    node {{
                        ... on Repository {{
                            name
                            description
                            url
                            stargazerCount
                            forkCount
                            languages(first:10,orderBy:{{field:SIZE,direction:DESC}}) {{
                                edges {{
                                    node {{
                                        name
                                    }}
                                size
                                cursor
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
    """

    while len(repositories) < max_results:
        url = "https://api.github.com/graphql"
        response = requests.post(url, json={"query": query}, headers=headers)
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            print("Error: Empty or badly formatted response received from GitHub API")
            break

        if response.status_code != 200:
            print(f"Error : {response.status_code} - {data.get('message')}")
            break

        repositories.extend(data['items'])

        if len(data['items']) < per_page:
            break

        page += 1
        time.sleep(1)  # Pause to avoid API limitations

    return repositories[:max_results]

def get_repository_details(repo, github_token: str):
    repo_url = repo['url']
    contributors_url = repo_url + "/contributors"
    commits_url = repo_url + "/commits"
    headers = {"Authorization": f"token {github_token}"}

    try:
        contributors_response = requests.get(contributors_url, headers=headers)
        commits_response = requests.get(commits_url, headers=headers)
        contributors_count = len(contributors_response.json()) if contributors_response.status_code == 200 else 0
        commits_count = len(commits_response.json()) if commits_response.status_code == 200 else 0
    except requests.exceptions.JSONDecodeError:
        contributors_count = 0
        commits_count = 0

    open_issues_count = repo['open_issues_count']

    return contributors_count, commits_count, open_issues_count

def save_to_csv(repositories, filename="digital_twin_repos_github.csv", github_token: str=""):
    with open("out/" + filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Stars", "Forks", "Language", "Description", "URL", "Contributors", "Commits", "Open Issues"])

        for repo in repositories:
            contributors, commits, open_issues = get_repository_details(repo, github_token=github_token)
            writer.writerow([
                repo['name'],
                repo['stargazers_count'],
                repo['forks_count'],
                repo['language'],
                repo['description'],
                repo['html_url'],
                contributors,
                commits,
                open_issues
            ])
