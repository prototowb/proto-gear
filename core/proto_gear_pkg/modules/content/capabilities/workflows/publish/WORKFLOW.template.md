# Publish Content

Take an approved content item live on its channel — with a mandatory human
approval gate before anything goes public.

## When to use

An item in `CONTENT_QUEUE.md` has cleared `review` and is ready to schedule or
publish. Triggers: _publish, go live, ship post, release content_.

## Supervision gate — `content-approval`

**This gate is mandatory and human.** An item may not move from `review` to
`scheduled`/`published` until a human editor has approved copy, brand fit, and
legal, and their name is recorded in the queue's **Approved by** column. Silence
is never consent (PROJECT_SPECIFICATIONS.md §4).

## Steps

1. Confirm the item is in `review` and all assets are attached.
2. Present the final copy + channel + target date to the human editor.
3. **Gate:** record the editor's approval in **Approved by**. If they decline or
   raise an undeclared concern, stop and record it in `SESSION_HANDOFF.md`.
4. Move the item to `scheduled` (or `published`) and append it to the Published
   Log with the permalink.

## Outputs

- A published (or scheduled) content item, with an auditable approval trail.
