# PyPI Publishing Instructions for sixty-nuts

## Pre-flight Checklist ✅

### Required Files (Now Complete)

- [x] `LICENSE` - MIT License
- [x] `README.md` - Comprehensive documentation
- [x] `CHANGELOG.md` - Version history
- [x] `pyproject.toml` - Complete package metadata with build system

### TODO Before Publishing

1. **Update Author Information** in `pyproject.toml`:
   - Replace "Your Name" with your actual name
   - Replace "<your.email@example.com>" with your email
   - Update GitHub URLs to your actual repository

2. **Create PyPI Account**:
   - Register at <https://pypi.org/account/register/>
   - Enable 2FA (recommended)
   - Generate API token at <https://pypi.org/manage/account/token/>

3. **Configure Authentication** (create `~/.pypirc`):

   ```ini
   [pypi]
   username = __token__
   password = pypi-AgEIcHlwaS5vcmc...your-token-here...
   ```

4. **Install Build Tools**:

   ```bash
   pip install --upgrade build twine
   ```

## Building and Publishing

### 1. Run Tests (Recommended)

```bash
pytest tests/
mypy sixty_nuts/
ruff check sixty_nuts/
```

### 2. Build the Package

```bash
python -m build
```

This creates:

- `dist/sixty_nuts-0.0.1-py3-none-any.whl` (wheel)
- `dist/sixty_nuts-0.0.1.tar.gz` (source)

### 3. Test with TestPyPI (Optional but Recommended)

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ sixty-nuts
```

### 4. Upload to PyPI

```bash
python -m twine upload dist/*
```

### 5. Verify Installation

```bash
pip install sixty-nuts
```

## Post-Publishing

1. **Create Git Tag**:

   ```bash
   git tag -a v0.0.1 -m "Initial release"
   git push origin v0.0.1
   ```

2. **Create GitHub Release**:
   - Go to your repo's releases page
   - Create release from tag v0.0.1
   - Copy CHANGELOG content for release notes

3. **Update for Next Version**:
   - Bump version in `pyproject.toml`
   - Add new "Unreleased" section in CHANGELOG.md
   - Commit changes

## Version Management

Consider using a tool like `bump2version` or `poetry-version` for automated version bumping:

```bash
pip install bump2version
# Create .bumpversion.cfg
```

## Continuous Deployment

Consider setting up GitHub Actions for automated publishing:

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Build and publish
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        pip install build twine
        python -m build
        python -m twine upload dist/*
```

## Important Notes

- The package name on PyPI is `sixty-nuts` (with hyphen)
- Import name in Python is `sixty_nuts` (with underscore)
- Make sure to test thoroughly before publishing - you cannot reuse version numbers!
- Consider using pre-release versions (0.0.1a1, 0.0.1b1, 0.0.1rc1) for testing
