$repo_owner = "jewandji"
$repo_name = "gestion-etudiants"
$head_branch = "feature/replay-from-root"
$base_branch = "main"

$title = "Refactoring: Replay commits with clean feature branch workflow"
$body = @"
# Summary
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
- This branch is ready for review and merge to main after approval
"@

$token = $env:GITHUB_TOKEN
if (-not $token) {
    Write-Host "Error: GITHUB_TOKEN environment variable not set"
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $token"
    "Accept" = "application/vnd.github.v3+json"
}

$body_obj = @{
    title = $title
    body = $body
    head = $head_branch
    base = $base_branch
} | ConvertTo-Json

$url = "https://api.github.com/repos/$repo_owner/$repo_name/pulls"

Write-Host "Creating PR from $head_branch to $base_branch..."
$response = Invoke-WebRequest -Uri $url -Method POST -Headers $headers -Body $body_obj -ContentType "application/json"

if ($response.StatusCode -eq 201) {
    $pr = $response.Content | ConvertFrom-Json
    Write-Host "PR created successfully: #$($pr.number)"
    Write-Host "URL: $($pr.html_url)"
} else {
    Write-Host "Failed to create PR: HTTP $($response.StatusCode)"
    Write-Host $response.Content
}
