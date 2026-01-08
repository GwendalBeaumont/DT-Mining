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
        self.name = name
        self.description = description
        self.url = url
        self.forks = forks
        self.stars = stars
        self.language = language
        self.contributors = contributors
        self.commits = commits
        self.open_issues = open_issues
    