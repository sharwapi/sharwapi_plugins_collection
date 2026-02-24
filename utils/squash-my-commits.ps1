##########################################################################
#
# This script will automatically bring the local git branch up to date
# with any changes in the main SharwAPI plugins collection repository
# and will then squash the local changes together in to a single commit.
#
# If the script fails to work, PRs for fixes are always welcome
# and you can always squash your commits manually.
#
# Usage:
#   .\utils\squash-my-commits.ps1 [options]
#
# use '-S' to sign the result with your GPG key
# use '--push' to also push automatically after squash
#
##########################################################################

param(
    [switch]$S,
    [switch]$Push,
    [switch]$Ssh,
    [switch]$Https,
    [switch]$Verify,
    [switch]$Help
)

if ($Help) {
    Write-Host "Usage: .\utils\squash-my-commits.ps1 [options]"
    Write-Host "Options:"
    Write-Host "  -S        sign the result with your GPG key (recommended)"
    Write-Host "  -Push     force push result to your fork after squash"
    Write-Host "  -Ssh      use SSH to fetch from upstream"
    Write-Host "  -Https    use HTTPS to fetch from upstream"
    Write-Host "  -Verify   check only (do not squash)"
    Write-Host "  -Help     display this message"
    Write-Host ""
    Write-Host "Environment variables:"
    Write-Host "  SHARWAPI_REG_URL   set the upstream repository URL directly"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\utils\squash-my-commits.ps1 -S -Push    # squash, sign, and push (recommended)"
    Write-Host "  .\utils\squash-my-commits.ps1 -Verify     # check if squash is needed"
    exit 0
}

##########################################################################
# Check for sharwapi remote, add if missing

$remotes = git remote -v 2>$null
if (-not ($remotes -match 'sharwapi')) {

    $regUrl = $env:SHARWAPI_REG_URL

    if (-not $regUrl) {
        $regProto = ''
        if ($Ssh)   { $regProto = 'ssh';   Write-Host 'Forcing use of SSH' }
        if ($Https) { $regProto = 'https'; Write-Host 'Forcing use of HTTPS' }

        if (-not $regProto) {
            if ($remotes -match 'https') {
                $regProto = 'https'
            } else {
                $regProto = 'ssh'
            }
        }

        switch ($regProto) {
            'ssh'   { $regUrl = 'git@github.com:sharwapi/sharwapi_plugins_collection.git' }
            'https' { $regUrl = 'https://github.com/sharwapi/sharwapi_plugins_collection.git' }
            default { Write-Error 'ERROR: Unknown protocol'; exit 1 }
        }
    }

    Write-Host "Adding sharwapi remote: $regUrl"
    git remote add sharwapi $regUrl
}

##########################################################################
# Fetch upstream main

Write-Host "Fetching sharwapi main"
git fetch sharwapi main
if ($LASTEXITCODE -ne 0) {
    Write-Error "ERROR: Failed to fetch upstream main branch"
    Write-Host "Hint: use -Ssh or -Https to force a specific protocol"
    Write-Host "Or set SHARWAPI_REG_URL environment variable to specify URL directly"
    exit 1
}

##########################################################################
# Count local commits ahead of upstream

$countStr = git rev-list --count HEAD "^sharwapi/main" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Error "ERROR: Failed to count local commits"
    exit 1
}
$count = [int]($countStr.Trim())

if ($count -lt 2) {
    Write-Host "$count local commit(s) found, no squash is required"
    exit 0
}

if ($Verify) {
    Write-Host "$count local commits found, squash is recommended"
    exit 1
}

##########################################################################
# Rebase and squash

Write-Host "Rebasing local changes against upstream main"
git rebase sharwapi/main
if ($LASTEXITCODE -ne 0) {
    Write-Error "ERROR: Rebase failed. Please resolve conflicts manually."
    exit 1
}

Write-Host "Squashing $count commits..."

# Build commit message from existing commits
$logLines = git log --oneline HEAD "^sharwapi/main"
$comment = "squashed commit:`n`n$($logLines -join "`n")"

# Reset to upstream main, keeping all changes staged
git reset --soft sharwapi/main
if ($LASTEXITCODE -ne 0) {
    Write-Error "ERROR: git reset failed"
    exit 1
}

if ($S) {
    git commit -S -m $comment
} else {
    git commit -m $comment
}
if ($LASTEXITCODE -ne 0) {
    Write-Error "ERROR: git commit failed"
    exit 1
}

Write-Host "---"
git log -n 1 --show-signature
Write-Host "---"

##########################################################################
# Push if requested

if ($Push) {
    $branch = git rev-parse --abbrev-ref HEAD
    Write-Host "Force pushing to origin/$branch"
    git push --force-with-lease origin $branch
    if ($LASTEXITCODE -ne 0) {
        Write-Error "ERROR: Push failed"
        exit 1
    }
    Write-Host "---"
    Write-Host "Done! Your PR has been updated."
    Write-Host "Visit GitHub to check the Pull Request status."
} else {
    $branch = git rev-parse --abbrev-ref HEAD
    Write-Host ""
    Write-Host "Squash complete. To push your changes, run:"
    Write-Host "  git push --force-with-lease origin $branch"
    Write-Host ""
    if (-not $S) {
        Write-Host "TIP: It is recommended to sign your commit with GPG."
        Write-Host "Re-run with -S flag: .\utils\squash-my-commits.ps1 -S -Push"
    }
}

##########################################################################
# end of file
