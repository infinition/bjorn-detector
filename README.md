# 🧭 Bjorn Detector

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)
![Python3](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![Status](https://img.shields.io/badge/Status-Stable-green.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![Reddit](https://img.shields.io/badge/Reddit-Bjorn__CyberViking-orange?style=for-the-badge&logo=reddit)](https://www.reddit.com/r/Bjorn_CyberViking)
[![Discord](https://img.shields.io/badge/Discord-Join%20Us-7289DA?style=for-the-badge&logo=discord)](https://discord.com/invite/B3ZH9taVfT)

<p align="center">
  <img src="https://github.com/user-attachments/assets/182f82f0-5c3a-48a9-a75e-37b9cfa2263a" alt="ezgif-1-a310f5fe8f" width="160">
</p>

**Bjorn Detector** detects [Bjorn](https://github.com/infinition/bjorn) device on the local network, displays its IP address, and allows you to initiate an SSH session with a single click on Bjorn Icon.
The red dot is moving around the radar while he looks for Bjorn.

## 📚 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Logging](#-logging)
- [License](#-license)
- [Contact](#-contact)

## ✨ Features

- **Automatic Network Detection**: Continuously checks for the device `bjorn.home` on the local network.
- **Interactive SSH Launcher**: When `bjorn.home` is detected, click the Bjorn icon to automatically launch an SSH terminal connected to Bjorn’s IP address.
- **IP Display**: Shows the IP address of `bjorn.home` upon detection.
- **Seamless Bjorn Installation**: Facilitates installation of [Bjorn](https://github.com/infinition/Bjorn/) by connecting to the device via SSH.

## 📌 Prerequisites

- **Python**: 3.9+
- **PyQt6**: 6.7.0+

  - **Linux**:

    ```bash
    sudo apt-get install -y libegl1 libpulse0
    ```

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

   - or if u prefer use poetry:

     ```bash
     pip install poetry
     poetry lock
     poetry install
     ```

     - When you're done, deactivate the environment:

       ```bash
       deactivate
       ```

## ⚙️ Configuration

**Environment Variables**:

Create a `.env` file from `.env.example` file in the project root directory and populate it with the following variables:

```bash
cp .env.example .env
```

...

```bash
# Global Config
TIMEOUT=50

# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# Discord
DISCORD_WEBHOOK_URL=your_discord_webhook_url

# SMTP
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password
SMTP_FROM_EMAIL=from@example.com
SMTP_TO_EMAIL=to@example.com
```

- Descriptions:
  - TIMEOUT: The duration in seconds the application waits before determining that the bjorn device is unreachable.
  - TELEGRAM_BOT_TOKEN: The token for your Telegram bot, which allows the application to send messages via Telegram.
  - TELEGRAM_CHAT_ID: The unique identifier for the Telegram chat where notifications will be sent.
  - DISCORD_WEBHOOK_URL: The webhook URL for your Discord channel, enabling the application to post messages to Discord.
  - SMTP_SERVER: The address of your SMTP server used for sending emails.
  - SMTP_PORT: The port number of your SMTP server (commonly 587 for TLS or 465 for SSL).
  - SMTP_USERNAME: The username for authenticating with your SMTP server.
  - SMTP_PASSWORD: The password for authenticating with your SMTP server.
  - SMTP_FROM_EMAIL: The email address that will appear as the sender of the emails.
  - SMTP_TO_EMAIL: The email address that will receive the notifications.

Note: All env vars are _optionals_ but inclusive between prefixes [TELEGRAM_, DISCORD_, SMTP_].

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

- `--identity-file, --i: Identity file used to connect device if set on install. Defaults to None.`

  ```bash
  python bjorn-detector.py --identity-file identity-file.pem
  ```

  - **Must be a Valid OpenSSH Key File**

- `--log-level: Set the logging level (INFO or DEBUG).`

  ```bash
  python bjorn-detector.py --log-level DEBUG
  ```

#### Headless Mode

- `--no-gui: launch detector using non-gui, non-ssh.`

  ```bash
  python bjorn-detector.py --no-gui
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

- **Author**: **infinition**
- **GitHub**: [infinition/bjorn-detector](https://github.com/infinition/bjorn-detector)

## 🌠 Stargazers

[![Star History Chart](https://api.star-history.com/svg?repos=infinition/bjorn-detector&type=Date)](https://star-history.com/#infinition/bjorn-detector&Date)

---

## 📜 License

2024 - Bjorn is distributed under the MIT License. For more details, please refer to the [LICENSE](LICENSE) file included in this repository.
