#!/bin/bash

set -e

if [ $# -ne 2 ]; then
    echo "Usage: $0 <branch-or-tag> <new-version>"
    echo "Example: $0 v1.0.0 1.0.0.1"
    exit 1
fi

BRANCH_OR_TAG=$1
NEW_VERSION=$2
SOURCE_REPO_DIR=$(mktemp -d)
ORIGINAL_REPO_URL="https://github.com/pf-robotics/kachaka-api.git"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "Temporary directory: ${SOURCE_REPO_DIR}"
echo "Fetching ${BRANCH_OR_TAG} from the original repository..."

# Clone the original repository 
# Use --quiet to suppress git messages and clone without checking out (--no-checkout)
# Then fetch the specific tag/branch and checkout to avoid detached HEAD warnings
git clone --quiet --no-checkout "${ORIGINAL_REPO_URL}" "${SOURCE_REPO_DIR}" || {
    echo "Error: Could not clone the repository."
    rm -rf "${SOURCE_REPO_DIR}"
    exit 1
}

# Enter directory and fetch the specific tag/branch
cd "${SOURCE_REPO_DIR}"
git fetch --quiet --depth 1 origin "${BRANCH_OR_TAG}"
git checkout --quiet FETCH_HEAD || {
    echo "Error: Branch or tag '${BRANCH_OR_TAG}' not found."
    cd "${REPO_ROOT}"
    rm -rf "${SOURCE_REPO_DIR}"
    exit 1
}
cd "${REPO_ROOT}"

echo "Updating kachaka_api directory..."


# Remove existing kachaka_api directory
rm -rf "${REPO_ROOT}/kachaka_api"

# Copy kachaka_api directory
cp -r "${SOURCE_REPO_DIR}/python/kachaka_api" "${REPO_ROOT}/kachaka_api"

# Use Python script to update pyproject.toml
echo "Updating pyproject.toml..."
pushd "${SCRIPT_DIR}/pyproject_toml_updater"
uv run update_pyproject_toml.py \
    "${SOURCE_REPO_DIR}/pyproject.toml" \
    "${REPO_ROOT}/pyproject.toml" \
    "${NEW_VERSION}"
popd

echo "Cleaning up..."
rm -rf "${SOURCE_REPO_DIR}"

echo "Completed! kachaka-api has been updated with code from ${BRANCH_OR_TAG} and version set to ${NEW_VERSION}."
