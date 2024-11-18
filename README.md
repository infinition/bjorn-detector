# 🧭 Bjorn Detector

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![Status](https://img.shields.io/badge/Status-Development-blue.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![Reddit](https://img.shields.io/badge/Reddit-Bjorn__CyberViking-orange?style=for-the-badge&logo=reddit)](https://www.reddit.com/r/Bjorn_CyberViking)
[![Discord](https://img.shields.io/badge/Discord-Join%20Us-7289DA?style=for-the-badge&logo=discord)](https://discord.com/invite/B3ZH9taVfT)

**Bjorn Detector** detects [Bjorn](https://github.com/infinition/bjorn) device on the local network, displays its IP address, and allows you to initiate an SSH session with a single click on Bjorn Icon.
The red dot is moving around the radar while he looks for Bjorn.

## 📚 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Usage](#-usage)
- [Logging](#-logging)
- [License](#-license)
- [Contact](#-contact)

## ✨ Features

- **Automatic Network Detection**: Continuously checks for the device `bjorn.home` on the local network.
- **Interactive SSH Launcher**: When `bjorn.home` is detected, click the Bjorn icon to automatically launch an SSH terminal connected to Bjorn’s IP address.
- **IP Display**: Shows the IP address of `bjorn.home` upon detection.
- **Seamless Bjorn Installation**: Facilitates  installation of [Bjorn](https://github.com/infinition/Bjorn/) by connecting to the device via SSH.

## 📌 Prerequisites

- **Python**: 3.9+
- **PyQt6**: 6.7.0+

## 🛠️ Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/infinition/bjorn-detector.git
   cd bjorn-detector
   ```

2. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**

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

4. **Upgrade pip**

   ```bash
   python -m ensurepip
   pip install --upgrade pip
   ```

5. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   - Deactivate the Virtual Environment

   When you're done, deactivate the environment:

   ```bash
    deactivate
   ```
   
## 🚀 Usage

### 🕵️ Scan for Bjorn Device

Run the main script:

```bash
python bjorn-detector.py
```

This will scan your network and find **Bjorn** device, One-Click **Bjorn** to start SSH session.

### 📟 Command-Line Arguments

You can customize the behavior using the following arguments:

- `--timeout: timeout in seconds. Must be between 10 to 300.`

   ```bash
   python bjorn-detector.py --timeout 10
   ```

- `--identity-file, --i: Identity file used to connect device if set on install. Defaults to None..`

   ```bash
   python bjorn-detector.py --identity-file identity-file.[ppk]
   ```

- `--log-level: Set the logging level (INFO or DEBUG).`

   ```bash
   python bjorn-detector.py --log-level DEBUG
   ```

### 📝 Example Usage

```bash
python bjorn-detector.py
```

## 📊 Logging

Logs are maintained in logs/bjorn-detector.log with rotating file handlers to prevent excessive file sizes.

    Log Levels:
        INFO: General operational messages.
        DEBUG: Detailed diagnostic information.

## 📫 Contact

- **Report Issues**: Via GitHub.
- **Guidelines**:
  - Follow ethical guidelines.
  - Document reproduction steps.
  - Provide logs and context.

- **Author**: __infinition__
- **GitHub**: [infinition/bjorn-detector](https://github.com/infinition/bjorn-detector)

---

## 📜 License

2024 - Bjorn is distributed under the MIT License. For more details, please refer to the [LICENSE](LICENSE) file included in this repository.
