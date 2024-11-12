# Bjorn Detector & SSH Launcher
![ezgif-1-a310f5fe8f](https://github.com/user-attachments/assets/182f82f0-5c3a-48a9-a75e-37b9cfa2263a)

I have created an application that detects **Bjorn** on the local network, displays its IP address, and allows you to initiate an SSH session with a single click on Bjorn Icon.
The red dot is moving around the radar when he looks for Bjorn.

## Features

- **Automatic Network Detection**: Continuously checks for the device `bjorn.home` on the local network.
- **Interactive SSH Launcher**: When `bjorn.home` is detected, click the Bjorn icon to automatically launch an SSH terminal connected to Bjorn’s IP address.
- **IP Display**: Shows the IP address of `bjorn.home` upon detection.
- **Seamless Bjorn Installation**: Facilitates  installation of [Bjorn](https://github.com/infinition/Bjorn/) by connecting to the device via SSH.

## Requirements

- **Python 3**
- **PyQt6**

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/infinition/Bjorn_Detector.git
   cd Bjorn_Detector
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Launch

Run the application with:
```bash
python main.py
```


