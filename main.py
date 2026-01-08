import asyncio
import json

from datetime import datetime
from github_scraper import get_github_token, search_github_repositories, get_latest_hash

async def main():
    keyword = "digital twin"
    github_token = get_github_token()
    repos = await search_github_repositories(keyword=keyword, github_token=github_token)

    n = len(repos)
    for i, repository in enumerate(repos):
        print(f"Getting sha for repository {i}/{n}")
        owner = repository["owner"]["login"]
        repo_name = repository["name"]
        sha = get_latest_hash(owner=owner, repo_name=repo_name, github_token=github_token)

        repository["latest_commit"] = sha
        repository["link_to_latest_commit"] = f"https://github.com/{owner}/{repo_name}/tree/{sha}"

    with open(f"out/digital_twin_repos_github_with_sha_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json", 'w', encoding='utf-8') as file:
        json.dump(repos, file, indent=4)

    
if __name__ == "__main__":
    asyncio.run(main())