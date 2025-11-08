#!/bin/bash
# worktree-cleanup.sh
# Cleanup script for Proto Gear v0.5.0 worktrees after successful merge

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
    echo "Usage: $0 <workstream|all>"
    echo ""
    echo "Available workstreams:"
    echo "  templates  - Clean up templates workstream"
    echo "  skills     - Clean up skills workstream"
    echo "  workflows  - Clean up workflows workstream"
    echo "  all        - Clean up all workstreams"
    echo ""
    echo "Example:"
    echo "  $0 templates"
    echo "  $0 all"
    exit 1
}

check_workstream() {
    local name=$1

    if [ "$name" != "all" ] && [[ ! -v "WORKTREES[$name]" ]]; then
        print_error "Unknown workstream: $name"
        usage
    fi
}

verify_merge() {
    local name=$1
    local branch=${WORKTREES[$name]}

    print_header "Verifying Merge: $name"

    cd "$MAIN_REPO"

    # Check if branch is merged into development
    if git branch --merged "$BASE_BRANCH" | grep -q "$branch"; then
        print_success "Branch $branch is merged into $BASE_BRANCH"
        return 0
    else
        print_error "Branch $branch is NOT merged into $BASE_BRANCH"
        echo ""
        echo "Cannot clean up unmerged worktree!"
        echo "First merge the branch:"
        echo "  bash dev/scripts/worktree-merge.sh $name"
        return 1
    fi
}

remove_worktree() {
    local name=$1
    local branch=${WORKTREES[$name]}
    local path="$WORKTREES_DIR/v0.5.0-$name"

    print_header "Removing Worktree: $name"

    cd "$MAIN_REPO"

    # Check if worktree exists
    if [ ! -d "$path" ]; then
        print_warning "Worktree not found at $path (already removed?)"
        return 0
    fi

    # Check for uncommitted changes
    cd "$path"
    if [[ -n $(git status -s) ]]; then
        print_error "Worktree has uncommitted changes!"
        git status -s
        echo ""
        read -p "Force remove anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_warning "Keeping worktree"
            return 1
        fi
    fi

    # Remove worktree
    cd "$MAIN_REPO"
    git worktree remove "$path"
    print_success "Removed worktree: $path"
}

delete_branch() {
    local name=$1
    local branch=${WORKTREES[$name]}

    print_header "Deleting Branch: $name"

    cd "$MAIN_REPO"

    # Ask for confirmation
    echo ""
    echo "Delete local branch: $branch?"
    echo "(The merge commit is safe in $BASE_BRANCH)"
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Keeping local branch"
        return 0
    fi

    # Delete local branch
    git branch -d "$branch"
    print_success "Deleted local branch: $branch"

    # Ask about remote branch
    if git ls-remote --exit-code --heads origin "$branch" >/dev/null 2>&1; then
        echo ""
        echo "Remote branch origin/$branch also exists."
        read -p "Delete remote branch? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git push origin --delete "$branch"
            print_success "Deleted remote branch: origin/$branch"
        else
            print_warning "Keeping remote branch"
        fi
    fi
}

cleanup_workstream() {
    local name=$1

    echo ""
    print_header "Cleaning Up: $name"
    echo ""

    # Verify merge first
    if ! verify_merge "$name"; then
        print_error "Skipping cleanup for $name (not merged)"
        return 1
    fi

    # Remove worktree
    if ! remove_worktree "$name"; then
        print_error "Failed to remove worktree for $name"
        return 1
    fi

    # Delete branch
    delete_branch "$name"

    print_success "Cleanup complete for $name"
    return 0
}

cleanup_all() {
    print_header "Cleaning Up All Worktrees"

    local success_count=0
    local fail_count=0

    for name in "${!WORKTREES[@]}"; do
        if cleanup_workstream "$name"; then
            ((success_count++))
        else
            ((fail_count++))
        fi
    done

    echo ""
    print_header "Cleanup Summary"
    echo ""
    echo "Successfully cleaned: $success_count"
    echo "Failed to clean: $fail_count"
}

show_final_status() {
    print_header "Final Status"

    cd "$MAIN_REPO"

    echo ""
    echo "Current worktrees:"
    git worktree list

    echo ""
    echo "Current branches:"
    git branch | grep -E "(development|main|v0.5.0)" || echo "No v0.5.0 branches remaining"

    echo ""
    if [ -d "$WORKTREES_DIR" ]; then
        echo "Worktrees directory contents:"
        ls -la "$WORKTREES_DIR"

        # Check if directory is empty
        if [ -z "$(ls -A $WORKTREES_DIR)" ]; then
            echo ""
            read -p "Worktrees directory is empty. Remove it? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                rmdir "$WORKTREES_DIR"
                print_success "Removed empty worktrees directory"
            fi
        fi
    fi

    echo ""
    print_success "Cleanup complete!"
    echo ""
    echo -e "${GREEN}Next steps:${NC}"
    echo "1. Verify development branch has all changes:"
    echo "   git log --oneline -10"
    echo ""
    echo "2. If ready, create release:"
    echo "   git tag -a v0.5.0 -m 'Release v0.5.0'"
    echo "   git checkout main"
    echo "   git merge development --no-ff"
    echo "   git push origin main --tags"
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

    print_header "Proto Gear v0.5.0 Cleanup"

    if [ "$name" = "all" ]; then
        echo "This script will clean up ALL worktrees:"
        echo "  - Remove worktree directories"
        echo "  - Delete feature branches (local and remote)"
        echo ""
        echo "Only proceed if all workstreams are merged!"
    else
        echo "This script will clean up the $name worktree:"
        echo "  - Remove worktree directory"
        echo "  - Delete feature branch (local and remote)"
        echo ""
        echo "Only proceed if $name is merged to $BASE_BRANCH!"
    fi

    echo ""
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Cleanup cancelled"
        exit 0
    fi

    cd "$MAIN_REPO"

    if [ "$name" = "all" ]; then
        cleanup_all
    else
        cleanup_workstream "$name"
    fi

    show_final_status
}

# Run main function
main "$@"
