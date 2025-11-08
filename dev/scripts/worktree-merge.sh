#!/bin/bash
# worktree-merge.sh
# Automated merge for Proto Gear v0.5.0 worktrees

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MAIN_REPO="G:/Projects/proto-gear"
WORKTREES_DIR="G:/Projects/proto-gear-worktrees"
BASE_BRANCH="development"

# Worktree definitions
declare -A WORKTREES
WORKTREES["templates"]="feature/v0.5.0-templates-core"
WORKTREES["skills"]="feature/v0.5.0-skills-system"
WORKTREES["workflows"]="feature/v0.5.0-workflows-engine"

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

usage() {
    echo "Usage: $0 <workstream>"
    echo ""
    echo "Available workstreams:"
    echo "  templates  - Merge templates workstream"
    echo "  skills     - Merge skills workstream"
    echo "  workflows  - Merge workflows workstream"
    echo ""
    echo "Example:"
    echo "  $0 templates"
    exit 1
}

check_workstream() {
    local name=$1

    if [[ ! -v "WORKTREES[$name]" ]]; then
        print_error "Unknown workstream: $name"
        usage
    fi
}

pre_merge_checks() {
    local name=$1
    local branch=${WORKTREES[$name]}
    local path="$WORKTREES_DIR/v0.5.0-$name"

    print_header "Pre-Merge Checks: $name"

    # Check if main repo exists
    if [ ! -d "$MAIN_REPO" ]; then
        print_error "Main repository not found at $MAIN_REPO"
        exit 1
    fi

    # Check if worktree exists
    if [ ! -d "$path" ]; then
        print_error "Worktree not found at $path"
        exit 1
    fi

    # Check if branch exists
    cd "$MAIN_REPO"
    if ! git show-ref --verify --quiet "refs/heads/$branch"; then
        print_error "Branch $branch does not exist"
        exit 1
    fi
    print_success "Branch exists"

    # Check if on development branch
    CURRENT_BRANCH=$(git branch --show-current)
    if [ "$CURRENT_BRANCH" != "$BASE_BRANCH" ]; then
        print_error "Not on $BASE_BRANCH branch (currently on $CURRENT_BRANCH)"
        exit 1
    fi
    print_success "On $BASE_BRANCH branch"

    # Check for uncommitted changes in main repo
    if [[ -n $(git status -s) ]]; then
        print_error "You have uncommitted changes in main repository"
        git status -s
        exit 1
    fi
    print_success "No uncommitted changes in main repo"

    # Check for uncommitted changes in worktree
    cd "$path"
    if [[ -n $(git status -s) ]]; then
        print_error "You have uncommitted changes in worktree"
        git status -s
        exit 1
    fi
    print_success "No uncommitted changes in worktree"

    # Pull latest from development
    cd "$MAIN_REPO"
    print_warning "Pulling latest from origin/$BASE_BRANCH..."
    git pull origin "$BASE_BRANCH" || {
        print_warning "Could not pull from origin (maybe no remote?)"
    }
}

run_tests() {
    local path=$1

    print_header "Running Tests"

    cd "$path"

    # Run pytest
    echo ""
    echo "Running unit tests..."
    if python -m pytest tests/ -v; then
        print_success "Unit tests passed"
    else
        print_error "Unit tests failed"
        exit 1
    fi

    # Check coverage
    echo ""
    echo "Checking test coverage..."
    if python -m pytest --cov=core --cov-report=term-missing; then
        print_success "Coverage check passed"
    else
        print_error "Coverage check failed"
        exit 1
    fi

    # Run linting
    echo ""
    echo "Running linter..."
    if python -m flake8 core/; then
        print_success "Linting passed"
    else
        print_error "Linting failed"
        exit 1
    fi

    # Test CLI
    echo ""
    echo "Testing CLI..."
    if pg init --dry-run; then
        print_success "CLI test passed"
    else
        print_error "CLI test failed"
        exit 1
    fi
}

merge_branch() {
    local name=$1
    local branch=${WORKTREES[$name]}

    print_header "Merging: $name"

    cd "$MAIN_REPO"

    echo ""
    echo "Merging $branch into $BASE_BRANCH..."
    echo ""

    if git merge "$branch" --no-ff -m "Merge $name workstream for v0.5.0

Merging $branch into $BASE_BRANCH.

This merge includes:
- All $name features for v0.5.0
- Tests and documentation
- Integration with existing codebase

Refs: v0.5.0 milestone"; then
        print_success "Merge completed successfully"
    else
        print_error "Merge failed with conflicts"
        echo ""
        echo "Conflicted files:"
        git diff --name-only --diff-filter=U
        echo ""
        echo "To resolve:"
        echo "  1. Edit conflicted files"
        echo "  2. git add <resolved-files>"
        echo "  3. git merge --continue"
        echo ""
        echo "To abort:"
        echo "  git merge --abort"
        exit 1
    fi
}

post_merge_tests() {
    print_header "Post-Merge Tests"

    cd "$MAIN_REPO"

    # Run full test suite
    echo ""
    echo "Running full test suite..."
    if python -m pytest tests/ -v; then
        print_success "All tests passed"
    else
        print_error "Tests failed after merge"
        echo ""
        echo "The merge introduced issues. You should:"
        echo "  1. Fix the failing tests"
        echo "  2. Commit the fixes"
        echo "  3. Run tests again"
        exit 1
    fi

    # Test CLI
    echo ""
    echo "Testing CLI integration..."
    if pg init --dry-run; then
        print_success "CLI integration test passed"
    else
        print_error "CLI integration test failed"
        exit 1
    fi
}

push_to_remote() {
    print_header "Push to Remote"

    cd "$MAIN_REPO"

    read -p "Push to origin/$BASE_BRANCH? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push origin "$BASE_BRANCH"
        print_success "Pushed to origin/$BASE_BRANCH"
    else
        print_warning "Skipped push to remote"
        echo "You can push later with: git push origin $BASE_BRANCH"
    fi
}

show_summary() {
    local name=$1
    local branch=${WORKTREES[$name]}

    print_header "Merge Complete!"

    cd "$MAIN_REPO"

    echo ""
    echo "Merged: $branch -> $BASE_BRANCH"
    echo ""
    echo "Recent commits:"
    git log --oneline -5
    echo ""
    echo -e "${GREEN}Next steps:${NC}"
    echo "1. Verify the merge in $BASE_BRANCH"
    echo "2. Test thoroughly:"
    echo "   python -m pytest"
    echo "   pg init --dry-run"
    echo ""
    echo "3. When ready, clean up:"
    echo "   bash dev/scripts/worktree-cleanup.sh $name"
    echo ""
    echo "4. Continue with next workstream:"
    echo "   bash dev/scripts/worktree-merge.sh <next-workstream>"
}

# Main execution
main() {
    # Check arguments
    if [ $# -eq 0 ]; then
        print_error "No workstream specified"
        usage
    fi

    local name=$1
    check_workstream "$name"

    local branch=${WORKTREES[$name]}
    local path="$WORKTREES_DIR/v0.5.0-$name"

    print_header "Proto Gear v0.5.0 Merge: $name"
    echo "This script will:"
    echo "  1. Run pre-merge checks"
    echo "  2. Test the worktree"
    echo "  3. Merge $branch -> $BASE_BRANCH"
    echo "  4. Run post-merge tests"
    echo "  5. Optionally push to remote"
    echo ""
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Merge cancelled"
        exit 0
    fi

    pre_merge_checks "$name"
    run_tests "$path"
    merge_branch "$name"
    post_merge_tests
    push_to_remote
    show_summary "$name"
}

# Run main function
main "$@"
