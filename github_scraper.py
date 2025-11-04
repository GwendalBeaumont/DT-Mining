import os
import requests
import time
import csv

GITHUB_TOKEN = ""
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

def is_github_token_present():
    """Verifies if the GITHUB_TOKEN variable is set.
    """
    try:
        GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
        print("GITHUB_TOKEN found:", "*" * (len(GITHUB_TOKEN) - 5) + GITHUB_TOKEN[-5:])
    except KeyError:
        print("Error: GITHUB_TOKEN is not set. Please add it as an environment variable.")


def search_github_repositories(query: str, max_results: int = 500, per_page: int = 100, sort_by: str = "stars") -> list:
    repositories: list = []
    page = 1

    while len(repositories) < max_results:
        url = f"https://api.github.com/search/repositories?q={query}&per_page={per_page}&page={page}&sort={sort_by}"
        response = requests.get(url, headers=HEADERS)
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

def get_repository_details(repo):
    repo_url = repo['url']
    contributors_url = repo_url + "/contributors"
    commits_url = repo_url + "/commits"

    try:
        contributors_response = requests.get(contributors_url, headers=HEADERS)
        commits_response = requests.get(commits_url, headers=HEADERS)
        contributors_count = len(contributors_response.json()) if contributors_response.status_code == 200 else 0
        commits_count = len(commits_response.json()) if commits_response.status_code == 200 else 0
    except requests.exceptions.JSONDecodeError:
        contributors_count = 0
        commits_count = 0

    open_issues_count = repo['open_issues_count']

    return contributors_count, commits_count, open_issues_count

def save_to_csv(repositories, filename="digital_twin_repos_gitHub.csv"):
    with open("out/" + filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Stars", "Forks", "Language", "Description", "URL", "Contributors", "Commits", "Open Issues"])

        for repo in repositories:
            contributors, commits, open_issues = get_repository_details(repo)
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
