import os
import requests
import csv
import json

from datetime import datetime
from dateutil.relativedelta import relativedelta
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

def is_github_token_present() -> bool:
    """Verifies if the GITHUB_TOKEN variable is set."""
    print("Looking for the GITHUB_TOKEN environment variable.")
    try:
        os.environ["GITHUB_TOKEN"]
        print("GITHUB_TOKEN environment variable found!")
        return True
    except KeyError:
        print("Error: GITHUB_TOKEN is not set. Please add it as an environment variable.")
    return False


def get_github_token() -> str:
    """Get the GITHUB_TOKEN environment variable."""
    if is_github_token_present():
        return os.environ["GITHUB_TOKEN"]
    return ""


def create_client(github_token: str) -> Client:
    transport = AIOHTTPTransport(
        url="https://api.github.com/graphql",
        headers={"Authorization": f"bearer {github_token}"},
    )

    return Client(transport=transport)


async def get_repository_count(keyword: str, client: Client) -> int:
    """Runs a small query to get the respositoryCount value."""
    query = gql("""
        query getReposCount ($query: String!) {
            search(type:REPOSITORY, query:$query) {
                repositoryCount
            }
        }""")
    query.variable_values = {
        "query": keyword
    }
    async with client as session:
        dataFetched = False
        while not dataFetched:
            try:
                result = await session.execute(query)
                dataFetched = True
            except TimeoutError:
                print("TimeoutError: Attempting the query until data is fetched.")
    return result["search"]["repositoryCount"]


async def get_repositories_for_period(start_date: datetime, end_date: datetime, date_format: str, query, keyword: str, client: Client) -> list:
    allDataFetched = False
    start_string = start_date.strftime(date_format)
    end_string = end_date.strftime(date_format)

    repositories = []
    cursor = ""
    n = 1
    
    while not allDataFetched:
        # Set the variables
        query.variable_values = {
            "query": f"{keyword} sort:updated-asc pushed:{start_string}..{end_string}",
            "cursor": cursor
        }

        # Get the data
        async with client as session:
            dataFetched = False
            while not dataFetched:
                try:
                    result = await session.execute(query)
                    dataFetched = True
                except TimeoutError:
                    print("TimeoutError: Attempting the query until data is fetched.")

        results = result["search"]["edges"]
        # Get the number of repos
        count = result["search"]["repositoryCount"]
        print(f"{count} repositories found for the given period{f" {n}/{count//100+1}" if count > 100 else ""}")

        # Add the repos to the final list of repos
        for repository in results:
            repositories.append(repository["node"])

        # If more than 100 repos, set the cursor at the latest repo in the results, else, we end the loop
        if n <= count // 100:
            cursor = results[-1]["cursor"]
            n += 1
        else:
            allDataFetched = True

    return repositories



async def search_github_repositories(keyword: str, github_token: str) -> list:
    print(f"Searching GitHub projects corresponding to: {keyword}")

    client = create_client(github_token=github_token)
    repository_count = await get_repository_count(keyword=keyword, client=client)

    print(f"{repository_count} repositories found. Fetching the data...")

    query = gql("""
        query getRepos ($query: String!, $cursor: String = "") {
            search(type:REPOSITORY, query:$query, first:100, after:$cursor) {
                repositoryCount
                edges {
                    cursor
                    node {
                        ... on Repository {
                            name
                            description
                            url
                            stargazerCount
                            forkCount
                            languages(first:10,orderBy:{field:SIZE,direction:DESC}) {
                                edges {
                                    node {
                                        name
                                    }
                                    size
                                }
                            }
                        }
                    }
                }
            }
        }""")
    
    repositories: list = []
    date_format = "%Y-%m-%d"
    today = datetime.now()
    start_date = datetime.strptime("2014-01-01", date_format)
    end_date = start_date + relativedelta(day=31)

    while start_date < today:
        start_string = start_date.strftime(date_format)
        end_string = end_date.strftime(date_format)
        print(f"Requesting repositories from {start_string} to {end_string}")

        results_from_period = await get_repositories_for_period(start_date=start_date, end_date=end_date, date_format=date_format, query=query, keyword=keyword, client=client)

        # Add the repos to the final list of repos
        repositories.extend(results_from_period)

        # Increment the dates
        start_date += relativedelta(months=1)
        end_date = start_date + relativedelta(day=31)

    # TEMP: save to file
    with open(f"out/digital_twin_repos_github_{today.strftime("%Y%m%d_%H%M%S")}.csv", 'w', encoding='utf-8') as file:
        json.dump(repositories, file, indent=4)
    
    return repositories

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

def save_to_csv(repositories, filename="digital_twin_repos_github", github_token: str=""):
    now = datetime.now().strftime("%Y%m%d")
    with open(f"out/{filename}_{now}.csv", mode='w', newline='', encoding='utf-8') as file:
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
