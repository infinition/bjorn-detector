# 🖲️ Bjorn Development

<p align="center">
  <img src="https://github.com/user-attachments/assets/c5eb4cc1-0c3d-497d-9422-1614651a84ab" alt="thumbnail_IMG_0546" width="98">
</p>

## 📚 Table of Contents

- [Educational Aspects](#-educational-aspects)
- [Disclaimer](#-disclaimer)
- [Extensibility](#-extensibility)
- [Development Status](#-development-status)
  - [Project Structure](#-project-structure)
  - [Core Files](#-core-files)
- [Getting Started](#-getting-started)
  - [Prerequisites](#-prerequisites)
  - [Installation](#-installation)
  - [Environment Setup](#-environment-setup)
  - [Pre-Commit Hooks](#-pre-commit-hooks)
- [License](#-license)

## 📔 Educational Aspects

- **Learning Tool**: Designed as an educational tool to understand cybersecurity concepts and penetration testing techniques.
- **Practical Experience**: Provides a practical means for students and professionals to familiarize themselves with network security practices and vulnerability assessment tools.

## ✒️ Disclaimer

- **Ethical Use**: This project is strictly for educational purposes.
- **Responsibility**: The author and contributors disclaim any responsibility for misuse of Bjorn.
- **Legal Compliance**: Unauthorized use of this tool for malicious activities is prohibited and may be prosecuted by law.

## 🧩 Extensibility

- **Evolution**: The main purpose of Bjorn is to gain new actions and extend his arsenal over time.
- **Contribution**: It's up to the user to develop new actions and add them to the project.

## 🔦 Development Status

- **Project Status**: Stable.

### 🗂️ Project Structure

```
bjorn-detector/
├───.github
│   ├───ISSUE_TEMPLATE
│   └───workflows
├───scripts
│   ├───bump_year
│   ├───commit_msg_version_bump
│   ├───control_commit
│   └───generate_changelog
├───src
│   ├───static
│   │   ├───images
│   │   └───sounds
│   └───utils
│       ├───discord
│       ├───smtp
│       └───telegram
└───tests
```

### ⚓ Core Files

#### bjorn-detector.py

The main entry point for the application. It initializes and runs the main components.

#### logger.py

Defines a custom logger with specific formatting and handlers for console and file logging. It also includes a custom log level for success messages.

#### config.py

Defines the `Config` class that holds configuration settings.

#### main.py

Load components, interface and get config.

## 🚀 Getting Started

### 📋 Prerequisites

**Before you begin development, ensure you have met the following requirements**:

- **GitHub Account:** You need a GitHub account to use GitHub Actions.
- **Python 3.10+:** Ensure Python is installed on your local machine.
- **Git:** Install [Git](https://git-scm.com/) to clone the repository.
- **NVM:** (Optional) Node.js installation environment versions control
- **Node.js 20.x+**: (Optional) (Required to Push) Used as lint orchestration manager in pre-commit and pre-push

### 🔨 Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/infinition/bjorn-detector.git
   ```

2. Navigate to the Project Directory
   ```bash
    cd bjorn-detector
   ```

### 🔧 Environment Setup

**Mandatory: Setting Up a Python Virtual Environment**

Setting up a Python virtual environment ensures that dependencies are managed effectively and do not interfere with other projects.

1. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   ```

2. **Activate the Virtual Environment**

   On Unix or MacOS:

   ```bash
   source venv/bin/activate
   ```

   On Windows:

   ```bash
    .\venv\Scripts\activate
   ```

   - or

   ```bash
    powershell.exe -ExecutionPolicy Bypass -File .\venv\Scripts\Activate.ps1
   ```

3. **Upgrade pip**

   ```bash
   pip install --upgrade pip
   ```

4. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   pip install poetry
   poetry lock
   poetry install
   ```

   - Deactivate the Virtual Environment

   When you're done, deactivate the environment:

   ```bash
    deactivate
   ```

5. **Docker Extra Steps**: Install Scoop and then install hadolint using scoop, refer to [Extra Steps](#-extra-steps)

### 🛸 Pre-Commit Hooks

**Install and check pre-commit hooks**: MD files changes countermeasures, python format, python lint, yaml format, yaml lint, version control hook, changelog auto-generation

```bash
pre-commit install
pre-commit install -t pre-commit
pre-commit install -t pre-push
pre-commit autoupdate
pre-commit run --all-files
```

### 📌 Extra Steps

1. **Docker**:

   - Using MacOs or Linux:
     ```bash
     brew install hadolint
     ```
   - On Windows **as non-admin user**:
     ```bash
     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
     Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
     scoop install hadolint
     ```

---

## 📜 License

2024 - Bjorn is distributed under the MIT License. For more details, please refer to the [LICENSE](LICENSE) file included in this repository.
