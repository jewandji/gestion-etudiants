$repo = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $repo
$p = git rev-list --reverse HEAD
$p = $p -split "`n" | Where-Object {$_ -ne ""}
$first = $p[0].Trim()
Write-Host "first=$first"

# ensure starting from main/master
git checkout main 2>$null
if ($LASTEXITCODE -ne 0) { git checkout master 2>$null }

# delete existing branch if present
git branch -D feature/replay-from-root 2>$null

# create branch from first commit
git checkout -b feature/replay-from-root $first
if ($LASTEXITCODE -ne 0) { Write-Host "Failed to create branch"; exit 1 }

# cherry-pick remaining commits, skipping merge commits
for ($i=1; $i -lt $p.Count; $i++) {
    $c = $p[$i].Trim()
    # detect number of parents
    $line = git rev-list --parents -n 1 $c
    $parts = $line -split ' '
    if ($parts.Length -gt 2) {
        Write-Host "Skipping merge commit $c"
        continue
    }
    Write-Host "Cherry-pick $c"
    git cherry-pick $c
    if ($LASTEXITCODE -ne 0) {
        Write-Host "CONFLICT_ON $c"
        exit 1
    }
}

Write-Host "All cherry-picks done (merge commits were skipped)"