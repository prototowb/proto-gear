# Template Metadata Schema

**Status**: Implemented
**Version**: 1.0.0
**Since**: v0.7.0
**Last Updated**: 2025-11-16

---

## Overview

Proto Gear supports YAML frontmatter in template files to enable conditional content generation based on project type, framework, and other project characteristics. This allows templates to adapt dynamically to different technology stacks while maintaining a single source of truth.

## Benefits

- **DRY Principle**: One template file instead of multiple language-specific versions
- **Smart Defaults**: Templates automatically show relevant content for detected project type
- **Maintainability**: Update once, applies to all project types
- **User Experience**: Users see only relevant examples and guidance
- **Extensibility**: Easy to add new conditional sections without code changes

---

## Metadata Schema

### YAML Frontmatter Format

Templates can include optional YAML frontmatter at the beginning of the file:

```markdown
---
name: "Template Name"
version: "1.0.0"
requires:
  project_type: ["Python", "Node.js", "Any"]
conditional_sections:
  section_name:
    condition: "project_type == 'Python'"
    content: |
      Content that appears only for Python projects
---

# Template Body

Regular template content with placeholders.

{{section_name}}

More content...
```

### Schema Fields

#### `name` (string, optional)

Human-readable template name for documentation purposes.

```yaml
name: "Testing Workflow"
```

#### `version` (string, optional, default: "1.0.0")

Template version for tracking changes and compatibility.

```yaml
version: "1.0.0"
```

#### `requires` (object, optional)

Specifies project requirements for this template. If requirements are not met, the template is still generated but a warning is shown.

**Supported requirement keys:**
- `project_type`: Array of acceptable project types
- `framework`: Array of acceptable frameworks (future)

**Special values:**
- `"Any"`: Accepts any value for that requirement

```yaml
requires:
  project_type: ["Python", "Node.js", "Any"]
```

#### `conditional_sections` (object, optional)

Defines content sections that are conditionally included based on project characteristics.

Each section has:
- **key**: Section name (used as placeholder in template)
- **condition**: Expression to evaluate
- **content**: Markdown content to insert if condition matches

```yaml
conditional_sections:
  python_examples:
    condition: "project_type == 'Python'"
    content: |
      ### Python-Specific Examples

      ```python
      import pytest

      def test_example():
          assert True
      ```

  nodejs_examples:
    condition: "project_type == 'Node.js'"
    content: |
      ### Node.js-Specific Examples

      ```javascript
      describe('example', () => {
        it('works', () => {
          expect(true).toBe(true);
        });
      });
      ```
```

---

## Condition Syntax

Currently supports simple equality expressions:

### Supported Patterns

```yaml
# Check project type
condition: "project_type == 'Python'"

# Check framework
condition: "framework == 'Django'"

# With double quotes
condition: "project_type == \"Python\""
```

### Future Support (Roadmap)

- Logical operators: `&&`, `||`, `!`
- Comparisons: `!=`, `in`
- Multiple conditions: `project_type == 'Python' && framework == 'Django'`

---

## Template Placeholders

In the template body, use double-curly-brace syntax to mark where conditional content should be inserted:

```markdown
# Template Content

{{python_examples}}

{{nodejs_examples}}

More content...
```

### Placeholder Behavior

- **Matching section**: Placeholder replaced with section content
- **No match**: Placeholder removed (empty string)
- **Multiple sections**: All matching sections inserted

---

## Complete Example

### TESTING.template.md

