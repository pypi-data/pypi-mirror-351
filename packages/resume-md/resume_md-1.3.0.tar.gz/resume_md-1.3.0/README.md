[![Build & Release](https://github.com/SamCullin/resume-md/actions/workflows/publish.yml/badge.svg)](https://github.com/SamCullin/resume-md/actions/workflows/publish.yml)
[![CI](https://github.com/SamCullin/resume-md/actions/workflows/ci.yml/badge.svg)](https://github.com/SamCullin/resume-md/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/resume-md.svg)](https://badge.fury.io/py/resume-md)
[![GitHub Release](https://img.shields.io/github/v/release/SamCullin/resume-md)](https://github.com/SamCullin/resume-md/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/SamCullin/resume-md/graphs/commit-activity)
[![Downloads](https://img.shields.io/pypi/dm/resume-md.svg)](https://pypi.org/project/resume-md/)
[![GitHub issues](https://img.shields.io/github/issues/SamCullin/resume-md.svg)](https://github.com/SamCullin/resume-md/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat)](https://makeapullrequest.com)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-%23FE5196?logo=conventionalcommits&logoColor=white)](https://conventionalcommits.org)
[![semantic-release: angular](https://img.shields.io/badge/semantic--release-angular-e10079?logo=semantic-release)](https://github.com/semantic-release/semantic-release)

# Markdown Resume Generator

[!['Buy Me A Coffee'](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/samcullin)

A simple, lightweight tool to convert markdown-formatted resumes into beautiful, print-ready HTML documents styled with Tailwind CSS.

![Resume-MD Example](https://raw.githubusercontent.com/SamCullin/resume-md/main/example/image.png)


## Features

- Convert Markdown to styled HTML resumes
- Modern design with Tailwind CSS
- Automatic header detection for contact information
- ATS-friendly hidden information for keyword optimization
- Print-optimized layout with page break support
- No external dependencies (Python standard library only)
- Responsive design for both screen and print

## Installation

### From PyPI

```bash
pip install resume-md
```

### From Source

```bash
git clone git@github.com:SamCullin/resume-md.git
cd resume-md
pip install -e .
```

### Development Setup

To set up the development environment:

```bash
git clone git@github.com:SamCullin/resume-md.git
cd resume-md
pip install -e ".[dev]"
```

## Usage

### Basic Usage

```bash
resume-md --input your_resume.md
```

This will generate an HTML file with the same name as your input file (e.g., your_resume.html).

### Command Line Options

```bash
resume-md --help
```

Available options:

- `--input`, `-i`: Path to input markdown file (default: resume.md)
- `--output`, `-o`: Path to output HTML file (default: <input_name>.html)
- `--template`, `-t`: Path to HTML template file (use built-in template if not specified)
- `--version`, `-v`: Show version information and exit

### Using as a Library

```python
from resume_md.tokenizer import MarkdownTokenizer, read_markdown_file
from resume_md.component_factory import tokens_to_components
from resume_md.renderer import Renderer

# Read and tokenize markdown
markdown_text = read_markdown_file("resume.md")
tokenizer = MarkdownTokenizer(markdown_text)
tokens = tokenizer.tokenize()

# Convert tokens to components and render to HTML
components = tokens_to_components(tokens)
renderer = Renderer()
rendered = renderer.render_components(components)

# Access the header and content HTML
header_html = rendered["header"]
content_html = rendered["content"]
```

## Markdown Format

The resume-md tool supports a specific markdown format designed for resumes. For examples, see:

- [Example 1](example/example1.md) - Basic resume format with tables
- [Example 2](example/example2.md) - Alternative resume format with lists
- [Page Break Example](example/page_break_test.md) - Example showing page break usage
- [ATS-Info Example](example/ats_info_test.md) - Example showing ATS-specific information usage

### Page Breaks

You can force a page break in your resume using the special markdown comment syntax:

```markdown
This is content on the first page.

[page-break]: # 

This content will appear on a new page.
```

When the document is printed, a page break will be inserted at this location.

### ATS-Specific Information

You can include ATS (Applicant Tracking System) specific information that will be hidden from the visual display but accessible to text extraction systems. This is useful for including additional keywords, skills, or metadata that ATS systems can parse.

```markdown
[ats-info]: # Skills: Python, JavaScript, TypeScript, React, Node.js
[ats-info]: # + Tools: Git, GitHub, VS Code, Docker, Kubernetes


[ats-info]: # + Certifications: AWS Certified Solutions Architect
[ats-info]: # + Languages: English (Native), Spanish (Fluent)
```
ATS Export Example:
```markdown
Skills: Python, JavaScript, TypeScript, React, Node.js + Tools: Git, GitHub, VS Code, Docker, Kubernetes + Certifications: AWS Certified Solutions Architect + Languages: English (Native), Spanish (Fluent)
```

The ATS-info comments follow the format: `[ats-info]: # Content`

This information will be rendered as hidden HTML elements that are:
- Invisible to users viewing the resume
- Accessible to ATS systems for keyword extraction


> [!NOTE]
> The ATS-info comments once exported to pdf will collapse to a single line.
> This is because the pdf format cannot support fonts below 1.5pt and sees these smaller lines as a single line.
> Keep this in mind when formatting your ats-info comments.






**Example usage in a resume:**

```markdown
# John Doe
Email: john@example.com | Phone: (555) 123-4567

[ats-info]: # Skills: Python, JavaScript, Machine Learning, Data Analysis
[ats-info]: # Tools: Git, Docker, AWS, Jenkins, Terraform
[ats-info]: # Frameworks: React, Django, Flask, Express.js

## Professional Experience
...
```

## Development

### Running Tests

```bash
pytest
# With coverage
pytest --cov=resume_md
```

### Code Formatting

```bash
black resume_md
isort resume_md
```

## Project Structure

- `resume_md/`: Main package
  - `__init__.py`: Package initialization
  - `main.py`: CLI entry point
  - `tokenizer.py`: Markdown tokenizer
  - `components.py`: Component data classes
  - `component_factory.py`: Converts tokens to components
  - `renderer.py`: Renders components as HTML
  - `template.html`: HTML template
- `tests/`: Test cases
- `.github/workflows/`: CI/CD workflows

## Repository

- **GitHub:** [https://github.com/SamCullin/resume-md](https://github.com/SamCullin/resume-md)
- **SSH:** `git@github.com:SamCullin/resume-md.git`

## License

MIT 