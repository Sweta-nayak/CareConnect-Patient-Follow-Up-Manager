
import { useState, useEffect } from "react";
import "./App.css";

import api from "./api/axios";

import PatientManagement from "./components/PatientManagement";
import AppointmentManagement from "./components/AppointmentManagement.jsx";
import CareInstructionManagement from "./components/CareInstructionManagement.jsx";
import ReminderManagement from "./components/ReminderManagement.jsx";
import ForgotPassword from "./ForgotPassword";


function App() {

  // ---------------------------------------
  // LOGIN AND REGISTRATION STATES
  // ---------------------------------------

  const [organizationCode, setOrganizationCode] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [isRegisterMode, setIsRegisterMode] = useState(false);

  const [organizationName, setOrganizationName] = useState("");
  const [adminFullName, setAdminFullName] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [isForgotPassword, setIsForgotPassword] = useState(false);

  const [isLoggedIn, setIsLoggedIn] = useState(
    Boolean(sessionStorage.getItem("access_token"))
  );

  const [activePage, setActivePage] = useState("Dashboard");
  const [adminName, setAdminName] = useState("Admin");
  const [userRole, setUserRole] = useState("");

  // ---------------------------------------
  // READ ROLE FROM JWT
  // ---------------------------------------

  const getRoleFromToken = () => {
    try {
      const token = sessionStorage.getItem("access_token");

      if (!token) return "";

      const payload = token.split(".")[1];

      const base64 = payload
        .replace(/-/g, "+")
        .replace(/_/g, "/");

      const decodedPayload = JSON.parse(
        atob(base64)
      );

      return decodedPayload.role || "";

    } catch (err) {
      console.error("Unable to read user role:", err);
      return "";
    }
  };

  // ---------------------------------------
  // DASHBOARD STATES
  // ---------------------------------------

  const [dashboardData, setDashboardData] = useState({
    total_patients: 0,
    todays_appointments: 0,
    missed_appointments: 0,
    pending_reminders: 0,
    recent_appointments: []
  });

  const [dashboardLoading, setDashboardLoading] = useState(false);
  const [dashboardError, setDashboardError] = useState("");

  // ---------------------------------------
  // AUDIT LOG STATES
  // ---------------------------------------

  const [auditLogs, setAuditLogs] = useState([]);
  const [auditLoading, setAuditLoading] = useState(false);
  const [auditError, setAuditError] = useState("");

  // ---------------------------------------
  // FETCH DASHBOARD DATA
  // ---------------------------------------

  const loadDashboardData = async () => {
    try {
      setDashboardLoading(true);
      setDashboardError("");

      const response = await api.get("/api/dashboard/summary");

      setDashboardData(response.data);

    } catch (err) {
      console.error("Dashboard loading error:", err);

      setDashboardError(
        err.response?.data?.detail ||
        "Unable to load dashboard information."
      );

    } finally {
      setDashboardLoading(false);
    }
  };

  // ---------------------------------------
  // LOAD DASHBOARD WHEN OPENED
  // ---------------------------------------

  useEffect(() => {
    if (isLoggedIn && activePage === "Dashboard") {
      loadDashboardData();
    }
  }, [isLoggedIn, activePage]);

  // ---------------------------------------
  // FETCH AUDIT LOGS
  // ---------------------------------------

  const loadAuditLogs = async () => {
    try {
      setAuditLoading(true);
      setAuditError("");

      const response = await api.get("/api/audit-logs/", {
        params: {
          limit: 100,
          offset: 0
        }
      });

      setAuditLogs(response.data);

    } catch (err) {
      console.error("Audit log loading error:", err);

      setAuditError(
        err.response?.data?.detail ||
        "Unable to load audit logs."
      );

    } finally {
      setAuditLoading(false);
    }
  };

  // ---------------------------------------
  // LOAD AUDIT LOGS WHEN OPENED
  // ---------------------------------------

  useEffect(() => {
    if (
      isLoggedIn &&
      activePage === "Audit Logs" &&
      userRole === "ADMIN"
    ) {
      loadAuditLogs();
    }
  }, [isLoggedIn, activePage, userRole]);

  // ---------------------------------------
  // LOGIN FUNCTION
  // ---------------------------------------

  const handleLogin = async (e) => {
    e.preventDefault();

    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const response = await api.post("/api/auth/login", {
        organization_code: organizationCode,
        email: email,
        password: password
      });

      const accessToken = response.data.access_token;

      sessionStorage.setItem("access_token", accessToken);

      const name =
        response.data.full_name ||
        response.data.user?.full_name ||
        email;

      setAdminName(name);

      const role = getRoleFromToken();
      setUserRole(role);

      setSuccess("Login successful!");
      setIsLoggedIn(true);

      setActivePage("Dashboard");

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Login failed. Check your details."
      );

      console.error("Login error:", err);

    } finally {
      setLoading(false);
    }
  };

  // ---------------------------------------
  // HOSPITAL REGISTRATION FUNCTION
  // ---------------------------------------

  const handleRegister = async (e) => {
    e.preventDefault();

    setError("");
    setSuccess("");

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      await api.post("/api/auth/register", {
        organization_name: organizationName,
        organization_code: organizationCode,
        full_name: adminFullName,
        email: email,
        password: password
      });

      setSuccess("Registration successful! Please sign in.");

      setIsRegisterMode(false);

      setPassword("");
      setConfirmPassword("");
      setOrganizationName("");
      setAdminFullName("");

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Registration failed. Please check your details."
      );

    } finally {
      setLoading(false);
    }
  };

  // ---------------------------------------
  // LOGOUT FUNCTION
  // ---------------------------------------

  const handleLogout = () => {
    sessionStorage.removeItem("access_token");

    setIsLoggedIn(false);

    setOrganizationCode("");
    setEmail("");
    setPassword("");

    setError("");
    setSuccess("");

    setUserRole("");
    setAdminName("Admin");

    setActivePage("Dashboard");

    setAuditLogs([]);
    setAuditError("");

    setDashboardData({
      total_patients: 0,
      todays_appointments: 0,
      missed_appointments: 0,
      pending_reminders: 0,
      recent_appointments: []
    });
  };

  // ---------------------------------------
  // LOGIN AND REGISTRATION PAGE
  // ---------------------------------------

  if (!isLoggedIn) {

    // FORGOT PASSWORD SCREEN

    if (isForgotPassword) {
      return (
        <ForgotPassword
          onBack={() => {
            setIsForgotPassword(false);
            setError("");
            setSuccess("");
          }}
        />
      );
    }

    return (
      <div className="login-container">

        {/* LEFT SECTION */}

        <div className="login-left">

          <div className="brand">
            <div className="brand-icon">+</div>
            <h2>CareConnect</h2>
          </div>

          <div className="welcome-content">

            <p className="welcome-tag">
              PATIENT FOLLOW-UP MANAGER
            </p>

            <h1>
              Better care.
              <br />
              Better follow-ups.
            </h1>

            <p className="welcome-description">
              Manage patients, appointments and follow-up
              reminders from one simple platform.
            </p>

            <div className="feature-list">
              <p>✓ Patient management</p>
              <p>✓ Appointment tracking</p>
              <p>✓ Care instructions and reminders</p>
            </div>

          </div>

          <p className="left-footer">
            © 2026 CareConnect. All rights reserved.
          </p>

        </div>

        {/* RIGHT SECTION */}

        <div className="login-right">

          <div
            className="login-card"
            style={{
              maxHeight: "85vh",
              overflowY: "auto"
            }}
          >

            {/* BACK TO SIGN IN */}

            {isRegisterMode && (
              <button
                type="button"
                onClick={() => {
                  setIsRegisterMode(false);
                  setError("");
                  setSuccess("");
                }}
                style={{
                  border: "none",
                  background: "transparent",
                  color: "#07838c",
                  fontWeight: 600,
                  cursor: "pointer",
                  padding: "0 0 18px",
                  fontSize: "14px"
                }}
              >
                ← Back to Sign In
              </button>
            )}

            {/* PAGE HEADING */}

            <h1>
              {isRegisterMode
                ? "Register your hospital"
                : "Welcome back!"}
            </h1>

            <p className="login-subtitle">
              {isRegisterMode
                ? "Create your hospital administrator account."
                : "Please enter your details to sign in."}
            </p>

            {/* LOGIN AND REGISTRATION FORM */}

            <form
              onSubmit={
                isRegisterMode
                  ? handleRegister
                  : handleLogin
              }
            >

              {/* REGISTRATION FIELDS */}

              {isRegisterMode && (
                <>
                  <label>Hospital Name</label>

                  <input
                    type="text"
                    placeholder="Enter hospital name"
                    value={organizationName}
                    onChange={(e) =>
                      setOrganizationName(e.target.value)
                    }
                    minLength={2}
                    required
                  />

                  <label>Admin Full Name</label>

                  <input
                    type="text"
                    placeholder="Enter admin full name"
                    value={adminFullName}
                    onChange={(e) =>
                      setAdminFullName(e.target.value)
                    }
                    minLength={2}
                    required
                  />
                </>
              )}

              {/* ORGANIZATION CODE */}

              <label>Organization Code</label>

              <input
                type="text"
                placeholder="Enter organization code"
                value={organizationCode}
                onChange={(e) =>
                  setOrganizationCode(e.target.value)
                }
                required
              />

              {/* EMAIL */}

              <label>Email Address</label>

              <input
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) =>
                  setEmail(e.target.value)
                }
                required
              />

              {/* PASSWORD */}

              <label>Password</label>

              <input
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) =>
                  setPassword(e.target.value)
                }
                minLength={8}
                required
              />

              {/* CONFIRM PASSWORD */}

              {isRegisterMode && (
                <>
                  <label>Confirm Password</label>

                  <input
                    type="password"
                    placeholder="Confirm your password"
                    value={confirmPassword}
                    onChange={(e) =>
                      setConfirmPassword(e.target.value)
                    }
                    minLength={8}
                    required
                  />
                </>
              )}

              {/* ERROR MESSAGE */}

              {error && (
                <p className="error-message">
                  {error}
                </p>
              )}

              {/* SUCCESS MESSAGE */}

              {success && (
                <p className="success-message">
                  {success}
                </p>
              )}

              {/* SUBMIT BUTTON */}

              <button
                type="submit"
                className="login-button"
                disabled={loading}
              >
                {loading
                  ? "Please wait..."
                  : isRegisterMode
                    ? "Create Account"
                    : "Sign In"}
              </button>

              {/* FORGOT PASSWORD LINK */}

              {!isRegisterMode && (
                <div
                  style={{
                    textAlign: "right",
                    marginTop: "12px"
                  }}
                >
                  <button
                    type="button"
                    onClick={() => {
                      setIsForgotPassword(true);
                      setError("");
                      setSuccess("");
                    }}
                    style={{
                      background: "transparent",
                      border: "none",
                      color: "#07838c",
                      fontWeight: 600,
                      cursor: "pointer",
                      fontSize: "14px"
                    }}
                  >
                    Forgot Password?
                  </button>
                </div>
              )}

            </form>

            {/* SWITCH BETWEEN PAGES */}

            <p className="login-footer">

              {isRegisterMode ? (
                <>
                  Already registered?{" "}

                  <button
                    type="button"
                    onClick={() => {
                      setIsRegisterMode(false);
                      setError("");
                      setSuccess("");
                    }}
                    style={{
                      border: "none",
                      background: "transparent",
                      color: "#07838c",
                      fontWeight: 600,
                      cursor: "pointer"
                    }}
                  >
                    Sign In
                  </button>
                </>
              ) : (
                <>
                  New hospital?{" "}

                  <button
                    type="button"
                    onClick={() => {
                      setIsRegisterMode(true);
                      setError("");
                      setSuccess("");
                    }}
                    style={{
                      border: "none",
                      background: "transparent",
                      color: "#07838c",
                      fontWeight: 600,
                      cursor: "pointer"
                    }}
                  >
                    Register your organization
                  </button>
                </>
              )}

            </p>

          </div>
        </div>
      </div>
    );
  }

  // ---------------------------------------
  // DASHBOARD NAVIGATION
  // ---------------------------------------

  const menuItems = [
    { name: "Dashboard", icon: "▦" },
    { name: "Patients", icon: "♙" },
    { name: "Appointments", icon: "▣" },
    { name: "Care Instructions", icon: "☷" },
    { name: "Reminders", icon: "♧" },

    ...(userRole === "ADMIN"
      ? [{ name: "Audit Logs", icon: "▤" }]
      : [])
  ];

  // ---------------------------------------
  // FORMAT APPOINTMENT DATE
  // ---------------------------------------

  const formatAppointmentDate = (dateValue) => {
    if (!dateValue) return "-";

    return new Date(dateValue).toLocaleString([], {
      dateStyle: "medium",
      timeStyle: "short"
    });
  };

  // ---------------------------------------
  // FORMAT AUDIT DATE
  // ---------------------------------------

  const formatAuditDate = (dateValue) => {
    if (!dateValue) return "-";

    return new Date(dateValue).toLocaleString([], {
      dateStyle: "medium",
      timeStyle: "short"
    });
  };

  // ---------------------------------------
  // DASHBOARD PAGE
  // ---------------------------------------

  return (
    <div className="dashboard-container">

      {/* SIDEBAR */}

      <aside className="sidebar">

        <div className="sidebar-brand">
          <div className="brand-icon">+</div>
          <h2>CareConnect</h2>
        </div>

        <p className="menu-heading">
          MAIN MENU
        </p>

        <nav className="sidebar-menu">

          {menuItems.map((item) => (
            <button
              key={item.name}
              className={`menu-item ${
                activePage === item.name ? "active" : ""
              }`}
              onClick={() => setActivePage(item.name)}
            >
              <span className="menu-icon">
                {item.icon}
              </span>

              {item.name}
            </button>
          ))}

        </nav>

        {/* LOGOUT */}

        <button
          className="logout-button"
          onClick={handleLogout}
        >
          ⇥ Logout
        </button>

      </aside>

      {/* MAIN CONTENT */}

      <main className="dashboard-main">

        {/* TOP NAVIGATION */}

        <header className="topbar">

          <div>
            <h3>Hospital Administration</h3>
            <p>Patient Follow-Up Management System</p>
          </div>

          <div className="admin-profile">

            <div className="admin-avatar">A</div>

            <div>
              <strong>{adminName}</strong>
              <p>{userRole || "User"}</p>
            </div>

          </div>

        </header>

        {/* DASHBOARD CONTENT */}

        <section className="dashboard-content">

          {/* PATIENT MANAGEMENT */}

          {activePage === "Patients" ? (

            <PatientManagement />

          ) : activePage === "Appointments" ? (

            <AppointmentManagement />

          ) : activePage === "Care Instructions" ? (

            <CareInstructionManagement />

          ) : activePage === "Reminders" ? (

            <ReminderManagement />

          ) : activePage === "Audit Logs" && userRole === "ADMIN" ? (

            /* ---------------------------------------
               AUDIT LOGS PAGE
            --------------------------------------- */

            <div className="audit-page">

              <div className="page-heading">

                <div>
                  <h1>Audit Logs</h1>
                  <p>
                    Track activities performed in your organization.
                  </p>
                </div>

                <button
                  className="view-button"
                  onClick={loadAuditLogs}
                  disabled={auditLoading}
                >
                  {auditLoading ? "Refreshing..." : "Refresh"}
                </button>

              </div>

              {auditError && (
                <p className="error-message">
                  {auditError}
                </p>
              )}

              <div className="dashboard-panel">

                <div className="panel-heading">
                  <div>
                    <h2>Activity History</h2>
                    <p>
                      Showing the latest {auditLogs.length} audit records.
                    </p>
                  </div>
                </div>

                {auditLoading ? (

                  <p style={{ padding: "20px" }}>
                    Loading audit logs...
                  </p>

                ) : auditLogs.length === 0 ? (

                  <p style={{ padding: "20px" }}>
                    No audit records found.
                  </p>

                ) : (

                  <div className="table-wrapper">

                    <table>

                      <thead>
                        <tr>
                          <th>Action</th>
                          <th>Entity Type</th>
                          <th>Record ID</th>
                          <th>Performed By</th>
                          <th>Date & Time</th>
                          <th>Details</th>
                        </tr>
                      </thead>

                      <tbody>

                        {auditLogs.map((log) => (

                          <tr key={log.audit_id}>

                            <td>
                              <span className="status">
                                {log.action}
                              </span>
                            </td>

                            <td>
                              {log.entity_type || "-"}
                            </td>

                            <td
                              style={{
                                maxWidth: "180px",
                                wordBreak: "break-all"
                              }}
                            >
                              {log.entity_id || "-"}
                            </td>

                            <td>
                              {log.actor_user_id || "System"}
                            </td>

                            <td>
                              {formatAuditDate(log.created_at)}
                            </td>

                            <td>
                              <details>
                                <summary
                                  style={{
                                    cursor: "pointer",
                                    color: "#07838c"
                                  }}
                                >
                                  View details
                                </summary>

                                <pre
                                  style={{
                                    whiteSpace: "pre-wrap",
                                    wordBreak: "break-word",
                                    fontSize: "12px",
                                    maxWidth: "250px"
                                  }}
                                >
                                  {JSON.stringify(
                                    log.details,
                                    null,
                                    2
                                  )}
                                </pre>

                              </details>
                            </td>

                          </tr>

                        ))}

                      </tbody>

                    </table>

                  </div>

                )}

              </div>

            </div>

          ) : activePage === "Dashboard" ? (

            <>

              {/* DASHBOARD HEADING */}

              <div className="page-heading">

                <div>
                  <h1>Dashboard</h1>

                  <p>
                    Welcome back! Here's your hospital overview.
                  </p>
                </div>

              </div>

              {/* DASHBOARD ERROR */}

              {dashboardError && (
                <p className="error-message">
                  {dashboardError}
                </p>
              )}

              {/* DASHBOARD STATISTICS */}

              <div className="stats-grid">

                {/* TOTAL PATIENTS */}

                <div className="stat-card">

                  <div className="stat-icon patients-icon">
                    ♙
                  </div>

                  <p>Total Patients</p>

                  <h2>
                    {dashboardLoading
                      ? "..."
                      : dashboardData.total_patients}
                  </h2>

                  <span>Registered patients</span>

                </div>

                {/* TODAY'S APPOINTMENTS */}

                <div className="stat-card">

                  <div className="stat-icon appointments-icon">
                    ▣
                  </div>

                  <p>Today's Appointments</p>

                  <h2>
                    {dashboardLoading
                      ? "..."
                      : dashboardData.todays_appointments}
                  </h2>

                  <span>Scheduled for today</span>

                </div>

                {/* MISSED APPOINTMENTS */}

                <div className="stat-card">

                  <div className="stat-icon missed-icon">
                    !
                  </div>

                  <p>Missed Appointments</p>

                  <h2>
                    {dashboardLoading
                      ? "..."
                      : dashboardData.missed_appointments}
                  </h2>

                  <span>Require follow-up</span>

                </div>

                {/* PENDING REMINDERS */}

                <div className="stat-card">

                  <div className="stat-icon reminders-icon">
                    ♧
                  </div>

                  <p>Pending Reminders</p>

                  <h2>
                    {dashboardLoading
                      ? "..."
                      : dashboardData.pending_reminders}
                  </h2>

                  <span>Waiting for processing</span>

                </div>

              </div>

              {/* RECENT APPOINTMENTS */}

              <div className="dashboard-panel">

                <div className="panel-heading">

                  <div>
                    <h2>Recent Appointments</h2>
                    <p>Overview of patient appointments</p>
                  </div>

                  <button
                    className="view-button"
                    onClick={() =>
                      setActivePage("Appointments")
                    }
                  >
                    View All
                  </button>

                </div>

                {/* RECENT APPOINTMENTS TABLE */}

                <div className="table-wrapper">

                  <table>

                    <thead>
                      <tr>
                        <th>Patient Name</th>
                        <th>Appointment Time</th>
                        <th>Doctor</th>
                        <th>Status</th>
                      </tr>
                    </thead>

                    <tbody>

                      {dashboardLoading ? (

                        <tr>
                          <td colSpan="4">
                            Loading appointments...
                          </td>
                        </tr>

                      ) : dashboardData.recent_appointments.length > 0 ? (

                        dashboardData.recent_appointments.map(
                          (appointment) => (

                            <tr key={appointment.appointment_id}>

                              <td>
                                {appointment.patient_name}
                              </td>

                              <td>
                                {formatAppointmentDate(
                                  appointment.appointment_datetime
                                )}
                              </td>

                              <td>
                                {appointment.doctor_name}
                              </td>

                              <td>
                                <span
                                  className={`status ${appointment.status.toLowerCase()}`}
                                >
                                  {appointment.status}
                                </span>
                              </td>

                            </tr>

                          )
                        )

                      ) : (

                        <tr>
                          <td colSpan="4">
                            No appointments found.
                          </td>
                        </tr>

                      )}

                    </tbody>

                  </table>

                </div>

              </div>

              {/* DASHBOARD NOTE */}

              <div className="dashboard-note">
                Dashboard information is retrieved from your
                hospital's database.
              </div>

            </>

          ) : (

            <div className="dashboard-panel placeholder-panel">

              <h1>{activePage}</h1>

              <p>
                The {activePage} module is planned. We will
                implement this feature and connect it to the
                backend next.
              </p>

              <button
                className="view-button"
                onClick={() => setActivePage("Dashboard")}
              >
                Back to Dashboard
              </button>

            </div>

          )}

        </section>

      </main>

    </div>
  );
}

export default App;