```markdown
---
name: "Testing Workflow"
version: "1.0.0"
requires:
  project_type: ["Python", "Node.js", "Any"]
conditional_sections:
  python_testing:
    condition: "project_type == 'Python'"
    content: |
      ## Python Testing with Pytest

      ```python
      # conftest.py
      import pytest

      @pytest.fixture
      def sample_data():
          return {"key": "value"}

      # test_example.py
      def test_example(sample_data):
          assert sample_data["key"] == "value"
      ```

      Run tests:
      ```bash
      pytest tests/ -v
      pytest tests/ --cov=src
      ```

  nodejs_testing:
    condition: "project_type == 'Node.js'"
    content: |
      ## Node.js Testing with Jest

      ```javascript
      // example.test.js
      describe('Example', () => {
        it('should work', () => {
          expect(true).toBe(true);
        });
      });
      ```

      Run tests:
      ```bash
      npm test
      npm run test:coverage
      ```
---

# {{PROJECT_NAME}} - Testing Strategy

## Overview

This guide provides testing patterns for {{PROJECT_NAME}}.

## Technology-Specific Testing

{{python_testing}}

{{nodejs_testing}}

## General Testing Best Practices

- Write tests first (TDD)
- Keep tests focused and isolated
- Use descriptive test names
- Aim for 80%+ code coverage

---

*Generated by Proto Gear v{{VERSION}}*
```

### Generated Output for Python Project

When `pg init` runs on a Python project, the output would be:

```markdown
# MyPythonApp - Testing Strategy

## Overview

This guide provides testing patterns for MyPythonApp.

## Technology-Specific Testing

## Python Testing with Pytest

```python
# conftest.py
import pytest

@pytest.fixture
def sample_data():
    return {"key": "value"}

# test_example.py
def test_example(sample_data):
    assert sample_data["key"] == "value"}
```

Run tests:
```bash
pytest tests/ -v
pytest tests/ --cov=src
```

## General Testing Best Practices

- Write tests first (TDD)
- Keep tests focused and isolated
- Use descriptive test names
- Aim for 80%+ code coverage

---

*Generated by Proto Gear v0.7.0*
```

Notice that:
- `{{python_testing}}` was replaced with Python-specific content
- `{{nodejs_testing}}` was removed (no match)
- Other placeholders like `{{PROJECT_NAME}}` and `{{VERSION}}` were replaced

---

## Implementation Details

### MetadataParser Class

Parses YAML frontmatter from templates:

```python
from core.proto_gear_pkg.metadata_parser import MetadataParser

# Parse template
metadata, content = MetadataParser.parse_template(template_text)

# Check if metadata exists
if metadata.name:
    # Template has metadata
    pass
```

### TemplateMetadata Class

Represents parsed metadata:

```python
# Check if requirements met
project_info = {'project_type': 'Python'}
if metadata.meets_requirements(project_info):
    print("Requirements met")

# Get conditional content
conditional = metadata.get_conditional_content(project_info)
# Returns: {'python_examples': '...content...'}
```

### Applying Conditional Content

```python
from core.proto_gear_pkg.metadata_parser import apply_conditional_content

# Replace placeholders with conditional content
result = apply_conditional_content(template_content, conditional_sections)
```

---

## Project Info Variables

The following project information is available for conditions:

| Variable | Source | Example Values |
|----------|--------|----------------|
| `project_type` | Detected from project files | `"Python"`, `"Node.js"`, `"Ruby"`, `"Unknown"` |
| `framework` | Detected from dependencies | `"Django"`, `"FastAPI"`, `"React"`, `"Vue"` |

### Detection Logic

```python
# From context in generate_project_template()
project_info = {
    'project_type': context.get('PROJECT_TYPE', 'Any'),
    'framework': context.get('FRAMEWORK', 'Unknown')
}
```

---

## Best Practices

### Template Authors

1. **Keep It Simple**
   - Use conditional sections for technology-specific examples
   - Keep general content outside frontmatter
   - Don't overuse conditions

2. **Provide Fallbacks**
   - Always include general content that works for all project types
   - Make conditional sections truly optional

3. **Test All Paths**
   - Test template with different project types
   - Verify placeholders are replaced correctly
   - Check that unreplaced placeholders are removed

4. **Document Conditions**
   - Comment complex conditions
   - Explain what triggers each section

5. **Version Your Templates**
   - Update `version` field when making breaking changes
   - Document changes in template comments

### Example: Good vs Bad

**Good** ✅

```markdown
---
conditional_sections:
  python_examples:
    condition: "project_type == 'Python'"
    content: |
      Python-specific examples here
---

# General Content (works for all)

General testing principles...

{{python_examples}}

More general content...
```

**Bad** ❌

