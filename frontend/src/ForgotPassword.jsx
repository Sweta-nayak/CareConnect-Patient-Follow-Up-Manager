
import { useState } from "react";
import api from "./api/axios";

function ForgotPassword({ onBack }) {
  const [step, setStep] = useState(1);

  const [organizationCode, setOrganizationCode] = useState("");
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [newPassword, setNewPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleForgotPassword = async (e) => {
    e.preventDefault();

    setLoading(true);
    setError("");
    setMessage("");

    try {
      const response = await api.post("/api/auth/forgot-password", {
        organization_code: organizationCode,
        email: email
      });

      setMessage(response.data.message);
      setStep(2);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Unable to process your request. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();

    setLoading(true);
    setError("");
    setMessage("");

    try {
      const response = await api.post("/api/auth/reset-password", {
        organization_code: organizationCode,
        email: email,
        otp: otp,
        new_password: newPassword
      });

      setMessage(response.data.message);
      setStep(3);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Password reset failed. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">

        <h2>
          {step === 1 && "Forgot Password?"}
          {step === 2 && "Verify OTP"}
          {step === 3 && "Password Reset Successful"}
        </h2>

        {step === 1 && (
          <>
            <p>Enter your organization code and registered email.</p>

            <form onSubmit={handleForgotPassword}>
              <input
                type="text"
                placeholder="Organization Code"
                value={organizationCode}
                onChange={(e) =>
                  setOrganizationCode(e.target.value)
                }
                required
              />

              <input
                type="email"
                placeholder="Registered Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />

              <button
                type="submit"
                className="login-button"
                disabled={loading}
              >
                {loading ? "Sending OTP..." : "Send OTP"}
              </button>
            </form>
          </>
        )}

        {step === 2 && (
          <>
            <p>Enter the six-digit OTP sent to your email and choose a new password.</p>

            <form onSubmit={handleResetPassword}>
              <input
                type="text"
                placeholder="Enter 6-digit OTP"
                value={otp}
                onChange={(e) =>
                  setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))
                }
                maxLength={6}
                inputMode="numeric"
                required
              />

              <input
                type="password"
                placeholder="New Password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                minLength={8}
                maxLength={128}
                required
              />

              <button
                type="submit"
                className="login-button"
                disabled={loading || otp.length !== 6}
              >
                {loading ? "Resetting..." : "Reset Password"}
              </button>
            </form>
          </>
        )}

        {step === 3 && (
          <>
            <p>Your password has been changed successfully.</p>

            <button
              className="login-button"
              onClick={onBack}
            >
              Back to Login
            </button>
          </>
        )}

        {message && (
          <p style={{ color: "green" }}>{message}</p>
        )}

        {error && (
          <p style={{ color: "red" }}>{error}</p>
        )}

        {step !== 3 && (
          <button
            type="button"
            onClick={onBack}
            style={{
              marginTop: "15px",
              background: "transparent",
              border: "none",
              cursor: "pointer"
            }}
          >
            Back to Login
          </button>
        )}

      </div>
    </div>
  );
}

export default ForgotPassword;
