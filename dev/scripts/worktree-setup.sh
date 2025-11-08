#!/bin/bash
# worktree-setup.sh
# Automated setup for Proto Gear v0.5.0 worktrees

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

check_prerequisites() {
    print_header "Checking Prerequisites"

    # Check if git is installed
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed"
        exit 1
    fi
    print_success "Git is installed"

    # Check if main repo exists
    if [ ! -d "$MAIN_REPO" ]; then
        print_error "Main repository not found at $MAIN_REPO"
        exit 1
    fi
    print_success "Main repository found"

    # Check if on correct branch
    cd "$MAIN_REPO"
    CURRENT_BRANCH=$(git branch --show-current)
    if [ "$CURRENT_BRANCH" != "$BASE_BRANCH" ]; then
        print_warning "Not on $BASE_BRANCH branch (currently on $CURRENT_BRANCH)"
        read -p "Switch to $BASE_BRANCH? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git checkout "$BASE_BRANCH"
            print_success "Switched to $BASE_BRANCH"
        else
            print_error "Must be on $BASE_BRANCH branch to continue"
            exit 1
        fi
    else
        print_success "On $BASE_BRANCH branch"
    fi

    # Check for uncommitted changes
    if [[ -n $(git status -s) ]]; then
        print_error "You have uncommitted changes in main repository"
        git status -s
        exit 1
    fi
    print_success "No uncommitted changes"

    # Pull latest
    print_warning "Pulling latest from origin/$BASE_BRANCH..."
    git pull origin "$BASE_BRANCH" || {
        print_warning "Could not pull from origin (maybe no remote?)"
    }
}

enable_rerere() {
    print_header "Configuring Git"

    cd "$MAIN_REPO"

    # Enable rerere
    git config rerere.enabled true
    git config rerere.autoupdate true
    print_success "Enabled Git rerere (reuse recorded resolution)"

    # Show current config
    echo ""
    echo "Current Git configuration:"
    echo "  rerere.enabled: $(git config rerere.enabled)"
    echo "  rerere.autoupdate: $(git config rerere.autoupdate)"
}

create_worktrees_directory() {
    print_header "Creating Worktrees Directory"

    if [ -d "$WORKTREES_DIR" ]; then
        print_warning "Worktrees directory already exists"
    else
        mkdir -p "$WORKTREES_DIR"
        print_success "Created $WORKTREES_DIR"
    fi
}

create_worktree() {
    local name=$1
    local branch=$2
    local path="$WORKTREES_DIR/v0.5.0-$name"

    print_header "Creating Worktree: $name"

    cd "$MAIN_REPO"

    # Check if branch already exists
    if git show-ref --verify --quiet "refs/heads/$branch"; then
        print_error "Branch $branch already exists"
        read -p "Delete existing branch and recreate? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            # Remove worktree if exists
            if [ -d "$path" ]; then
                git worktree remove "$path" --force 2>/dev/null || true
            fi
            # Delete branch
            git branch -D "$branch"
            print_success "Deleted existing branch"
        else
            print_warning "Skipping $name worktree"
            return
        fi
    fi

    # Check if worktree path already exists
    if [ -d "$path" ]; then
        print_error "Worktree directory already exists: $path"
        read -p "Remove and recreate? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git worktree remove "$path" --force 2>/dev/null || true
            rm -rf "$path"
            print_success "Removed existing directory"
        else
            print_warning "Skipping $name worktree"
            return
        fi
    fi

    # Create worktree
    git worktree add -b "$branch" "$path" "$BASE_BRANCH"
    print_success "Created worktree: $name"

    # Initial commit
    cd "$path"
    echo "# ${name^} Development" > WORKSTREAM.md
    echo "" >> WORKSTREAM.md
    echo "Workstream for v0.5.0 $name development." >> WORKSTREAM.md
    echo "" >> WORKSTREAM.md
    echo "**Branch**: $branch" >> WORKSTREAM.md
    echo "**Created**: $(date +%Y-%m-%d)" >> WORKSTREAM.md
    echo "" >> WORKSTREAM.md
    echo "## Progress" >> WORKSTREAM.md
    echo "" >> WORKSTREAM.md
    echo "- [ ] Initial implementation" >> WORKSTREAM.md
    echo "- [ ] Tests written" >> WORKSTREAM.md
    echo "- [ ] Documentation updated" >> WORKSTREAM.md
    echo "- [ ] Ready for merge" >> WORKSTREAM.md

    git add WORKSTREAM.md
    git commit -m "feat($name): initialize $name workstream

Starting development for v0.5.0 $name features.

Refs: v0.5.0 milestone"

    print_success "Created initial commit"

    cd "$MAIN_REPO"
}

show_summary() {
    print_header "Setup Complete!"

    cd "$MAIN_REPO"

    echo ""
    echo "Worktrees created:"
    git worktree list

    echo ""
    echo "Branches created:"
    git branch | grep "v0.5.0"

    echo ""
    echo -e "${GREEN}Next steps:${NC}"
    echo "1. Start working in each worktree:"
    echo "   cd $WORKTREES_DIR/v0.5.0-templates"
    echo "   cd $WORKTREES_DIR/v0.5.0-skills"
    echo "   cd $WORKTREES_DIR/v0.5.0-workflows"
    echo ""
    echo "2. Make your changes and commit regularly"
    echo ""
    echo "3. Test before merging:"
    echo "   python -m pytest"
    echo "   pg init --dry-run"
    echo ""
    echo "4. Merge sequentially when ready:"
    echo "   bash dev/scripts/worktree-merge.sh templates"
    echo "   bash dev/scripts/worktree-merge.sh skills"
    echo "   bash dev/scripts/worktree-merge.sh workflows"
    echo ""
    echo -e "${YELLOW}Documentation:${NC}"
    echo "  - Full workflow: docs/dev/git-worktrees-workflow.md"
    echo "  - Quick reference: docs/dev/worktrees-quick-reference.md"
    echo "  - Visual guide: docs/dev/worktrees-workflow-diagram.md"
}

# Main execution
main() {
    print_header "Proto Gear v0.5.0 Worktrees Setup"
    echo "This script will create 3 worktrees for parallel development:"
    echo "  1. Templates (CONTRIBUTING, SECURITY, etc.)"
    echo "  2. Skills (debugging, code-review, etc.)"
    echo "  3. Workflows (bug-fix, hotfix, release)"
    echo ""
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Setup cancelled"
        exit 0
    fi

    check_prerequisites
    enable_rerere
    create_worktrees_directory

    # Create each worktree
    for name in "${!WORKTREES[@]}"; do
        create_worktree "$name" "${WORKTREES[$name]}"
    done

    show_summary
}

# Run main function
main