```markdown
---
# Over-complicated conditions
conditional_sections:
  section1:
    condition: "project_type == 'Python'"
    content: "Only works for Python!"
  section2:
    condition: "project_type == 'Node.js'"
    content: "Only works for Node.js!"
  # No general content!
---

{{section1}}
{{section2}}
```

---

## Error Handling

### Malformed YAML

If frontmatter YAML is malformed, the parser gracefully falls back:

```markdown
---
invalid: yaml: syntax:
---

Content here
```

Result:
- Metadata is empty (default values)
- Full template content is used (including frontmatter)

### Missing Sections

If a placeholder has no matching conditional section:

```markdown
Template: "{{missing_section}}"
Sections: {}
Result: ""  # Placeholder removed
```

### Failed Requirements

If template requirements aren't met:

```yaml
requires:
  project_type: ["Python"]
```

For a Node.js project:
- Warning message shown
- Template still generated
- User can decide if it's useful

---

## Testing Templates with Metadata

### Unit Tests

```python
from core.proto_gear_pkg.metadata_parser import MetadataParser

def test_template_metadata():
    template = """---
name: "Test"
conditional_sections:
  python:
    condition: "project_type == 'Python'"
    content: "Python content"
---
{{python}}
"""

    metadata, content = MetadataParser.parse_template(template)

    # Test parsing
    assert metadata.name == "Test"

    # Test conditional content
    conditional = metadata.get_conditional_content({'project_type': 'Python'})
    assert 'python' in conditional
```

### Integration Tests

Test full template generation workflow:

```python
from core.proto_gear_pkg.proto_gear import generate_project_template

def test_template_generation_python():
    context = {
        'PROJECT_NAME': 'MyApp',
        'PROJECT_TYPE': 'Python',
        'VERSION': '0.7.0'
    }

    result = generate_project_template('TESTING', project_dir, context)

    assert result is not None
    content = result.read_text()
    assert 'Python' in content
    assert 'Node.js' not in content
```

---

## Migration Guide

### Converting Existing Templates

**Before** (no metadata):

```markdown
# {{PROJECT_NAME}} - Testing

Use pytest for Python or jest for Node.js.
```

**After** (with metadata):

```markdown
---
conditional_sections:
  python_info:
    condition: "project_type == 'Python'"
    content: "Use pytest for testing."
  nodejs_info:
    condition: "project_type == 'Node.js'"
    content: "Use jest for testing."
---

# {{PROJECT_NAME}} - Testing

{{python_info}}

{{nodejs_info}}
```

### Backward Compatibility

- Templates without frontmatter work as before
- No breaking changes to existing templates
- Gradual migration path

---

## Future Enhancements

### Planned Features

1. **Complex Conditions**
   - Logical operators (`&&`, `||`, `!`)
   - Multiple conditions per section

2. **More Variables**
   - `language_version`: Python 3.8+, Node 18+
   - `has_database`: true/false
   - `build_tool`: pip, npm, cargo

3. **Conditional Includes**
   - Include other template files
   - Reusable snippet library

4. **Template Validation**
   - Schema validation for frontmatter
   - Warning for unused sections
   - Linting for condition syntax

---

## Reference

### Complete Schema (JSON Schema)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "Template name"
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "Semantic version"
    },
    "requires": {
      "type": "object",
      "properties": {
        "project_type": {
          "type": "array",
          "items": {"type": "string"}
        }
      }
    },
    "conditional_sections": {
      "type": "object",
      "patternProperties": {
        ".*": {
          "type": "object",
          "properties": {
            "condition": {"type": "string"},
            "content": {"type": "string"}
          },
          "required": ["condition", "content"]
        }
      }
    }
  }
}
```

---

## See Also

- [Template Guide](../user/template-guide.md) - User guide for templates
- [PROTO-020 Plan](v0.7.0-worktrees-plan.md) - Development plan for this feature
- [Project Structure](project-structure.md) - Where templates are located
- [API Documentation](metadata_parser.py) - Implementation details

---

*Template Metadata Schema Documentation - Proto Gear v0.7.0*
*Last Updated: 2025-11-16*
