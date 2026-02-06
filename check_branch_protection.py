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

def get_branch_protection(owner, repo, branch, token):
    """Get current branch protection rules"""
    url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}/protection"
    
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
        if e.code == 404:
            return None
        error_data = e.read().decode()
        print(f"HTTP Error {e.code}: {error_data}")
        return None

def set_branch_protection(owner, repo, branch, token):
    """Configure branch protection rules"""
    url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}/protection"
    
    protection_config = {
        "required_status_checks": None,
        "enforce_admins": True,
        "required_pull_request_reviews": {
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": False,
            "required_approving_review_count": 1
        },
        "restrictions": None,
        "allow_force_pushes": False,
        "allow_deletions": False,
        "required_linear_history": False,
        "allow_auto_merge": False
    }
    
    data = json.dumps(protection_config).encode('utf-8')
    
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

def print_protection_status(protection):
    """Print human-readable protection status"""
    if not protection:
        print("Branch protection: NOT CONFIGURED")
        return False
    
    print("\n=== Branch Protection Status ===\n")
    
    status_items = {
        "Enforce on Admins": protection.get("enforce_admins", False),
        "Allow Force Pushes": protection.get("allow_force_pushes", False),
        "Allow Deletions": protection.get("allow_deletions", False),
        "Require Pull Request Reviews": bool(protection.get("required_pull_request_reviews")),
    }
    
    pr_reviews = protection.get("required_pull_request_reviews", {})
    if pr_reviews:
        approvals_required = pr_reviews.get("required_approving_review_count", 0)
        status_items[f"Minimum Approvals Required"] = approvals_required
        status_items["Dismiss Stale Reviews"] = pr_reviews.get("dismiss_stale_reviews", False)
    
    all_good = True
    for key, value in status_items.items():
        if key.startswith("Allow"):
            check = "OK" if not value else "ISSUE"
            if value:
                all_good = False
        elif key == "Enforce on Admins":
            check = "OK" if value else "ISSUE"
            if not value:
                all_good = False
        elif "Approvals" in key:
            check = "OK" if value >= 1 else "ISSUE"
            if value < 1:
                all_good = False
        else:
            check = "OK" if value else "ISSUE"
            if not value:
                all_good = False
        
        symbol = "[OK]" if check == "OK" else "[!]"
        print(f"{symbol} {key}: {value}")
    
    print()
    return all_good

if __name__ == "__main__":
    token = get_git_credentials()
    if not token:
        print("Error: Could not retrieve GitHub token")
        sys.exit(1)
    
    owner = "jewandji"
    repo = "gestion-etudiants"
    branch = "main"
    
    print(f"Checking branch protection for {owner}/{repo}:{branch}...\n")
    
    current_protection = get_branch_protection(owner, repo, branch, token)
    is_protected = print_protection_status(current_protection)
    
    if not is_protected:
        print("Configuring branch protection rules...\n")
        result = set_branch_protection(owner, repo, branch, token)
        
        if result:
            print("Branch protection configured successfully:")
            print_protection_status(result)
            print("SUCCESS: Branch 'main' is now protected")
        else:
            print("ERROR: Failed to configure branch protection")
            sys.exit(1)
    else:
        print("SUCCESS: Branch 'main' is already properly protected")
