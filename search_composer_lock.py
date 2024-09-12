import os
import re

# Define the directory where your repos are located
base_directory = os.path.expanduser('~/Sites/WECMS')

# Define the local repository directories you want to search for
local_repositories = [
    'Drupal-CMSGov',
    'Drupal-MedicareGov',
    'healthcare',
    'medicaid',
    'payments',
    'pfs-data',
    'qic-data',
]

# Define the keywords or modules to search for
keywords = [
    'freelinking',
    'content_entity_clone',
    'paragraphs_table',
    'social',
]

def search_composer_lock_in_repo(repo_path):
    # Path to composer.lock file
    composer_lock_path = os.path.join(repo_path, 'composer.lock')

    # Check if the composer.lock file exists
    if not os.path.isfile(composer_lock_path):
        print(f"No composer.lock found in {repo_path}")
        return

    # Read the composer.lock file
    with open(composer_lock_path, 'r') as file:
        contents = file.read()

    print(f"\nSearching in {composer_lock_path}:")

    # Search for local repositories
    print("Local Repositories found:")
    for repo in local_repositories:
        if re.search(re.escape(repo), contents):
            print(f"Found local repository: {repo}")

    # Search for keywords
    print("\nKeywords found:")
    for keyword in keywords:
        matches = re.findall(r'\b' + re.escape(keyword) + r'\b', contents, re.IGNORECASE)
        if matches:
            print(f"Found keyword: {keyword} ({len(matches)} times)")

def search_all_repos(base_directory):
    # Iterate through all directories in the base directory
    for repo_name in os.listdir(base_directory):
        repo_path = os.path.join(base_directory, repo_name)
        if os.path.isdir(repo_path):
            search_composer_lock_in_repo(repo_path)

if __name__ == "__main__":
    # Search through all repositories in the base directory
    search_all_repos(base_directory)
