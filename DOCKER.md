# Docker Deployment Guide

## 🐳 Containerization Complete!

Your Flask Todo App has been containerized with Docker. Here's how to push it to Docker Hub:

### Prerequisites
- Docker installed and running
- Docker Hub account (https://hub.docker.com/)

### Step 1: Login to Docker Hub
```bash
docker login
```
Enter your Docker Hub username and password when prompted.

### Step 2: Build the Image (Already Done!)
```bash
docker build -t SayedSadiq/flask-todo-app:latest .
```

### Step 3: Push to Docker Hub
```bash
docker push SayedSadiq/flask-todo-app:latest
```

### Step 4: Verify on Docker Hub
Visit https://hub.docker.com/r/SayedSadiq/flask-todo-app to see your image!

---

## 🚀 Running the Container Locally

Once pushed, anyone can run your app with:

```bash
docker run -p 5000:5000 SayedSadiq/flask-todo-app:latest
```

Then visit `http://localhost:5000` in your browser.

---

## 📝 Files Added

- **Dockerfile**: Multi-stage build for production
- **.dockerignore**: Excludes unnecessary files from build context

---

## 🔧 Advanced Usage

### Run with custom port:
```bash
docker run -p 8080:5000 SayedSadiq/flask-todo-app:latest
```

### Run with environment variables:
```bash
docker run -p 5000:5000 -e FLASK_ENV=development SayedSadiq/flask-todo-app:latest
```

### Check running containers:
```bash
docker ps
```

### View logs:
```bash
docker logs <container_id>
```

---

**Image Details:**
- Base Image: `python:3.12-slim`
- Size: ~132MB
- Port: 5000
- Health Check: Enabled

## Versioned images

We tag releases using semantic versioning. The initial release is:

```bash
docker pull sayedsadiq/flask-todo-app:1.0.0
docker run -p 5000:5000 sayedsadiq/flask-todo-app:1.0.0
```

Future releases will use the `MAJOR.MINOR.PATCH` format (for example `1.0.1`, `1.1.0`, `2.0.0`).

Happy containerizing! 🎉
