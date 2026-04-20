# Branching + Feature + Release Submission

Student: Sayed Sadiq  
Course: CC302  
Date: 2026-04-20

## Features Implemented (3)

1. feature/task-descriptions-and-metadata
- Added task fields: title, description, priority, due_date, status, created_at, updated_at
- Added normalization/backfill migration from legacy plain-string tasks into structured task objects
- Preserved legacy form routes while introducing structured storage

2. feature/search-tasks
- Added backend search support with q query parameter against title + description
- Added API endpoint GET /api/tasks with query support
- Updated UI search box to call backend API

3. feature/filters-and-sorting
- Added filters: status, priority, due bucket (overdue, today, this_week)
- Added sorting: created_at, due_date, priority, title
- Added sort order toggle (asc/desc)
- Updated UI controls and backend query builder

## Code Evidence

- Backend data model + migration/backfill + API routes: [app/routes.py](app/routes.py#L8)
- Query filtering/sorting logic: [app/routes.py](app/routes.py#L145)
- API endpoints: [app/routes.py](app/routes.py#L223)
- UI controls for search/filter/sort: [app/templates/index.html](app/templates/index.html#L40)
- Frontend API integration and interactions: [app/static/js/app.js](app/static/js/app.js#L20)
- Automated API lifecycle test: [tests/test_app.py](tests/test_app.py#L31)
- Smoke validations for metadata/search/filter behavior: [tests/smoke_test.py](tests/smoke_test.py#L55)

## Verification Output

Executed:

```bash
pytest -q
```

Result:

```text
3 passed in 0.15s
```

## Part A: Branch Setup (Commands)

Run from main:

```bash
git checkout main
git pull origin main
git checkout -b dev
git push -u origin dev

# Create required feature branches from dev
git checkout dev
git checkout -b feature/task-descriptions-and-metadata
git push -u origin feature/task-descriptions-and-metadata

git checkout dev
git checkout -b feature/search-tasks
git push -u origin feature/search-tasks

git checkout dev
git checkout -b feature/filters-and-sorting
git push -u origin feature/filters-and-sorting

# Deliverable A
git branch -a
```

Add screenshot of branch list from GitHub or output of git branch -a.

## Part B: Feature PR Workflow (Commands + Links)

For each feature branch:

```bash
# example for metadata feature
git checkout feature/task-descriptions-and-metadata
# stage only feature files
git add app/routes.py tests/smoke_test.py tests/test_app.py
git commit -m "feat: add task metadata and migration backfill"
git push

gh pr create \
  --base dev \
  --head feature/task-descriptions-and-metadata \
  --title "feat: task descriptions and metadata" \
  --body "Adds description, priority, due_date, status, updated_at and migration backfill for legacy todos."
```

Repeat for:
- feature/search-tasks
- feature/filters-and-sorting

When PRs are approved/green:

```bash
gh pr merge <PR_NUMBER> --merge --delete-branch
```

Fill Deliverable B:
- PR 1 (feature -> dev): <ADD_LINK>
- PR 2 (feature -> dev): <ADD_LINK>
- PR 3 (feature -> dev): <ADD_LINK>
- Short descriptions: included above
- Screenshot evidence: add UI screenshots for each feature

## Part C: Merge dev into main

```bash
git checkout dev
git pull origin dev
gh pr create \
  --base main \
  --head dev \
  --title "release: merge dev into main for v0.1.0" \
  --body "Release PR with metadata, search, filters and sorting features."
```

Merge after checks pass:

```bash
gh pr merge <DEV_TO_MAIN_PR_NUMBER> --merge
```

Fill Deliverable C:
- PR link (dev -> main): <ADD_LINK>
- Screenshot showing merged changes on main: <ADD_SCREENSHOT>

## Part D: Container Build + SemVer Push

Version for this assignment: 0.1.0

DockerHub path:

```bash
docker build -t <dockerhub_user>/todo-saas:0.1.0 .
docker push <dockerhub_user>/todo-saas:0.1.0
docker tag <dockerhub_user>/todo-saas:0.1.0 <dockerhub_user>/todo-saas:latest
docker push <dockerhub_user>/todo-saas:latest
```

ECR path:

```bash
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com
docker build -t <account>.dkr.ecr.<region>.amazonaws.com/todo-saas:0.1.0 .
docker push <account>.dkr.ecr.<region>.amazonaws.com/todo-saas:0.1.0
```

Fill Deliverable D:
- Registry screenshot showing 0.1.0 (and latest if DockerHub): <ADD_SCREENSHOT>
- Command output proving push success: <ADD_OUTPUT>

## Part E: GitHub Tag + Release

```bash
git checkout main
git pull origin main
git tag v0.1.0
git push origin v0.1.0

gh release create v0.1.0 \
  --title "v0.1.0" \
  --notes "Features:\n1) Task descriptions + metadata\n2) Search tasks\n3) Filters + sorting"
```

Fill Deliverable E:
- GitHub Release link: <ADD_LINK>

## Submission Checklist

- [ ] Branch list screenshot/output included
- [ ] 3 PR links (feature -> dev)
- [ ] 1 PR link (dev -> main)
- [ ] DockerHub/ECR screenshot with tags
- [ ] GitHub Release link
- [ ] Short reflection paragraph

## Reflection (Branching + Merging)

This assignment improved my practical workflow discipline: I separated work using feature branches from dev, opened focused pull requests, and merged safely into integration before releasing to main. I also practiced release hygiene by tagging with semantic versioning and mapping code changes to a container image version. The process made changes easier to review, reduced integration risk, and produced a traceable release history from feature implementation to deployable artifact.
