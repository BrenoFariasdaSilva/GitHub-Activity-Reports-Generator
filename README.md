<div align="center">
  
# [GitHub-Activity-Reports-Generator.](https://github.com/BrenoFariasdaSilva/GitHub-Activity-Reports-Generator) <img src="https://github.com/BrenoFariasdaSilva.png"  width="3%" height="3%">

</div>

<div align="center">
  
---

This project is a **GitHub Activity Reports Generator** that collects and organizes information about issues, sub-issues, pull requests (PRs), and commits from specified repositories within a defined date range.  
It saves raw JSON responses to `./responses/` and generates **Quarto Markdown reports** grouped by author, with outputs in PDF, DOCX, and QMD formats stored in `./reports/`.
  
---

</div>

<div align="center">

![GitHub Code Size in Bytes](https://img.shields.io/github/languages/code-size/BrenoFariasdaSilva/GitHub-Activity-Reports-Generator)
![GitHub Commits](https://img.shields.io/github/commit-activity/t/BrenoFariasDaSilva/GitHub-Activity-Reports-Generator/main)
![GitHub Last Commit](https://img.shields.io/github/last-commit/BrenoFariasdaSilva/GitHub-Activity-Reports-Generator)
![GitHub Forks](https://img.shields.io/github/forks/BrenoFariasDaSilva/GitHub-Activity-Reports-Generator)
![GitHub Language Count](https://img.shields.io/github/languages/count/BrenoFariasDaSilva/GitHub-Activity-Reports-Generator)
![GitHub License](https://img.shields.io/github/license/BrenoFariasdaSilva/GitHub-Activity-Reports-Generator)
![GitHub Stars](https://img.shields.io/github/stars/BrenoFariasdaSilva/GitHub-Activity-Reports-Generator)
![wakatime](https://wakatime.com/badge/github/BrenoFariasdaSilva/GitHub-Activity-Reports-Generator.svg)

</div>

<div align="center">
  
![RepoBeats Statistics](https://repobeats.axiom.co/api/embed/85ae4e5b591ce5aebee352186f43f84ec68519b8.svg "Repobeats analytics image")

</div>

## Table of Contents
- [GitHub-Activity-Reports-Generator. ](#github-activity-reports-generator-)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Features](#features)
  - [TODO / Roadmap](#todo--roadmap)
  - [Requirements](#requirements)
  - [Setup](#setup)
    - [1. Install Python](#1-install-python)
      - [Linux](#linux)
      - [macOS](#macos)
      - [Windows](#windows)
    - [2. Install `make` utility](#2-install-make-utility)
      - [Linux](#linux-1)
      - [macOS](#macos-1)
      - [Windows](#windows-1)
    - [3. Clone the repository](#3-clone-the-repository)
    - [4. Virtual environment (strongly recommended)](#4-virtual-environment-strongly-recommended)
    - [5. Install dependencies](#5-install-dependencies)
    - [6. Environment Variables Configuration](#6-environment-variables-configuration)
      - [Full list of environment variables](#full-list-of-environment-variables)
    - [main.py configuration](#mainpy-configuration)
  - [Usage](#usage)
  - [Results](#results)
    - [Example structure](#example-structure)
    - [Convert QMD to other formats](#convert-qmd-to-other-formats)
  - [Contributing](#contributing)
  - [Collaborators](#collaborators)
  - [License](#license)
    - [Apache License 2.0](#apache-license-20)

## Introduction

The **GitHub Activity Reports Generator** is a Python-based tool designed to streamline the process of collecting and analyzing contributions across multiple GitHub repositories. It connects to the GitHub API, retrieves issues, sub-issues, pull requests, and commits within a specified date range, and organizes the data per author. The tool saves raw JSON responses for traceability and produces structured, per-author reports in Quarto Markdown (`.qmd`) format, which can be rendered into PDF, DOCX, or other formats. This enables teams, project managers, and educators to gain clear insights into individual and team contributions, track progress over time, and maintain accurate records of repository activity.

## Features

- Collects **issues** (created and updated) within a given date range.  
- Fetches **sub-issues** (via GitHub API).  
- Extracts **PRs strictly linked to issues** (via timeline).  
- Gathers **commits** from PRs and direct commit searches.  
- Maps GitHub usernames to **real author names**.  
- Saves **raw JSON responses**.  
- Generates **Quarto Markdown reports per author** (qmd, that can be converted to PDF, DOCX, etc.).  
- Supports **multiple repositories**, automatically sorted alphabetically.  
- Deduplicates commits by SHA.  
- Includes sound notification when finished.  

## TODO / Roadmap

The following improvements and enhancements are planned for this project. These items are also documented in the `main.py` header description:

- **Organize responses directory** → Create subdirectories per repository and separate folders for each issue, storing all related content inside.  
- **Incremental data fetching** → Avoid re-fetching all data every time; only retrieve new or updated items.  
- **GraphQL support** → Implement GraphQL queries for `/Projects` content to improve efficiency and flexibility.  

## Requirements

- Python **3.9 or higher**  
- A valid GitHub **Personal Access Token (Classic)** with at least `repo` and `read:org` scopes  
- `make` utility installed on your system  
- Internet connection (to fetch data from GitHub API)  
- [Quarto CLI](https://quarto.org/) installed system-wide (required for report rendering)  
- [Quarto PDF dependencies](https://quarto.org/docs/output-formats/pdf/) installed (for PDF output)

Dependencies in the `requirements.txt` include:
- `certifi` → Provides trusted CA certificates for secure HTTPS requests.  
- `charset-normalizer` → Handles encoding/decoding of response text when fetching from the GitHub API.  
- `colorama` → Enables colored terminal output for status and progress messages.  
- `DateTime` → Simplifies working with dates and times (used alongside `pytz`).  
- `idna` → Ensures proper handling of internationalized domain names in URLs.  
- `python-dotenv` → Loads environment variables from a `.env` file (e.g., GitHub token).  
- `pytz` → Provides time zone support for date/time handling and conversions.  
- `requests` → Core HTTP library used to interact with the GitHub API.  
- `setuptools` → Build system utility required for packaging and environment setup.  
- `urllib3` → Low-level HTTP library that powers `requests`, handling connections and retries.  
- `zope.interface` → Dependency of `DateTime`, provides interface definitions and enforcement.  

## Setup

Before running the project, ensure that both **Python** and the **make utility** are installed on your system. Follow the instructions below according to your operating system.

### 1. Install Python

The project requires **Python 3.9 or higher**.

#### Linux
On Debian/Ubuntu-based distributions:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip -y
```

On Fedora/RHEL-based distributions:

```bash
sudo dnf install python3 python3-venv python3-pip -y
```

Verify installation:

```bash
python3 --version
```

#### macOS
1. Install via Homebrew (recommended):

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" # if Homebrew not installed
brew install python
```

2. Verify installation:

```bash
python3 --version
```

#### Windows
1. Download Python from the official website: [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)
2. Run the installer and check **“Add Python to PATH”**.
3. Verify installation:

```powershell
python --version
```

---

### 2. Install `make` utility

The `make` utility is used to automate tasks such as setting up the virtual environment and installing dependencies.

#### Linux
`make` is usually pre-installed. If not:

```bash
sudo apt install build-essential -y  # Debian/Ubuntu
sudo dnf install make -y            # Fedora/RHEL
make --version
```

#### macOS
`make` comes pre-installed with Xcode Command Line Tools:

```bash
xcode-select --install
make --version
```

#### Windows
1. Install via [Chocolatey](https://chocolatey.org/):

```powershell
choco install make
```

Or, install [GnuWin32 Make](http://gnuwin32.sourceforge.net/packages/make.htm).

2. Verify installation:

```powershell
make --version
```

---

### 3. Clone the repository

```bash
git clone https://github.com/BrenoFariasDaSilva/GitHub-Activity-Reports-Generator.git
cd GitHub-Activity-Reports-Generator
```

### 4. Virtual environment (strongly recommended)

With `make`:

```bash
make venv
source venv/bin/activate # Linux/macOS
venv\Scripts\activate # Windows
```

Or manually:

```bash
python -m venv venv
source venv/bin/activate # Linux/macOS
venv\Scripts\activate # Windows
```

### 5. Install dependencies

1. Install **Quarto CLI** (required for report rendering): [Quarto Installation Guide](https://quarto.org/docs/get-started/)  

```bash
quarto --version  # verify installation
```

2. Install **TinyTeX** for PDF output:

```bash
quarto install tinytex
```

3. Install Python packages:

With `make`:

```bash
make dependencies
```

Or manually:

```bash
pip install -r requirements.txt
```

---

### 6. Environment Variables Configuration

Copy the `.env-example` file and rename it `.env`. Edit it with your GitHub credentials and repositories. For full details, see the [Environment Variables Configuration](#environment-variables-configuration) section above.

#### Full list of environment variables

The `.env` file supports the following variables:

```env
# GitHub authentication token (classic, required)
GITHUB_CLASSIC_TOKEN=your_classic_github_token_here
```

Only **classic tokens** are supported (with `repo` and `read:org` scopes). You can generate a new classic token in your GitHub account settings under Developer Settings > Personal Access Tokens > Tokens (classic), or by the following link: [Generate new token (classic)](https://github.com/settings/tokens)

Also, you need to configure the owner and repositories to fetch the data from:

```env
# Owner of the repositories (GitHub organization or username, required)
GitHub URL Template to fill the variables: https://github.com/{owner}/{repo}
OWNER=OWNER_NAME_HERE

# Dictionary with project names and their repositories (JSON string, required)
# Example: {"ProjectA": ["repo1", "repo2"], "ProjectB": ["repo3"]}
REPOS='{"ANY_NAME_FOR_REPOS_LIST": ["REPO_NAME_1", "REPO_NAME_2"]}'
```

Lastly, there is the user mapping configuration, to map GitHub usernames to real names:

```env
# If true, only generate reports for users listed in USER_MAP
# If false, generate reports for all contributors
USER_MAP_ONLY=true

# Dictionary with canonical names and their possible variations (JSON string, optional but recommended)
# Example: {"John Doe": ["jdoe", "john_d", "John_Doe"]}
USER_MAP='{
  "YOUR NAME": ["Your_GitHub_Username", "Your full name with underscores"]
}'
```

---

### main.py configuration

Inside the `main.py` file, you can adjust the following constants if needed:

```python
SAVE_JSONS = False # Set to True to save raw JSON responses in ./responses/
VERBOSE = False # Set to True to print detailed messages during execution
```

## Usage

Run the `main.py` file with `make`:

```bash
make run SINCE=2024-01-01 UNTIL=2024-12-31
```

If no dates are provided (by simply running `make`), it defaults to fetching all data from `2000-01-01` to the current date. This is adjustable in the `Makefile`, at the `SINCE` and `UNTIL` variables.

Or manually:

```bash
source venv/bin/activate # On Linux/macOS
venv\Scripts\activate # On Windows
python3 main.py --since 2024-01-01 --until 2024-12-31
```

## Results

After running the project, you will obtain:  

- **Raw data** → JSON files with issues, PRs, and commits from the configured repositories, stored in the `responses/` folder.  
- **Per-author reports** → Contributions grouped by author (based on `USER_MAP`) within the selected date range. Reports are generated as Quarto `.qmd` files and automatically rendered into **PDF** and **DOCX** formats inside the `reports/` directory.  
- **Traceability** → Clear tracking of how many issues, PRs, and commits were authored by each contributor.  
- **Navigation** → Hyperlinked references to GitHub issues, PRs, and commits for quick access back to the platform.  

### Example structure

```
responses/
├── issue_123.json
├── pr_456_commits.json
└── repo_commits_page_1.json

reports/YYYY-MM-DD_YYYY-MM-DD/Author_Name/
├── Author_Name_YYYY-MM-DD_YYYY-MM-DD.qmd
├── Author_Name_YYYY-MM-DD_YYYY-MM-DD.pdf
└── Author_Name_YYYY-MM-DD_YYYY-MM-DD.docx
```

### Convert QMD to other formats

If you need to modify the `.qmd` report file, then you need to manually convert it to other formats, so the changes are reflected.

To convert to PDF:

```bash
quarto render reports/YYYY-MM-DD_YYYY-MM-DD/Author_Name/activity_Author_Name.qmd --to pdf
```

To convert to DOCX:

```bash
quarto render reports/YYYY-MM-DD_YYYY-MM-DD/Author_Name/activity_Author_Name.qmd --to docx
```

This will create `reports/YYYY-MM-DD_YYYY-MM-DD/activity_Author_Name.pdf` and `reports/YYYY-MM-DD_YYYY-MM-DD/activity_Author_Name.docx` in the same directory. The other available formats include `html` and `latex`.

Read the guide on the official Quarto website for more details: [Quarto Output Formats](https://quarto.org/docs/output-formats/all-formats.html).

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**. If you have suggestions for improving the code, your insights will be highly welcome.
In order to contribute to this project, please follow the guidelines below or read the [CONTRIBUTING.md](CONTRIBUTING.md) file for more details on how to contribute to this project, as it contains information about the commit standards and the entire pull request process.
Please follow these guidelines to make your contributions smooth and effective:

1. **Set Up Your Environment**: Ensure you've followed the setup instructions in the [Setup](#setup) section to prepare your development environment.

2. **Make Your Changes**:
   - **Create a Branch**: `git checkout -b feature/YourFeatureName`
   - **Implement Your Changes**: Make sure to test your changes thoroughly.
   - **Commit Your Changes**: Use clear commit messages, for example:
     - For new features: `git commit -m "FEAT: Add some AmazingFeature"`
     - For bug fixes: `git commit -m "FIX: Resolve Issue #123"`
     - For documentation: `git commit -m "DOCS: Update README with new instructions"`
     - For refactorings: `git commit -m "REFACTOR: Enhance component for better aspect"`
     - For snapshots: `git commit -m "SNAPSHOT: Temporary commit to save the current state for later reference"`
   - See more about crafting commit messages in the [CONTRIBUTING.md](CONTRIBUTING.md) file.

3. **Submit Your Contribution**:
   - **Push Your Changes**: `git push origin feature/YourFeatureName`
   - **Open a Pull Request (PR)**: Navigate to the repository on GitHub and open a PR with a detailed description of your changes.

4. **Stay Engaged**: Respond to any feedback from the project maintainers and make necessary adjustments to your PR.

5. **Celebrate**: Once your PR is merged, celebrate your contribution to the project!

## Collaborators

We thank the following people who contributed to this project:

<table>
  <tr>
    <td align="center">
      <a href="#" title="defina o titulo do link">
        <img src="https://github.com/BrenoFariasdaSilva.png" width="100px;" alt="My Profile Picture"/><br>
        <sub>
          <b>Breno Farias da Silva</b>
        </sub>
      </a>
    </td>
  </tr>
</table>

## License

### Apache License 2.0

This project is licensed under the [Apache License 2.0](LICENSE). This license permits use, modification, distribution, and sublicense of the code for both private and commercial purposes, provided that the original copyright notice and a disclaimer of warranty are included in all copies or substantial portions of the software. It also requires a clear attribution back to the original author(s) of the repository. For more details, see the [LICENSE](LICENSE) file in this repository.
