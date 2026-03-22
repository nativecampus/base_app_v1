#!/usr/bin/env bash
set -euo pipefail

REPO="nativecampus/base_app_v1"

usage() {
    echo "Usage: curl -sL https://raw.githubusercontent.com/$REPO/main/install.sh | bash -s <project_name>"
    echo "  project_name: snake_case (e.g. email_reviewer, brace_scraper)"
    exit 1
}

name="${1:-}"
[ -z "$name" ] && usage

if ! [[ "$name" =~ ^[a-z][a-z0-9_]*$ ]]; then
    echo "Error: project name must be snake_case (lowercase letters, digits, underscores, starting with a letter)"
    exit 1
fi

if [ "$name" = "base_app" ]; then
    echo "Error: pick a real name, not 'base_app'"
    exit 1
fi

if [ -d "$name" ]; then
    echo "Error: directory '$name' already exists"
    exit 1
fi

for cmd in git python3 pipenv npm createdb; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "Error: $cmd is required but not found"
        exit 1
    fi
done

echo "Creating $name..."

git clone --quiet "git@github.com:$REPO.git" "$name"
cd "$name"
rm -rf .git install.sh
git init --quiet

python3 manage.py init "$name"

git add -A
git commit --quiet -m "Initial commit from base_app template"

echo ""
echo "Ready. Next steps:"
echo "  cd $name"
echo "  python manage.py dev"
