import os
import re
import secrets
import string
import time
from threading import Lock

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

OTP_LENGTH = 6
OTP_TTL_SECONDS = 120
RESEND_COOLDOWN_SECONDS = 60
MAX_ATTEMPTS = 3

# Demo-only in-memory storage. Records are lost when the server restarts.
_otp_store = {}
_store_lock = Lock()


def generate_otp(length=OTP_LENGTH):
    if length <= 0:
        raise ValueError("OTP length must be positive")
    return "".join(secrets.choice(string.digits) for _ in range(length))


def normalize_phone(phone):
    phone = re.sub(r"[\s()-]", "", phone or "")
    # Demo validation: allow an optional + and 8–15 digits.
    if not re.fullmatch(r"\+?[0-9]{8,15}", phone):
        return None
    return phone


def send_sms_otp(phone_number, otp):
    """
    Demo only: OTP is printed to the backend terminal.
    Replace this function with a real SMS provider integration before production.
    Never log OTP values in a real deployment.
    """
    print(f"[DEMO OTP] To {phone_number}: {otp} (expires in {OTP_TTL_SECONDS}s)")


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/api/request-otp")
def api_request_otp():
    data = request.get_json(silent=True) or {}
    phone = normalize_phone(data.get("phone", ""))

    if not phone:
        return jsonify(success=False, message="Enter a valid phone number (8–15 digits)."), 400

    now = time.time()
    with _store_lock:
        record = _otp_store.get(phone)
        if record:
            elapsed = now - record["created_at"]
            if elapsed < RESEND_COOLDOWN_SECONDS:
                wait = max(1, int(RESEND_COOLDOWN_SECONDS - elapsed))
                return jsonify(
                    success=False,
                    message=f"Please wait {wait} second(s) before requesting another OTP.",
                    wait_seconds=wait,
                ), 429

        otp = generate_otp()
        _otp_store[phone] = {
            "otp": otp,
            "created_at": now,
            "attempts": 0,
        }

    send_sms_otp(phone, otp)
    return jsonify(
        success=True,
        message="Demo OTP generated. Check the VS Code terminal. It expires in 2 minutes.",
        expires_in=OTP_TTL_SECONDS,
        resend_after=RESEND_COOLDOWN_SECONDS,
    )


@app.post("/api/verify-otp")
def api_verify_otp():
    data = request.get_json(silent=True) or {}
    phone = normalize_phone(data.get("phone", ""))
    user_input = str(data.get("otp", "")).strip()

    if not phone:
        return jsonify(success=False, message="Enter the same valid phone number."), 400
    if not re.fullmatch(r"[0-9]{6}", user_input):
        return jsonify(success=False, message="Enter the 6-digit OTP."), 400

    with _store_lock:
        record = _otp_store.get(phone)

        if not record:
            return jsonify(success=False, message="No active OTP found. Request a new OTP."), 400

        if time.time() - record["created_at"] > OTP_TTL_SECONDS:
            _otp_store.pop(phone, None)
            return jsonify(success=False, message="OTP expired. Request a new one."), 400

        if record["attempts"] >= MAX_ATTEMPTS:
            _otp_store.pop(phone, None)
            return jsonify(success=False, message="Maximum attempts exceeded. Request a new OTP."), 429

        record["attempts"] += 1
        if secrets.compare_digest(user_input, record["otp"]):
            _otp_store.pop(phone, None)  # Single-use OTP
            return jsonify(success=True, message="Verification successful! Access granted.")

        remaining = MAX_ATTEMPTS - record["attempts"]
        if remaining <= 0:
            _otp_store.pop(phone, None)
            return jsonify(success=False, message="Invalid OTP. Maximum attempts exceeded; request a new OTP."), 429

        return jsonify(
            success=False,
            message=f"Invalid OTP. {remaining} attempt(s) remaining.",
            attempts_remaining=remaining,
        ), 400


if __name__ == "__main__":
    # Debug mode is for local development only.
    app.run(host="127.0.0.1", port=5000, debug=True)
