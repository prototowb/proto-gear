#!/usr/bin/env python3
"""
Interactive demonstration of the v0.8.0 Composition Engine

Run this script to see the composition engine in action.
"""

from pathlib import Path
from core.proto_gear_pkg.capability_metadata import (
    load_all_capabilities,
    CompositionEngine,
    CapabilityValidator
)


def main():
    print("=== Proto Gear v0.8.0 Composition Engine Demo ===\n")

    # Load all capabilities
    caps_dir = Path('core/proto_gear_pkg/capabilities')
    all_caps = load_all_capabilities(caps_dir)

    print(f"PASS: Loaded {len(all_caps)} capabilities")
    print()

    # Example 1: Simple capability info
    print("--- Example 1: View Capability Info ---")
    testing = all_caps['skills/testing']
    print(f"Name: {testing.name}")
    print(f"Type: {testing.type.value}")
    print(f"Description: {testing.description}")
    print(f"Status: {testing.status.value}")
    print(f"Agent roles: {', '.join(testing.agent_roles[:3])}...")
    print()

    # Example 2: Dependency Resolution
    print("--- Example 2: Automatic Dependency Resolution ---")
    print("User selects: bug-fix workflow")
    selected = ["workflows/bug-fix"]

    resolved = CompositionEngine.resolve_dependencies(selected, all_caps)
    print(f"Engine automatically includes: {len(resolved)} capabilities")
    for cap_id in sorted(resolved):
        print(f"  - {cap_id}")
    print()

    # Example 3: Conflict Detection
    print("--- Example 3: Conflict Detection ---")
    print("(Currently no conflicts defined)")
    selected = ["workflows/bug-fix", "workflows/feature-development"]
    conflicts = CompositionEngine.detect_conflicts(selected, all_caps)
    if conflicts:
        print(f"Found {len(conflicts)} conflicts:")
        for c1, c2, reason in conflicts:
            print(f"  WARN: {c1} <-> {c2}: {reason}")
    else:
        print("  PASS: No conflicts - these capabilities work together!")
    print()

    # Example 4: Smart Recommendations
    print("--- Example 4: Smart Recommendations ---")
    print("User has: testing skill")
    selected = ["skills/testing"]

    recommended = CompositionEngine.get_recommended_capabilities(selected, all_caps)
    print(f"Engine suggests {len(recommended)} compatible capabilities:")
    for cap_id in recommended[:5]:  # Show first 5
        cap = all_caps[cap_id]
        print(f"  -> {cap_id}: {cap.name}")
    print()

    # Example 5: Transitive Dependencies
    print("--- Example 5: Transitive Dependencies ---")
    print("User selects: refactoring skill")
    selected = ["skills/refactoring"]

    refactoring = all_caps['skills/refactoring']
    print(f"Required dependencies: {refactoring.dependencies.required}")

    resolved = CompositionEngine.resolve_dependencies(selected, all_caps)
    print(f"Engine includes: {sorted(resolved)}")
    print()

    # Example 6: Validation
    print("--- Example 6: Metadata Validation ---")
    testing = all_caps['skills/testing']
    warnings = CapabilityValidator.validate_metadata(testing)
    print(f"Validating 'testing' skill...")
    if warnings:
        print(f"  WARN: {warnings}")
    else:
        print("  PASS: No warnings - metadata is complete!")
    print()

    # Example 7: Search by Trigger
    print("--- Example 7: Search by Trigger Keywords ---")
    query = "bug"
    print(f"Searching for capabilities matching '{query}'...")
    matches = []
    for cap_id, metadata in all_caps.items():
        if metadata.relevance and metadata.relevance.matches_trigger(query):
            matches.append((cap_id, metadata.name))

    print(f"Found {len(matches)} matches:")
    for cap_id, name in matches[:5]:
        print(f"  -> {cap_id}: {name}")
    print()

    # Summary
    print("=== Summary ===")
    print(f"Total capabilities: {len(all_caps)}")
    print(f"  - Skills: {len([c for c in all_caps if c.startswith('skills/')])}")
    print(f"  - Workflows: {len([c for c in all_caps if c.startswith('workflows/')])}")
    print(f"  - Commands: {len([c for c in all_caps if c.startswith('commands/')])}")
    print()
    print("PASS: Composition engine is ready for v0.8.0!")


if __name__ == "__main__":
    main()
