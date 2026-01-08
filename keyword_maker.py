import ollama
import re
import json
import pandas as pd

def create_prompt(keyword: str) -> str:
    """Create a prompt based on a keyword."""
    return f"Give keywords relative to the word:\n{keyword}"


def create_prompts(keywords: list[str]) -> list[str]:
    """Create of list of prompts based on a given list of keywords."""
    return [create_prompt(keyword) for keyword in keywords]


def ask_ollama(model_name: str, messages: list[dict[str, str]]) -> str:
    """Asks Ollama for a given prompt using a given model."""
    response = ollama.chat(model=model_name, messages=messages)
    content = response['message']['content']

    # Remove <think>...</think> block
    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

    return content


def get_keywords(response: str) -> list[str]:
    # Extract the json text from the response
    start_index = response.find('json') + len('json') 
    end_index = response.find('```', start_index)

    if start_index<end_index and end_index != -1 and start_index!=0:
        response = response[start_index:end_index].strip()

    # Transform the response to a list of keywords
    data = json.loads(response)

    if 'keywords' in data:
        return data['keywords']
    
    return []


def generate_keywords(prompts: list[str], meta_prompt: str, model_name: str = "deepseek-r1:8b") -> list[str]:
    """This generates keywords based on a list of prompts."""
    results = []
    for prompt in prompts:
        print(prompt)
        messages = [
            {"role": "system", "content": meta_prompt},
            {"role": "user", "content": prompt}
        ]
        response = ask_ollama(model_name=model_name, messages=messages)
        results += get_keywords(response)
    return results


def create_dataframe(keywords: list[str]) -> pd.DataFrame:
    """Create a single column DataFrame based on a list of keywords. Duplicates are removed."""
    # Create a DataFrame with a single column
    df = pd.DataFrame(keywords, columns=["Keywords"])

    # Convert column to lowercase and remove duplicates
    df["Keywords"] = df["Keywords"].str.lower()
    df = df.drop_duplicates()

    return df


def save_dataframe(dataframe: pd.DataFrame, path: str = "out/example.csv") -> None:
    """Save the given DataFrame as a Comma Separated Value (CSV) file."""
    # Save without the index column
    dataframe.to_csv(path, index=False)


input_keywords = [
    "digital twins",
    "Virtual Representation",
    "Cyber-Physical System",
    "Simulation Model",
    "Data Synchronization",
    "Real-Time Monitoring",
    "System Simulation",
    "Virtual Prototyping",
    "Internet of Things",
    "ISO 23247", # Digital Twin Framework Norm
    "Digital Twin Framework"
]
meta_prompt = "I'm working on a project where I need keywords that refer to digital twins. You give each keyword separately in a json format. Like this:\n ```json\n{ \n\"keywords\": [\n    \"digital twin\",\n    \"digital model\"\n  ]}\n```\n Give the maximum keywords possible. Give solely the json text code."
prompts = create_prompts(input_keywords)
model_name = "deepseek-r1:8b"

results = generate_keywords(prompts=prompts, meta_prompt=meta_prompt, model_name=model_name)
results_df = create_dataframe(results)
save_dataframe(results_df, "out/start_keywords2.csv")
