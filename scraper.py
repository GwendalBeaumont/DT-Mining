import requests
import pandas as pd
import time
from tqdm import tqdm

outputfile = 'out/repos_metadata3.csv'

# Create a session once at the beginning
session = requests.Session()
session.headers.update({"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"})


def get_rate_limit():
    """Fetches both search and core rate limits from GitHub API."""
    url = "https://api.github.com/rate_limit"
    response = session.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return {
            "core_remaining": data['resources']['core']['remaining'],
            "core_reset": data['resources']['core']['reset'],
            "search_remaining": data['resources']['search']['remaining'],
            "search_reset": data['resources']['search']['reset']
        }
    
    print("Warning: Unable to fetch rate limit status.")
    return None
    
def check_requests_limit(limit_type="search"):
    """
    Ensures API requests stay within GitHub's rate limits.
    
    Args:
        limit_type (str): "search" for search-related requests, "core" for general API requests.
    """
    for _ in range(5):  # Retry up to 5 times before failing
        rate_limits = get_rate_limit()
        if rate_limits is None:
            print("Error: Unable to fetch rate limit. Retrying...")
            time.sleep(5)
            continue
        
        remaining = rate_limits[f"{limit_type}_remaining"]
        reset_time = rate_limits[f"{limit_type}_reset"]

        if remaining > 0:
            return  # Safe to proceed
        
        wait_time = reset_time - time.time() + 1
        if wait_time > 0:
            print(f"{limit_type.capitalize()} rate limit exceeded. Waiting {int(wait_time)} seconds...")
            time.sleep(wait_time)

    raise RuntimeError(f"Failed to check {limit_type} rate limit after multiple attempts.")


def get_repository_details(repo):
    repo_url = repo['url']
    contributors_url = repo_url + "/contributors"
    commits_url = repo_url + "/commits"

    try:
        check_requests_limit("core")
        contributors_response = session.get(contributors_url)
        commits_response = session.get(commits_url)
        contributors_count = len(contributors_response.json()) if contributors_response.status_code == 200 else 0
        commits_count = len(commits_response.json()) if commits_response.status_code == 200 else 0
    except requests.exceptions.JSONDecodeError:
        contributors_count = 0
        commits_count = 0

    open_issues_count = repo['open_issues_count']

    return contributors_count, commits_count, open_issues_count

def search_github_repos(keyword, per_page=10, pages=1):
    all_metadata = []
    
    for page in range(1, pages + 1):
        
        check_requests_limit("search")
        
        url = f"https://api.github.com/search/repositories?q={keyword}&per_page={per_page}&page={page}"
        #headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
        
        response = session.get(url)
        
        if response.status_code == 200:
            data = response.json()
            repos = data.get("items", [])
            
            for repo in repos:

                contributors_count, commits_count, open_issues_count = get_repository_details(repo)

                repo_data = {
                    "name": repo["name"],
                    "owner": repo["owner"]["login"],
                    "stars": repo["stargazers_count"],
                    "forks": repo["forks_count"],
                    "description": repo["description"],
                    "url": repo["html_url"],
                    "open_issues":repo["open_issues_count"],
                    "language":repo["language"],
                    "Contributors":contributors_count,
                    "Commits":commits_count, 
                    "Open Issues":open_issues_count
                }
                all_metadata.append(repo_data)
        else:
            print(f"Error: Unable to fetch data for page {page} (Status code: {response.status_code})")
            break
    
    return pd.DataFrame(all_metadata) if all_metadata else None

def search_multiple_keywords(keywords, per_page=10, pages=1, save_path=outputfile):
    
    # Try to load existing data if the file exists
    try:
        existing_df = pd.read_csv(save_path,sep=';',)
    except FileNotFoundError:
        existing_df = pd.DataFrame()

    for keyword in tqdm(keywords):
        df = search_github_repos(keyword, per_page, pages)
        if df is not None:
            df["search_keyword"] = keyword  # Add keyword column to track origin
            
            # Combine with existing data if available
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            combined_df.drop_duplicates(subset=["url"], inplace=True)
            
            # Save the updated DataFrame
            combined_df.to_csv(save_path, sep=';', index=False)
            existing_df = combined_df  # Update existing_df for next iterations

    return existing_df

# Keywords are loaded from the CSV database below.

keywords_DB_df = pd.read_csv("out/keywords_database.csv")

keywords = keywords_DB_df["Keywords"].tolist()

search_multiple_keywords(keywords, per_page=10, pages=100)