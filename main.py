import asyncio

from github_scraper import get_github_token, search_github_repositories, save_to_csv

async def main():
    keyword = "digital twin"
    repos = await search_github_repositories(keyword=keyword, github_token=get_github_token())
    #save_to_csv(repos)

    
if __name__ == "__main__":
    asyncio.run(main())