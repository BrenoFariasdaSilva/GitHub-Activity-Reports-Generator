<div align="center">
  
# [GitHub-Activity-Reports-Generator.](https://github.com/BrenoFariasdaSilva/GitHub-Activity-Reports-Generator) <img src="https://github.com/BrenoFariasdaSilva/GitHub-Activity-Reports-Generator/blob/main/.assets/Images/Github.svg"  width="3%" height="3%">

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
  - [Requirements](#requirements)
  - [Setup](#setup)
    - [Clone the repository](#clone-the-repository)
    - [Virtual environment (strongly recommended)](#virtual-environment-strongly-recommended)
    - [Install dependencies](#install-dependencies)
    - [Environment Variables configuration](#environment-variables-configuration)
    - [Dataset - Optional](#dataset---optional)
  - [Usage](#usage)
  - [Results - Optional](#results---optional)
  - [Contributing](#contributing)
  - [Collaborators](#collaborators)
  - [License](#license)
    - [Apache License 2.0](#apache-license-20)

## Introduction

Detailed project description.

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

---

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

### Clone the repository

1. Clone the repository with the following command:

```bash
git clone https://github.com/BrenoFariasDaSilva/GitHub-Activity-Reports-Generator.git
cd GitHub-Activity-Reports-Generator
```

### Virtual environment (strongly recommended)

With `make`:

```bash
make venv
source venv/bin/activate # On Linux/macOS
venv\Scripts\activate # On Windows
```

Or manually:

```bash
python -m venv venv
source venv/bin/activate # On Linux/macOS
venv\Scripts\activate # On Windows
```

### Install dependencies

To generate reports, you’ll need to install **Quarto CLI** and **TinyTeX** (required for PDF output).

1. Install Quarto by following the official instructions: [Quarto Installation Guide](https://quarto.org/docs/get-started/).

Verify that is was installed correctly:

```bash
quarto --version
```

2. Install TinyTeX (a lightweight LaTeX distribution) with Quarto:

```bash
quarto install tinytex
```

Now you need to install the required Python packages.

With `make`:

```bash
make dependencies
```

Or manually:

```bash
source venv/bin/activate # On Linux/macOS
venv\Scripts\activate # On Windows
pip install -r requirements.txt
```

### Environment Variables configuration

Copy the `.env-example` file in the project root, naming it `.env`, and add your GitHub Personal Access Token (Classic):

```env
GITHUB_CLASSIC_TOKEN=your_personal_access_token
```

Only **classic tokens** are supported (with `repo` and `read:org` scopes). You can generate a new classic token in your GitHub account settings under Developer Settings > Personal Access Tokens > Tokens (classic), or by the following link: [Generate new token (classic)](https://github.com/settings/tokens)

### Dataset - Optional

1. Download the dataset from [WEBSITE-HERE]() and place it in this project directory `(/GitHub-Activity-Reports-Generator)` and run the following command:

```bash
make dataset
```

## Usage

In order to run the project, run the following command:

```bash
make run
```

## Results - Optional

Discuss the results obtained in the project.

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
        <img src="https://github.com/BrenoFariasdaSilva/GitHub-Activity-Reports-Generator/blob/main/.assets/Images/Github.svg" width="100px;" alt="My Profile Picture"/><br>
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
