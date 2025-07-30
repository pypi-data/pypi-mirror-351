## OAT Tools

OAT Tools is a CLI tool written in Python. It is installed as executable `oat` using `uv tool install` or as one-off run using `uvx`. The tool has been designed to help you manage Markdown files written to learning diary written using OAT Spec (as described in [Oppimispäiväkirja 101](https://sourander.github.io/oat)).

The idea is to keep the tool minimalistic and simple. It will handle the following tasks:

* Detect unused references (Footnotes in Vancouver style)
* Order references by first appearance
* Remove unused references
* Count words in Markdown files, excluding code blocks, footnotes and urls.

## Installation

You can install OAT Tools using `uv`:

```bash
uv tool install oat-tools
```
Or you can run it as a one-off command using `uvx`:

```bash
uvx oat-tools
```

## Usage

### References

To detect unused references, order them by first appearance, and remove unused references, you can use the following command:

```bash
# Abstract
oat references [--fix] <FILE...>

# Concrete example (check diary, another and all Markdown files in docs directory)
oat references check diary.md another.md docs/**/*.md

# Concrete example (fix the same files)
oat references fix diary.md another.md docs/**/*.md
```

Where `<FILE...>` is any number or Markdown files you want to process. You can use wildcards since your shell will expand them. Note that the `--fix` option will modify the files in place, so use it with caution. It is recommended to run the command without `--fix` first to see what changes will be made. Any unused references will be REMOVED, which is a destructive operation. It is recommended to run these commands after a Git commit, so you can easily revert the changes if needed, and can also review the changes using various diff tools.

Terminology used in this tool:

* **appearance**: Means that the `[^ref]` is used in the body text.
* **reference**: Means that the `[^ref]:` is defined in the footnotes section.
* **unused**: The `[^ref]:` is defined in the footnotes section, but has no appearance in the body text.
* **orphan**: Opposite situation. The `[^ref]` is used in the body text without a corresponding `[^ref]:`.

### Word Count

To count words in Markdown files, excluding code blocks, footnotes, and URLs, you can use the following command:

```bash
# Abstract
oat wordcount <FILE...>

# Concrete example
oat wordcount diary.md another.md docs/**/*.md
```

Where `<FILE...>` is any number of Markdown files you want to process. Again, you can use wildcards.

## Development and Releases

This section is intended for maintainers of the project.

### Releasing a New Version

To release a new version of OAT Tools, follow these steps:

1. **Implement or modify features and tests**
   - Make your changes to the codebase
   - Add or update corresponding tests
   - Ensure your code follows the project's coding standards

2. **Run tests to ensure everything works**
   ```bash
   uv run pytest
   ```
   Make sure all tests pass before proceeding.

3. **Update the version number**
   - Edit `pyproject.toml` and increment the version number in the `[project]` section
   - Follow [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`
     - **PATCH**: Bug fixes and small improvements
     - **MINOR**: New features that are backwards compatible
     - **MAJOR**: Breaking changes

4. **Commit and push your changes**
   ```bash
   git add .
   git commit -m "Release version X.Y.Z"
   git push origin main
   ```

5. **Create and push a version tag**
   ```bash
   # Create a tag (replace X.Y.Z with your version number)
   git tag vX.Y.Z
   
   # Push the tag to trigger the release workflow
   git push origin vX.Y.Z
   ```

6. **Monitor the release**
   - The GitHub Actions workflow will automatically build and publish the package to PyPI
   - Check the [Actions tab](../../actions) in GitHub to ensure the release completed successfully
   - Verify the new version appears on [PyPI](https://pypi.org/project/oat-tools/)

### Example Release Commands

Here's a complete example for releasing version 1.0.1:

```bash
# After making your changes and updating pyproject.toml version to "1.0.1"
uv run pytest                    # Ensure tests pass
git add .
git commit -m "Release version 1.0.1"
git push origin main
git tag v1.0.1
git push origin v1.0.1
```

The automated workflow will handle the rest!