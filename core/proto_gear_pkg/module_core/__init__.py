"""Department-agnostic module core.

The reusable engine every departmental module runs on (ADR-001 Phase B):
capability schema + index building, context sync, discovery, drift diagnostics,
and the module manifest contract. Nothing here is engineering-specific — the
engineering module (and any future department) consumes these through the same
interfaces.
"""
