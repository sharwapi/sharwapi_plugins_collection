#!/bin/sh
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
#   ./utils/squash-my-commits.sh [options]
#
# use './utils/squash-my-commits.sh -S' to sign the result with your GPG key
# use './utils/squash-my-commits.sh -S --push' to also push automatically
#
##########################################################################

usage()
{
    echo "Usage: $0 [options]"
    echo 'Options:'
    echo ' -S,        sign the result with your GPG key (recommended)'
    echo ' --push,    force push result to your fork after squash'
    echo ' --ssh,     use SSH to fetch from the upstream repository'
    echo ' --https,   use HTTPS to fetch from the upstream repository'
    echo ' --verify,  check only (do not squash)'
    echo ' --help,    display this message'
    echo ''
    echo 'Environment variables:'
    echo ' SHARWAPI_REG_URL,  set the upstream repository URL directly'
    echo ''
    echo 'Examples:'
    echo " $0 -S --push     # squash, sign with GPG, and push (recommended)"
    echo " $0 -S            # squash and sign, then push manually"
    echo " $0 --verify      # check if squash is needed"
}

##########################################################################
# parse arguments

do_push=0
verify_only=0
do_sign=0

for arg
do
    case "$arg" in

        -S)
            do_sign=1
            ;;
        --push)
            do_push=1
            ;;
        --ssh)
            echo 'Forcing use of SSH to fetch from upstream'
            reg_proto="ssh"
            ;;
        --https)
            echo 'Forcing use of HTTPS to fetch from upstream'
            reg_proto="https"
            ;;
        --verify)
            verify_only=1
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $arg"
            usage
            exit 1
            ;;

    esac
done

##########################################################################

# check for sharwapi remote, and add if missing
if ! git remote -v | grep sharwapi > /dev/null 2>&1
then

    # was the URL specified directly?
    if [ -n "$SHARWAPI_REG_URL" ]
    then
        reg="$SHARWAPI_REG_URL"
    else

        if [ -z "$reg_proto" ]
        then
            # if the proto wasn't forced, try to guess it
            if git remote -v | grep 'https' > /dev/null 2>&1
            then
                reg_proto='https'
            else
                reg_proto='ssh'
            fi
        fi

        case "$reg_proto" in
            ssh)
                reg='git@github.com:sharwapi/sharwapi_plugins_collection.git'
                ;;
            https)
                reg='https://github.com/sharwapi/sharwapi_plugins_collection.git'
                ;;
            *)
                echo 'ERROR: Unknown registry protocol'
                exit 1
                ;;
        esac
    fi

    echo "Adding sharwapi remote: $reg"
    git remote add sharwapi "$reg"
fi

##########################################################################

# ensure the local branch is up to date
echo "Fetching sharwapi main"
if ! git fetch sharwapi main
then
    echo 'ERROR: Failed to fetch upstream main branch'
    echo 'Hint: use --ssh or --https to force a specific protocol'
    echo 'Or set SHARWAPI_REG_URL to specify the URL directly'
    exit 1
fi

# find number of local commits
if ! count=$(git rev-list --count HEAD ^sharwapi/main)
then
    echo "ERROR: Failed to find the number of local commits"
    echo "Please report this as a bug"
    exit 1
fi

# if there are less than 2 local commits, there's nothing to squash
if [ "$count" -lt 2 ]
then
    echo "$count local commit(s) found, no squash is required"
    exit 0
fi

if [ "$verify_only" -eq 1 ]
then
    echo "$count local commits found, squash is recommended"
    exit 1
fi

# fail on errors from here onwards
set -e

# do the rebase to bring up to date with upstream
echo 'Rebasing local changes against upstream main'
git rebase sharwapi/main

echo "Squashing $count commits..."

# construct a new commit message based on previous commits
comment="squashed commit:

$(git log --oneline HEAD ^sharwapi/main)"

# squash: reset to upstream main, keeping all changes staged
git reset --soft sharwapi/main

if [ "$do_sign" -eq 1 ]
then
    git commit -S -m "$comment"
else
    git commit -m "$comment"
fi

# show what happened
echo '---'
git log -n 1 --show-signature
echo '---'

##########################################################################

# push changes if requested
if [ "$do_push" -eq 1 ]
then
    branch=$(git rev-parse --abbrev-ref HEAD)
    echo "Force pushing to origin/$branch"
    git push --force-with-lease origin "$branch"
    echo '---'
    echo 'Done! Your PR has been updated.'
    echo 'Visit GitHub to check the Pull Request status.'
else
    echo ''
    branch=$(git rev-parse --abbrev-ref HEAD)
    echo "Squash complete. To push your changes, run:"
    echo "  git push --force-with-lease origin $branch"
    echo ''
    if [ "$do_sign" -ne 1 ]
    then
        echo 'TIP: It is recommended to sign your commit with GPG.'
        echo 'Re-run with the -S flag: ./utils/squash-my-commits.sh -S --push'
    fi
fi

##########################################################################
# end of file
