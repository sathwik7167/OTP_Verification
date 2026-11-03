const phoneInput = document.getElementById("phone");
const otpInput = document.getElementById("otp");
const requestBtn = document.getElementById("request-btn");
const verifyBtn = document.getElementById("verify-btn");
const form = document.getElementById("otp-form");
const statusEl = document.getElementById("status");
const timerEl = document.getElementById("timer");

let resendTimer = null;
let expiryTimer = null;

function showStatus(message, type = "info") {
  statusEl.textContent = message;
  statusEl.className = `status ${type}`;
}
function setBusy(button, busy, text) {
  button.disabled = busy;
  if (busy) {
    button.dataset.originalText = button.textContent;
    button.textContent = text;
  } else {
    button.textContent = button.dataset.originalText || text;
  }
}
async function postJSON(url, body) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.message || "Request failed.");
  return data;
}
function startCountdown(seconds, label, callback) {
  let remaining = seconds;
  callback(remaining);
  const id = setInterval(() => {
    remaining -= 1;
    callback(Math.max(remaining, 0));
    if (remaining <= 0) clearInterval(id);
  }, 1000);
  return id;
}

requestBtn.addEventListener("click", async () => {
  setBusy(requestBtn, true, "Sending...");
  try {
    const data = await postJSON("/api/request-otp", { phone: phoneInput.value });
    showStatus(data.message, "success");
    otpInput.focus();

    clearInterval(resendTimer);
    requestBtn.disabled = true;
    resendTimer = startCountdown(data.resend_after, "resend", seconds => {
      requestBtn.textContent = seconds > 0 ? `Resend OTP in ${seconds}s` : "Send OTP";
      if (seconds <= 0) requestBtn.disabled = false;
    });

    clearInterval(expiryTimer);
    expiryTimer = startCountdown(data.expires_in, "expiry", seconds => {
      timerEl.textContent = seconds > 0
        ? `OTP expires in ${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`
        : "OTP expired. Request a new one.";
    });
  } catch (error) {
    showStatus(error.message, "error");
    setBusy(requestBtn, false, "Send OTP");
  }
});

form.addEventListener("submit", async event => {
  event.preventDefault();
  setBusy(verifyBtn, true, "Verifying...");
  try {
    const data = await postJSON("/api/verify-otp", {
      phone: phoneInput.value,
      otp: otpInput.value
    });
    showStatus(data.message, "success");
    clearInterval(expiryTimer);
    timerEl.textContent = "This OTP has been used and cannot be reused.";
    otpInput.value = "";
  } catch (error) {
    showStatus(error.message, "error");
  } finally {
    setBusy(verifyBtn, false, "Verify OTP");
  }
});
