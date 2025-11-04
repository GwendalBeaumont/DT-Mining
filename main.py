from github_scraper import is_github_token_present, search_github_repositories, save_to_csv
from software_heritage_scraper import search_projects_by_metadata

def main():
    QUERY = "digital twin"
    MAX_RESULTS = 2000
    PER_PAGE = 100
    
    is_github_token_present()
    print(f"Search GitHub projects for : {QUERY}")
    repos = search_github_repositories(QUERY, MAX_RESULTS, PER_PAGE, sort_by="stars")
    print(f"{len(repos)} projects found.")
    save_to_csv(repos)
    print("The results were saved in 'digital_twin_repos_gitHub.csv'")
    
    print(f"Search Software Heritage projects for : {QUERY}")
    projects_metadata = search_projects_by_metadata()
    print(f"{len(projects_metadata)} projects found.")
    df = pd.DataFrame(projects_metadata)
    file_path = "digital_twin_repos_softwareHeritage.csv"
    df.to_csv(file_path, index=False)
    print("The results were saved in 'digital_twin_repos_softwareHeritage.csv'")
    
if __name__ == "__main__":
    main()