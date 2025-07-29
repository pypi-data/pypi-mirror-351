#!/bin/bash

set -e

if [ $# -ne 2 ]; then
    echo "Usage: $0 <branch-or-tag> <new-version>"
    echo "Example: $0 v1.0.0 1.0.0.1"
    exit 1
fi

BRANCH_OR_TAG=$1
NEW_VERSION=$2
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Check if current branch is main
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "Error: You must be on the main branch to run this script."
    exit 1
fi

# Pull latest changes from main
echo "Pulling latest changes from main branch..."
git pull origin main

# Create a new release branch (or recreate if it exists)
RELEASE_BRANCH="release_${NEW_VERSION}"
echo "Creating branch ${RELEASE_BRANCH}..."
git switch -C ${RELEASE_BRANCH}

# Run update_kachaka_api.sh
echo "Running update_kachaka_api.sh..."
${SCRIPT_DIR}/update_kachaka_api.sh "${BRANCH_OR_TAG}" "${NEW_VERSION}"

# Stage and commit changes
echo "Staging and committing changes..."
git add -A
git commit -m "release v${NEW_VERSION}"

# Push to remote
echo "Pushing branch to remote..."
git push -u origin ${RELEASE_BRANCH}

# Create PR if GitHub CLI is installed
if command -v gh &> /dev/null; then
    echo "Creating pull request using GitHub CLI..."
    gh pr create \
        --title "Release v${NEW_VERSION}" \
        --body "This PR updates kachaka-api with code from ${BRANCH_OR_TAG} and sets version to ${NEW_VERSION}." \
        --base main \
        --head ${RELEASE_BRANCH}
else
    echo "GitHub CLI not installed. Please create a pull request manually using the URL below:"
    REPO_URL=$(git config --get remote.origin.url | sed 's/\.git$//' | sed 's/^git@github\.com:/https:\/\/github.com\//')
    echo "${REPO_URL}/compare/main...${RELEASE_BRANCH}?expand=1"
fi

# Switch back to main branch
git switch main

echo "Done! Release branch ${RELEASE_BRANCH} created and pull request submitted."
