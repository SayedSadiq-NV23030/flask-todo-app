# feature/task-descriptions-and-metadata

This branch documents the `task-descriptions-and-metadata` feature implementation already merged into `dev`.

What was implemented:
- UI: added `description`, `priority`, and `due_date` controls in the add/edit modal and quick-add input.
- JS: client-side persistence to `localStorage`, priority badges, and filters.
- Files: `app/templates/index.html`, `app/static/js/app.js`, `app/static/css/style.css`.

Reference commits:
- feature branch commit: 13a76b2 (origin/feature/task-descriptions)

How to test:
1. Open the app and add a task with a description and priority via the Add modal or quick-add.
2. Verify badge and that filtering by priority works.

