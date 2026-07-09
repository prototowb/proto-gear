"""Content department module — the second module implementation.

Module #2 of the agency OS (PROJECT_SPECIFICATIONS.md §2). It exists to *prove
the module contract*: shipped as a pure manifest + templates + design doc, it
must be discovered, loaded, and audited by the department-agnostic core with no
core edits (ADR-001 Phase C entry, action item 7).

The content department's state surface is a content queue
(``CONTENT_QUEUE.md``) — draft → review → scheduled → published — with a human
approval gate before publish. See ``docs/dev/content-module-design.md`` for the
full design and the core seams this module surfaces.
"""
