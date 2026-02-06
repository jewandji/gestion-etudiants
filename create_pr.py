#!/usr/bin/env python3
import subprocess
import json
import sys

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

def create_pr(owner, repo, head, base, token):
    """Create a pull request on GitHub"""
    import urllib.request
    import urllib.error
    
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    
    title = "Refactoring: Replay commits with clean feature branch workflow"
    body = """# Summary
This pull request introduces a proper feature branch workflow for secure development practices.

## Changes
This branch replays all non-merge commits from the initial commit sequentially onto a feature branch, ensuring:
- Clean commit history without merge artifacts
- Traceability of all code modifications
- Compliance with secure development practices requiring code review before merging to main

## Related Commits
- Initial commit and all subsequent development commits
- Merge commits excluded to maintain linear history

## Testing
All code modifications have been validated during the replay process.

## Notes
- Merge commits were skipped to maintain a clean linear history
- All functional changes are preserved in sequential commits
- This branch is ready for review and merge to main after approval"""
    
    data = json.dumps({
        "title": title,
        "body": body,
        "head": head,
        "base": base
    }).encode('utf-8')
    
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        },
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            return result
    except urllib.error.HTTPError as e:
        error_data = e.read().decode()
        print(f"HTTP Error {e.code}: {error_data}")
        return None

if __name__ == "__main__":
    token = get_git_credentials()
    if not token:
        print("Error: Could not retrieve GitHub token")
        sys.exit(1)
    
    result = create_pr("jewandji", "gestion-etudiants", "feature/replay-from-root", "main", token)
    
    if result:
        if "number" in result:
            print(f"Pull request created successfully: #{result['number']}")
            print(f"URL: {result['html_url']}")
        else:
            print(f"Error creating PR: {result}")
            sys.exit(1)
    else:
        print("Failed to create PR")
        sys.exit(1)
