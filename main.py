from github_scraper import get_github_token, search_github_repositories, save_to_csv
from software_heritage_scraper import search_projects_by_metadata
import pandas as pd

def main():
    KEYWORD = "digital twin"
    MAX_RESULTS = 2000
    PER_PAGE = 100
    
    print(f"Search GitHub projects for : {KEYWORD}")
    repos = search_github_repositories(keyword=KEYWORD, github_token=get_github_token(), max_results=MAX_RESULTS, per_page=PER_PAGE, sort_by="stars")
    print(f"{len(repos)} projects found.")
    save_to_csv(repos)
    print("The results were saved in 'digital_twin_repos_gitHub.csv'")
    
    print(f"Search Software Heritage projects for : {KEYWORD}")
    projects_metadata = search_projects_by_metadata(query=KEYWORD, max_results=MAX_RESULTS)
    print(f"{len(projects_metadata)} projects found.")
    df = pd.DataFrame(projects_metadata)
    file_path = "out/digital_twin_repos_softwareHeritage.csv"
    df.to_csv(file_path, index=False)
    print("The results were saved in 'digital_twin_repos_softwareHeritage.csv'")
    
if __name__ == "__main__":
    main()