# upboard

upboard (Update-Board) is a lightweight CLI tool used to manage and deliver updated versions of applications during development.

**upboard** helps you distribute software updates to clients by providing a simple HTTP server (`upboard-server`) and a   file publisher (`upboard-publish`). Applications can check for and download updates dynamically at runtime using standard HTTP requests.

## 📦 Installation

```bash
pip install upboard
```

## 🚀 Usage

### Start the update server

```bash
upboard-server --dir ./release-dir --port 5001 --password mysecret
```

- Releases file hosted by the service from `./release-dir`
- Accepts authenticated `PUT` uploads at `/api/v1/releases/...`

### Run As Server

#### Linux

You can run upboard as a systemd service on Linux systems:

```bash
# 1. Copy and modify the service file to systemd directory:
sudo cp src/etc/systemd/upboard.service /etc/systemd/system/

# 2. Reload systemd daemon:
sudo systemctl daemon-reload

# 3. Start the service:
sudo systemctl start upboard

# 4. Enable auto-start on boot:
sudo systemctl enable upboard

# 5. To check service status:
systemctl status upboard
```

#### Windows

To run upboard as a Windows service, you can use NSSM (Non-Sucking Service Manager):

1. Download and install NSSM from: <https://nssm.cc/>

2. Open Command Prompt as Administrator and run:

    ```cmd
    nssm install upboard
    ```

3. In the NSSM service installer:
   - Application Path: Path to your Python executable
   - Arguments: -m upboard-server
   - Startup Directory: Your release directory path

4. Start the service:

    ```cmd
    nssm start upboard
    ```

### Upload a file

```bash
upboard-publish --password mysecret http://localhost:5001/api/v1/releases/win32/x64/ your-release-file
```

### Check for updates (client-side, GET request)

```http
GET /api/v1/updates/your-project/win32/x64/your-release-file
```

## 📁 API Overview

| Description                     | Method | Endpoint Example                                                      |
|---------------------------------|--------|-----------------------------------------------------------------------|
| Upload a new version            | PUT    | `/api/v1/releases/<product>/<platform>/<arch>[/<version>]/<filename>` |
| Check if a newer version exists | GET    | `/api/v1/updates/<product>/<platform>/<arch>[/<version>]/<filename>`  |

## 📄 License

MIT License
