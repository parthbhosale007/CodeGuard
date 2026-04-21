import requests

def fetch_repo_code(repo_url):
    # Extract owner & repo
    parts = repo_url.replace("https://github.com/", "").split("/")
    owner = parts[0]
    repo = parts[1]

    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"

    files = requests.get(api_url).json()

    code = ""

    for file in files:
        if file["type"] == "file":
            if file["name"].endswith((".py", ".js", ".cpp")):
                raw = requests.get(file["download_url"]).text
                code += f"\n\nFile: {file['name']}\n{raw}"

    return code