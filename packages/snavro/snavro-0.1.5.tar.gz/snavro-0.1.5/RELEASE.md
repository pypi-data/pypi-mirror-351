# Release Process

This project uses **git flow** for releases with automatic version management from git tags using `setuptools-scm`.

## Git Flow Setup

### Initial Setup

1. **Install git flow** (if not already installed):
   ```bash
   # macOS
   brew install git-flow-avh
   
   # Ubuntu/Debian
   sudo apt-get install git-flow
   
   # Windows
   # Download from: https://github.com/petervanderdoes/gitflow-avh
   ```

2. **Initialize git flow** in your repository:
   ```bash
   git flow init
   ```
   
   Use these branch names (defaults):
   - Production releases: `main`
   - Next release development: `develop`
   - Feature branches: `feature/`
   - Release branches: `release/`
   - Hotfix branches: `hotfix/`
   - Support branches: `support/`

## Release Workflow

### 1. Feature Development

```bash
# Start a new feature
git flow feature start my-new-feature

# Work on your feature...
git add .
git commit -m "Add new feature"

# Finish the feature (merges to develop)
git flow feature finish my-new-feature
```

### 2. Preparing a Release

```bash
# Start a release branch (use semantic versioning)
git flow release start 1.2.0

# Make any final adjustments, update CHANGELOG.md
git add .
git commit -m "Prepare release 1.2.0"

# Finish the release (merges to main and develop, creates tag)
git flow release finish 1.2.0
```

### 3. Publishing the Release

After finishing a git flow release:

```bash
# Push all branches and tags
git push origin main
git push origin develop
git push origin --tags
```

**This will automatically trigger the PyPI publication workflow when the tag is pushed!**

### 4. Optional: Create GitHub Release

You can optionally create a GitHub release for better documentation:

1. Go to your GitHub repository
2. Click "Releases" → "Create a new release"
3. Choose the tag that was already created (e.g., `1.2.0`)
4. Fill in the release title and description
5. Click "Publish release"

Note: The PyPI publication already happened when you pushed the tag, so this is just for documentation.

### 5. Hotfixes

For urgent fixes to production:

```bash
# Start a hotfix from main
git flow hotfix start 1.2.1

# Fix the issue
git add .
git commit -m "Fix critical bug"

# Finish the hotfix (merges to main and develop, creates tag)
git flow hotfix finish 1.2.1

# Push everything
git push origin main
git push origin develop
git push origin --tags
```

## Version Management

### Automatic Versioning

- **No manual version editing** in `pyproject.toml`
- Version is automatically derived from git tags using `setuptools-scm`
- The version follows this pattern:
  - Tagged releases: `1.2.0`
  - Development builds: `1.2.0.dev5+g1234567` (5 commits since tag, git hash 1234567)

### Version Scheme

We use **semantic versioning** (semver):
- `MAJOR.MINOR.PATCH` (e.g., `1.2.0`)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Checking Current Version

```bash
# Check version from git
python -m setuptools_scm

# Check installed package version
python -c "import snavro; print(snavro.__version__)"
```

## CI/CD Pipeline

### Automated Workflows

1. **CI Pipeline** (`.github/workflows/ci.yml`):
   - Runs on every push to `main` and `develop`
   - Tests across Python 3.8-3.12
   - Code quality checks (Black, mypy)

2. **Release Pipeline** (`.github/workflows/publish.yml`):
   - Triggers when a GitHub release is published
   - Runs full test suite
   - Builds package with version from git tag
   - Publishes to PyPI automatically

### Manual Testing Before Release

```bash
# Install in development mode
pip install -e ".[dev]"

# Run all checks locally
pytest tests/ -v
black --check snavro/ tests/
mypy snavro/

# Build and check package
python -m build
twine check dist/*
```

## Branch Protection

Recommended GitHub branch protection rules:

### Main Branch
- Require pull request reviews
- Require status checks to pass
- Require branches to be up to date
- Include administrators

### Develop Branch
- Require status checks to pass
- Require branches to be up to date

## Example Release Cycle

```bash
# 1. Start working on features
git checkout develop
git flow feature start user-authentication
# ... work on feature ...
git flow feature finish user-authentication

git flow feature start data-export
# ... work on feature ...
git flow feature finish data-export

# 2. Prepare release
git flow release start 1.3.0
# Update CHANGELOG.md, final testing
git add CHANGELOG.md
git commit -m "Update changelog for 1.3.0"
git flow release finish 1.3.0

# 3. Push everything (this triggers PyPI publication!)
git push origin main
git push origin develop
git push origin --tags

# 4. Optionally create GitHub release for documentation
# (PyPI publication already happened automatically)
```

## Troubleshooting

### Version Not Detected
```bash
# Ensure you have tags and full git history
git fetch --tags --unshallow

# Check setuptools-scm can detect version
python -m setuptools_scm
```

### Failed PyPI Upload
- Check that the tag follows semantic versioning
- Ensure the version doesn't already exist on PyPI
- Verify GitHub secrets are configured correctly

### Git Flow Issues
```bash
# If git flow gets confused, you can manually merge:
git checkout main
git merge --no-ff release/1.2.0
git tag 1.2.0
git checkout develop
git merge --no-ff release/1.2.0
git branch -d release/1.2.0
``` 