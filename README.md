# Secure OTP Verification Website

A beginner-friendly frontend/backend demo based on the supplied Python OTP code.

## Features
- Six-digit cryptographically secure OTP
- Two-minute OTP expiry
- 60-second resend cooldown
- Maximum three verification attempts
- Constant-time OTP comparison
- OTP is single-use
- Responsive HTML/CSS/JavaScript frontend
- Python Flask JSON API backend

## Requirements
- Python 3.10 or newer
- VS Code (recommended)

## Run in VS Code

1. Extract the ZIP and open the `otp_verification_website` folder in VS Code.
2. Open the VS Code terminal in this folder.
3. Create a virtual environment:

   Windows:
   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt:
   ```bat
   .venv\Scripts\activate.bat
   ```

4. Install Flask:
   ```bash
   python -m pip install -r requirements.txt
   ```

5. Start the backend:
   ```bash
   python app.py
   ```

6. Open `http://127.0.0.1:5000` in your browser.
7. Enter a phone number and click **Send OTP**. Look at the VS Code terminal for the demo OTP, then enter it on the page.

## API endpoints
- `POST /api/request-otp` JSON: `{"phone":"+919876543210"}`
- `POST /api/verify-otp` JSON: `{"phone":"+919876543210","otp":"123456"}`

## Important security limitations
This is a local learning demo, not production authentication:
- OTPs are printed in the terminal; no real SMS is sent.
- OTP records are stored in process memory and disappear when the server restarts. Multiple server workers would not share state.
- For production, use an SMS provider, HTTPS, persistent shared storage such as Redis, per-IP and per-phone rate limits, abuse monitoring, secure session handling, and generic responses that reduce phone-number enumeration.
- Flask debug mode is for local development only. Disable it in production.
