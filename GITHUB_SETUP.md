# Push OrgChartAI to GitHub

Your project is already initialized with Git and has an initial commit. Follow these steps to put it on GitHub.

---

## 1. Create a new repository on GitHub

1. Open **https://github.com/new**
2. Set **Repository name** (e.g. `OrgChartAI`).
3. Choose **Public** or **Private**.
4. **Do not** initialize with a README, .gitignore, or license (you already have these).
5. Click **Create repository**.

---

## 2. Add the remote and push

In a terminal, from your project folder:

```powershell
cd C:\Users\sumit\Documents\OrgChartAI

# Add your GitHub repo as "origin" (replace YOUR_USERNAME and YOUR_REPO with yours)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Push your "master" branch to GitHub
git push -u origin master
```

**Example:** If your GitHub user is `sumit` and the repo is `OrgChartAI`:

```powershell
git remote add origin https://github.com/sumit/OrgChartAI.git
git push -u origin master
```

---

## 3. If GitHub uses "main" instead of "master"

If the new repo was created with a default branch `main` and you want to use that:

```powershell
# Rename local branch to main
git branch -M main

# Push to main
git push -u origin main
```

---

## 4. Authentication

- **HTTPS:** Git will ask for your GitHub username and a **Personal Access Token** (not your account password). Create one at: **GitHub → Settings → Developer settings → Personal access tokens**.
- **SSH:** If you use SSH keys:
  ```powershell
  git remote set-url origin git@github.com:YOUR_USERNAME/YOUR_REPO.git
  git push -u origin master
  ```

---

## What’s already done

- `git init`  
- `.gitignore` (including `.env`, `venv/`, `node_modules/`, `.cursor/`, secrets)  
- Initial commit with 224 files  
- `.gitignore` updated to exclude `.cursor/`

---

## Useful commands later

```powershell
git status
git add .
git commit -m "Your message"
git push
```
