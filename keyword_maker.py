import ollama
import re
import json
import pandas as pd

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

def create_prompt(keyword):
    prompt="Give keywords relative to the word:\n"
    prompt+= keyword
    return prompt

print(meta_prompt)

prompts = [create_prompt(keyword) for keyword in input_keywords]

print(prompts[0])

model_name = "deepseek-r1:8b"

result_keywords = []

for prompt in prompts:
    # Get response from Ollama
    response = ollama.chat(model=model_name, messages=[
        {"role": "system", "content": meta_prompt},
        {"role": "user", "content": prompt}])
    print(response)
    ollama_response = response['message']['content']
    print(ollama_response)

    # Remove <think>...</think> block
    ollama_response = re.sub(r"<think>.*?</think>", "", ollama_response, flags=re.DOTALL).strip()

    # Extract the json text from the response
    start_index = ollama_response.find('json') + len('json') 
    end_index = ollama_response.find('```', start_index)

    if start_index<end_index and end_index != -1 and start_index!=0:
        
        json_text = ollama_response[start_index:end_index].strip()

        # Transform the response to a list of keywords
        data = json.loads(json_text)

        if 'keywords' in data:
            output_keywords = data['keywords']

            result_keywords+=output_keywords
            
len(result_keywords)

df = pd.DataFrame(result_keywords, columns=["Keywords"])  # Create a DataFrame with a single column

# Convert column to lowercase and remove duplicates
df["Keywords"] = df["Keywords"].str.lower()
df = df.drop_duplicates()

df.to_csv("out/start keywords.csv", index=False)  # Save without the index column