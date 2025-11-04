class Repository:
    name: str
    description: str
    url: str
    forks: int
    stars: int
    language: str
    contributors: list[str]
    commits: list
    open_issues: list
    
    
    def __init__(self, name, description, url, forks, stars, language, contributors, commits, open_issues):
        name = name
        description = description
        url = url
        forks = forks
        stars = stars
        language = language
        contributors = contributors
        commits = commits
        open_issues = open_issues
    