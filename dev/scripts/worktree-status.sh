#!/bin/bash
# worktree-status.sh
# Check status of all Proto Gear v0.5.0 worktrees

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

print_section() {
    echo -e "${CYAN}--- $1 ---${NC}"
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

show_main_repo_status() {
    print_header "Main Repository Status"

    cd "$MAIN_REPO"

    echo ""
    print_section "Current Branch"
    git branch --show-current

    echo ""
    print_section "Git Status"
    git status -s || echo "Clean"

    echo ""
    print_section "Recent Commits"
    git log --oneline -5

    echo ""
    print_section "All Worktrees"
    git worktree list
}

show_worktree_status() {
    local name=$1
    local branch=${WORKTREES[$name]}
    local path="$WORKTREES_DIR/v0.5.0-$name"

    echo ""
    print_header "Worktree: $name"

    # Check if worktree exists
    if [ ! -d "$path" ]; then
        print_warning "Worktree not found at $path"
        return
    fi

    cd "$path"

    echo ""
    print_section "Branch"
    git branch --show-current

    echo ""
    print_section "Git Status"
    if [[ -z $(git status -s) ]]; then
        print_success "Clean (no uncommitted changes)"
    else
        print_warning "Has uncommitted changes:"
        git status -s
    fi

    echo ""
    print_section "Commits Ahead of Development"
    local ahead=$(git rev-list --count "$BASE_BRANCH"..HEAD)
    if [ "$ahead" -eq 0 ]; then
        print_warning "No commits (0 ahead of $BASE_BRANCH)"
    else
        print_success "$ahead commits ahead of $BASE_BRANCH"
        git log --oneline "$BASE_BRANCH"..HEAD
    fi

    echo ""
    print_section "Files Changed"
    local files_changed=$(git diff --name-only "$BASE_BRANCH"..HEAD | wc -l)
    echo "$files_changed files changed from $BASE_BRANCH"
    if [ "$files_changed" -gt 0 ]; then
        git diff --name-only "$BASE_BRANCH"..HEAD | head -10
        if [ "$files_changed" -gt 10 ]; then
            echo "... and $((files_changed - 10)) more files"
        fi
    fi

    echo ""
    print_section "Test Status"
    if python -m pytest tests/ -q 2>/dev/null; then
        print_success "Tests passing"
    else
        print_error "Tests failing or not run"
    fi

    echo ""
    print_section "Merge Status"
    cd "$MAIN_REPO"
    if git branch --merged "$BASE_BRANCH" | grep -q "$branch"; then
        print_success "Merged into $BASE_BRANCH"
    else
        print_warning "Not yet merged into $BASE_BRANCH"
    fi
}

show_conflict_analysis() {
    print_header "Potential Conflicts Analysis"

    cd "$MAIN_REPO"

    echo ""
    print_section "Files Modified by Multiple Workstreams"

    # Collect files modified by each workstream
    declare -A file_workstreams

    for name in "${!WORKTREES[@]}"; do
        local branch=${WORKTREES[$name]}
        local path="$WORKTREES_DIR/v0.5.0-$name"

        if [ -d "$path" ]; then
            cd "$path"
            while IFS= read -r file; do
                if [[ -v "file_workstreams[$file]" ]]; then
                    file_workstreams["$file"]="${file_workstreams[$file]},$name"
                else
                    file_workstreams["$file"]="$name"
                fi
            done < <(git diff --name-only "$BASE_BRANCH"..HEAD)
        fi
    done

    # Show conflicts
    local has_conflicts=false
    for file in "${!file_workstreams[@]}"; do
        local workstreams="${file_workstreams[$file]}"
        if [[ "$workstreams" == *","* ]]; then
            has_conflicts=true
            print_warning "$file modified by: $workstreams"
        fi
    done

    if [ "$has_conflicts" = false ]; then
        print_success "No file conflicts detected!"
    fi
}

show_test_coverage() {
    print_header "Test Coverage Overview"

    for name in "${!WORKTREES[@]}"; do
        local path="$WORKTREES_DIR/v0.5.0-$name"

        if [ ! -d "$path" ]; then
            continue
        fi

        echo ""
        print_section "$name Workstream"
        cd "$path"

        python -m pytest --cov=core --cov-report=term-missing -q 2>/dev/null || {
            print_warning "Could not run coverage analysis"
        }
    done
}

show_integration_readiness() {
    print_header "Integration Readiness"

    for name in "${!WORKTREES[@]}"; do
        local branch=${WORKTREES[$name]}
        local path="$WORKTREES_DIR/v0.5.0-$name"

        echo ""
        print_section "$name"

        if [ ! -d "$path" ]; then
            print_warning "Worktree not found"
            continue
        fi

        cd "$path"

        local ready=true
        local issues=()

        # Check for uncommitted changes
        if [[ -n $(git status -s) ]]; then
            ready=false
            issues+=("Has uncommitted changes")
        fi

        # Check for commits
        local ahead=$(git rev-list --count "$BASE_BRANCH"..HEAD)
        if [ "$ahead" -eq 0 ]; then
            ready=false
            issues+=("No commits")
        fi

        # Check if tests pass
        if ! python -m pytest tests/ -q 2>/dev/null; then
            ready=false
            issues+=("Tests failing")
        fi

        # Check if merged
        cd "$MAIN_REPO"
        if git branch --merged "$BASE_BRANCH" | grep -q "$branch"; then
            print_success "Already merged"
        elif [ "$ready" = true ]; then
            print_success "Ready for merge ($ahead commits)"
        else
            print_error "Not ready for merge"
            for issue in "${issues[@]}"; do
                echo "  - $issue"
            done
        fi
    done
}

show_summary() {
    print_header "Summary"

    cd "$MAIN_REPO"

    echo ""
    print_section "Worktrees Active"
    local worktree_count=$(git worktree list | grep -c "v0.5.0" || echo "0")
    echo "$worktree_count v0.5.0 worktrees"

    echo ""
    print_section "Branches Status"
    local merged_count=0
    local unmerged_count=0

    for name in "${!WORKTREES[@]}"; do
        local branch=${WORKTREES[$name]}
        if git show-ref --verify --quiet "refs/heads/$branch"; then
            if git branch --merged "$BASE_BRANCH" | grep -q "$branch"; then
                ((merged_count++))
            else
                ((unmerged_count++))
            fi
        fi
    done

    echo "Merged: $merged_count"
    echo "Unmerged: $unmerged_count"

    echo ""
    if [ "$unmerged_count" -eq 0 ] && [ "$merged_count" -eq 3 ]; then
        print_success "All workstreams merged! Ready for cleanup."
        echo ""
        echo "Next steps:"
        echo "  bash dev/scripts/worktree-cleanup.sh all"
    elif [ "$worktree_count" -gt 0 ]; then
        print_warning "Development in progress"
        echo ""
        echo "Continue working in worktrees, then merge when ready:"
        echo "  bash dev/scripts/worktree-merge.sh <workstream>"
    else
        print_warning "No active worktrees found"
        echo ""
        echo "Setup worktrees to begin:"
        echo "  bash dev/scripts/worktree-setup.sh"
    fi
}

# Main execution
main() {
    print_header "Proto Gear v0.5.0 Worktrees Status"
    echo ""

    if [ ! -d "$MAIN_REPO" ]; then
        print_error "Main repository not found at $MAIN_REPO"
        exit 1
    fi

    # Show status of each component
    show_main_repo_status

    for name in templates skills workflows; do
        show_worktree_status "$name"
    done

    show_conflict_analysis
    show_integration_readiness
    show_summary

    echo ""
    echo "For detailed workflow documentation:"
    echo "  docs/dev/git-worktrees-workflow.md"
}

# Run main function
main
