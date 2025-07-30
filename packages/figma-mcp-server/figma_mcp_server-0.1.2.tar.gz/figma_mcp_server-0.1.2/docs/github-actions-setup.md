# GitHub Actions Setup for Automated Publishing

This document explains how to set up automated publishing to PyPI using GitHub Actions.

## Prerequisites

1. Your package is already published to PyPI (at least once manually)
2. You have a PyPI API token with upload permissions for your package
3. Your repository is hosted on GitHub

## Setup Steps

### 1. Create PyPI API Token

1. Go to [PyPI Account Settings](https://pypi.org/manage/account/token/)
2. Click "Add API token"
3. Give it a name like "figma-mcp-server-github-actions"
4. Set scope to "Entire account" or specific to your project
5. Copy the token (starts with `pypi-`)

### 2. Add Secret to GitHub Repository

1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `PYPI_API_TOKEN`
5. Value: Paste your PyPI API token
6. Click "Add secret"

### 3. How the Workflow Works

The workflow (`.github/workflows/publish.yml`) will automatically:

- **On Release**: Trigger when you create a GitHub release
- **Manual Trigger**: Allow manual runs with optional version override
- **Build**: Create source and wheel distributions
- **Publish**: Upload to PyPI using your API token

### 4. Publishing a New Version

#### Option A: Create a GitHub Release (Recommended)

1. Update version in `pyproject.toml` and `figma_mcp_server/cli.py`
2. Commit and push changes
3. Go to GitHub → Releases → "Create a new release"
4. Create a new tag (e.g., `v0.1.2`)
5. Fill in release notes
6. Click "Publish release"
7. GitHub Actions will automatically build and publish to PyPI

#### Option B: Manual Workflow Trigger

1. Go to GitHub → Actions → "Publish to PyPI"
2. Click "Run workflow"
3. Optionally specify a version number
4. Click "Run workflow"

### 5. Monitoring

- Check the Actions tab to see workflow runs
- View logs for any build or publish errors
- Verify the new version appears on PyPI

## Security Notes

- The API token is stored securely as a GitHub secret
- Only repository maintainers can trigger the workflow
- The token is only exposed during the publish step
- Consider using PyPI's "Trusted Publishing" for even better security (OIDC-based, no tokens needed)

## Troubleshooting

### Common Issues

1. **"Invalid credentials"**: Check that your PyPI API token is correct
2. **"File already exists"**: Version already published, increment version number
3. **"Permission denied"**: API token doesn't have upload permissions for this package

### Getting Help

- Check the GitHub Actions logs for detailed error messages
- Verify your PyPI token has the correct permissions
- Ensure version numbers are properly updated before publishing 