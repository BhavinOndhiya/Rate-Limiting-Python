import requests
import time
import csv
import json
import base64
import os
from functools import wraps
from datetime import datetime
from itertools import cycle

# ---- Load Proxies ----
def load_proxies(proxy_file="proxy.json"):
    """Load proxies from JSON file and return a cycle iterator."""
    try:
        with open(proxy_file, 'r') as f:
            data = json.load(f)
            proxies_list = data.get("proxies", [])
            
        if not proxies_list:
            print("⚠️ No proxies found in proxy.json")
            return None
            
        # Filter only valid proxies
        valid_proxies = [p for p in proxies_list if p.get("valid", False)]
        
        if not valid_proxies:
            print("⚠️ No valid proxies found")
            return None
            
        print(f"✅ Loaded {len(valid_proxies)} valid proxies")
        
        # Format proxies for requests library
        formatted_proxies = []
        for proxy in valid_proxies:
            username = proxy["username"]
            password = proxy["password"]
            address = proxy["proxy_address"]
            port = proxy["ports"]["http"]
            
            proxy_url = f"http://{username}:{password}@{address}:{port}"
            formatted_proxies.append({
                "http": proxy_url,
                "https": proxy_url
            })
            
        return cycle(formatted_proxies)
    
    except FileNotFoundError:
        print("❌ proxy.json file not found!")
        return None
    except Exception as e:
        print(f"❌ Error loading proxies: {e}")
        return None


# Global proxy cycle
PROXY_CYCLE = load_proxies()
REQUEST_COUNT = {}  # Track requests per proxy


# ---- Rate Limiter Decorator ----
def rate_limit(max_calls, period):
    """Allow only `max_calls` every `period` seconds."""
    calls = []

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal calls
            now = time.time()
            calls = [t for t in calls if now - t < period]

            if len(calls) >= max_calls:
                wait = period - (now - calls[0])
                print(f"⏳ Rate limit hit. Waiting {wait:.2f} seconds...")
                time.sleep(wait)

            calls.append(time.time())
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ---- Get Next Proxy ----
def get_next_proxy():
    """Get the next proxy from the cycle."""
    if PROXY_CYCLE is None:
        return None
    
    proxy = next(PROXY_CYCLE)
    proxy_key = proxy["http"]
    
    # Track request count per proxy
    REQUEST_COUNT[proxy_key] = REQUEST_COUNT.get(proxy_key, 0) + 1
    
    # If this proxy has made 60 requests, skip to next one
    if REQUEST_COUNT[proxy_key] >= 60:
        print(f"🔄 Proxy reached 60 requests, rotating to next proxy...")
        REQUEST_COUNT[proxy_key] = 0  # Reset counter
        return get_next_proxy()
    
    return proxy


# ---- Helper: Fetch and Save README ----
def fetch_and_save_readme(username, repo_name):
    """Fetch README.md from a GitHub repo and save locally."""
    readme_url = f"https://api.github.com/repos/{username}/{repo_name}/readme"
    
    proxy = get_next_proxy()
    
    try:
        response = requests.get(readme_url, proxies=proxy, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if "content" in data:
                content = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
                os.makedirs(f"readmes/{username}", exist_ok=True)
                file_path = f"readmes/{username}/{repo_name}_README.md"
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"      📄 README saved → {file_path}")
                return True
        else:
            print(f"      ⚠️ No README found ({response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"      ❌ Error fetching README: {e}")
    
    return False


# ---- GitHub API Call ----
@rate_limit(max_calls=5, period=2)
def fetch_github_user(username):
    """Fetch user data and repos from GitHub"""
    user_url = f"https://api.github.com/users/{username}"
    repos_url = f"https://api.github.com/users/{username}/repos"

    proxy = get_next_proxy()
    
    try:
        user_response = requests.get(user_url, proxies=proxy, timeout=10)
        if user_response.status_code != 200:
            print(f"❌ Error fetching user {username}: {user_response.status_code}")
            return None

        user_data = user_response.json()
        print(f"\n👤 {user_data['login']} ({user_data.get('name', 'N/A')})")
        print(f"🏠 Location: {user_data.get('location', 'N/A')}")
        print(f"📦 Public repos: {user_data['public_repos']}")
        print(f"👥 Followers: {user_data['followers']} | Following: {user_data['following']}")
        print("📄 Fetching repositories and README files...\n")

        # Use a fresh proxy for repos request
        proxy = get_next_proxy()
        repos_response = requests.get(repos_url, proxies=proxy, timeout=10)
        if repos_response.status_code != 200:
            print(f"❌ Error fetching repos for {username}: {repos_response.status_code}")
            return None

        repos = repos_response.json()
        repo_info = []
        print("📂 Repositories:")
        if not repos:
            print("   (No public repos found)")
        else:
            for repo in repos[:5]:  # limit to 5 repos for demo
                print(f"   🔹 {repo['name']}")
                print(f"      ⭐ Stars: {repo['stargazers_count']}, 🍴 Forks: {repo['forks_count']}, 🧠 Language: {repo['language']}")
                print(f"      📜 {repo['description'] or 'No description provided.'}")
                has_readme = fetch_and_save_readme(username, repo["name"])
                print()

                repo_info.append({
                    "repo_name": repo["name"],
                    "stars": repo["stargazers_count"],
                    "forks": repo["forks_count"],
                    "language": repo["language"],
                    "description": repo["description"],
                    "readme_found": has_readme
                })

        return {
            "username": user_data["login"],
            "name": user_data.get("name"),
            "location": user_data.get("location"),
            "public_repos": user_data["public_repos"],
            "followers": user_data["followers"],
            "following": user_data["following"],
            "repos": repo_info
        }
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error for {username}: {e}")
        return None


# ---- Main Script ----
if __name__ == "__main__":
    usernames = ["torvalds", "BhavinOndhiya"]

    # Create a timestamped folder
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_dir = f"data/{timestamp}"
    os.makedirs(base_dir, exist_ok=True)

    all_data = []

    for user in usernames:
        data = fetch_github_user(user)
        if data:
            all_data.append(data)

            # Create user folder inside timestamped directory
            user_dir = os.path.join(base_dir, user)
            os.makedirs(user_dir, exist_ok=True)

            # Save individual JSON for each user
            user_json_path = os.path.join(user_dir, "details.json")
            with open(user_json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            print(f"💾 Saved user details → {user_json_path}")

    # ---- Save Combined CSV ----
    csv_path = os.path.join(base_dir, "github_repos.csv")
    with open(csv_path, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Username", "Repo Name", "Stars", "Forks", "Language", "Description", "README Found"])
        for user in all_data:
            for repo in user["repos"]:
                writer.writerow([
                    user["username"],
                    repo["repo_name"],
                    repo["stars"],
                    repo["forks"],
                    repo["language"],
                    repo["description"],
                    "Yes" if repo["readme_found"] else "No"
                ])

    print(f"\n💾 Combined CSV saved → {csv_path}")
    print(f"✅ All data saved inside folder: {base_dir}")
    print(f"\n📊 Proxy Usage Summary:")
    for proxy_url, count in REQUEST_COUNT.items():
        print(f"   • {proxy_url.split('@')[1]}: {count} requests")