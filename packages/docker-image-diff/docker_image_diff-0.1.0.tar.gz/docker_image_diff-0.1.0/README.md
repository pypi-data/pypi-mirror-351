# docker-image-diff

A tool to generate and apply diffs between Docker image tar archives, allowing you to package only the updated parts for offline updates.

## Features

* **Diff**: Create a diff tar containing only files added or changed between two Docker image tar files.
* **Merge**: Merge a diff tar back into a base tar to reconstruct the updated image.
* Prints size summary for base, new, and diff archives.

## Requirements

* Python 3.10 or above
* Standard library only (no external dependencies)

## Installation

If published on PyPI, install with:

```bash
pip install docker-image-diff
```

Or to use from source:

```bash
git clone <repo-url>
cd docker-image-diff
pip install .
```

## Usage

```bash
# Generate a diff archive:
dockerdiff diff --base <base tar path> --new <new tar path> --output <diff tar path>

# Merge a diff archive into the base to create the updated image:
dockerdiff merge --base <base tar path> --diff <diff tar path> --output <new tar path>
```

### Examples

```bash
# Create a diff between two images:
$ dockerdiff diff --base ubuntu_old.tar --new ubuntu_new.tar --output ubuntu_diff.tar

# Reconstruct the updated image on an offline server:
$ dockerdiff merge --base ubuntu_old.tar --diff ubuntu_diff.tar --output ubuntu_reconstructed.tar
```

## Output

After running a command, the tool prints a summary of the archive sizes:

```
Base image size: 123.45 MB
New image size: 130.67 MB
Diff image size: 7.22 MB
```

Use these numbers to verify that only the changed content was packaged.

## Author

Junghyun Kwon

## Version

0.1.0

## License

This project is licensed under the Apache License 2.0.
