import requests
import time
from typing import Any

def search_projects_by_metadata(query: str, max_results: int, per_page: int=50) -> list:
    metarequest = 0
    projects = []
    base_url = "https://archive.softwareheritage.org/api/1/origin/metadata-search/"
    params: dict[str, Any] = {"fulltext": {query}, "per_page": per_page}
    next_page = base_url

    while next_page and metarequest < max_results:
        metarequest += 50
        response = requests.get(next_page, params=params)
        if response.status_code == 200:
            data = response.json()
            projects.extend(data)  # Ajouter les résultats
            # L'API de Software Heritage ne fournit pas toujours un lien "next"
            if len(data) < 50:
                break  # Plus de pages à récupérer

            time.sleep(1)

        else:
            print("Erreur lors de la requête:", response.status_code, response.text)
            break

    return projects