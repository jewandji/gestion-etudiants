#!/usr/bin/env python3
import subprocess
import json
import sys
import urllib.request
import urllib.error

def get_git_credentials():
    """Get GitHub token from git credentials"""
    try:
        result = subprocess.run(
            ['git', 'credential', 'fill'],
            input=b'protocol=https\nhost=github.com\n\n',
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            output = result.stdout.decode()
            for line in output.split('\n'):
                if line.startswith('password='):
                    return line.split('=', 1)[1]
    except Exception as e:
        print(f"Could not retrieve git credentials: {e}")
    return None

def merge_pull_request(owner, repo, pr_number, token):
    """Merge a pull request"""
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/merge"
    
    merge_data = {
        "commit_title": "Merge: Replay commits with clean feature branch workflow",
        "commit_message": "Merged feature/replay-from-root into main with proper feature branch workflow and contribution guidelines.",
        "merge_method": "squash"
    }
    
    data = json.dumps(merge_data).encode('utf-8')
    
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        },
        method='PUT'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        error_data = e.read().decode()
        print(f"HTTP Error {e.code}: {error_data}")
        return None

def get_pr_info(owner, repo, pr_number, token):
    """Get PR information"""
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    
    req = urllib.request.Request(
        url,
        headers={
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        },
        method='GET'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        error_data = e.read().decode()
        print(f"HTTP Error {e.code}: {error_data}")
        return None

if __name__ == "__main__":
    token = get_git_credentials()
    if not token:
        print("Error: Could not retrieve GitHub token")
        sys.exit(1)
    
    owner = "jewandji"
    repo = "gestion-etudiants"
    pr_number = 1
    
    print(f"Checking PR #{pr_number}...\n")
    
    pr_info = get_pr_info(owner, repo, pr_number, token)
    if not pr_info:
        print("ERROR: Could not fetch PR information")
        sys.exit(1)
    
    print(f"PR Title: {pr_info['title']}")
    print(f"Status: {pr_info['state']}")
    print(f"Mergeable: {pr_info.get('mergeable', 'Unknown')}")
    print(f"Author: {pr_info['user']['login']}")
    print()
    
    if pr_info['state'] != 'open':
        print(f"ERROR: PR is {pr_info['state']}, not open")
        sys.exit(1)
    
    print("Merging PR #1 into main...")
    print()
    
    result = merge_pull_request(owner, repo, pr_number, token)
    
    if result:
        if 'message' in result and 'merged' in result['message']:
            print(f"SUCCESS: PR merged")
            print(f"Message: {result['message']}")
        else:
            print(f"Merge result: {result}")
    else:
        print("ERROR: Failed to merge PR")
        sys.exit(1)
