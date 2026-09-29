# Project Administration

Projects are workspace-owned administrative records. Every project has an immutable workspace, immutable code, creator provenance, mutable display metadata, a lifecycle status, and a default validation-profile assignment.

## Statuses

- `active`: normal creation and production work.
- `on_hold`: retained and visible while production work is paused.
- `archived`: retained for immutable history and read access. New assets are rejected.

Archiving never deletes assets, streams, versions, files, validation runs, or validation jobs. A project can be restored by an authorized administrator through `PATCH /api/v1/projects/{project_id}` with status `active` or `on_hold`.

## Filtering

`GET /api/v1/projects` accepts `workspace_id`, `status`, `search`, and `created_by_user_id`. All filters remain constrained by the authenticated user's workspace memberships.

## Default validation profile

`default_validation_profile` is a profile-name assignment used as the project policy default. The profile implementation remains in the validation domain; the project stores only the stable profile name.

## Authorization

Viewer and Contributor roles may read accessible projects. Administrator and Owner roles hold `manage_projects` and may create, update, archive, restore, and change profile assignments. The service remains authoritative even if a desktop control is hidden.
