
import { useEffect, useState } from "react";
import api from "../api/axios";

function AppointmentManagement() {
  const [appointments, setAppointments] = useState([]);
  const [patients, setPatients] = useState([]);
  const [doctors, setDoctors] = useState([]);

  const [showForm, setShowForm] = useState(false);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [formData, setFormData] = useState({
    patient_id: "",
    clinician_user_id: "",
    date: "",
    time: "",
    type: ""
  });

  // =========================================
  // 1. FETCH PATIENTS, DOCTORS AND APPOINTMENTS
  // =========================================

  const fetchData = async () => {
    try {
      setLoading(true);
      setError("");

      const [patientResponse, doctorResponse, appointmentResponse] =
        await Promise.all([
          api.get("/api/patients/"),
          api.get("/api/users/doctors"),
          api.get("/api/appointments/")
        ]);

      setPatients(patientResponse.data);
      setDoctors(doctorResponse.data);
      setAppointments(appointmentResponse.data);

    } catch (err) {
      console.error("Error fetching appointment data:", err);

      setError(
        err.response?.data?.detail ||
        "Unable to load appointment data. Please try again."
      );

    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // =========================================
  // 2. HANDLE FORM INPUT CHANGES
  // =========================================

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  // =========================================
  // 3. ADD NEW APPOINTMENT
  // =========================================

  const handleAddAppointment = async (e) => {
    e.preventDefault();

    try {
      setSaving(true);
      setError("");
      setSuccess("");

      const appointmentData = {
        patient_id: formData.patient_id,
        clinician_user_id: formData.clinician_user_id,
        appointment_datetime: `${formData.date}T${formData.time}:00`,
        appointment_type: formData.type
      };

      await api.post("/api/appointments/", appointmentData);

      setFormData({
        patient_id: "",
        clinician_user_id: "",
        date: "",
        time: "",
        type: ""
      });

      setShowForm(false);
      setSuccess("Appointment scheduled successfully.");

      await fetchData();

    } catch (err) {
      console.error("Error creating appointment:", err);

      setError(
        err.response?.data?.detail ||
        "Unable to schedule appointment."
      );

    } finally {
      setSaving(false);
    }
  };

  // =========================================
  // 4. UPDATE APPOINTMENT STATUS
  // =========================================

  const handleStatusChange = async (appointmentId, newStatus) => {
    try {
      setError("");
      setSuccess("");

      await api.put(`/api/appointments/${appointmentId}`, {
        status: newStatus
      });

      setSuccess("Appointment status updated successfully.");

      await fetchData();

    } catch (err) {
      console.error("Error updating appointment:", err);

      setError(
        err.response?.data?.detail ||
        "Unable to update appointment status."
      );
    }
  };

  // =========================================
  // 5. GET PATIENT AND DOCTOR NAMES
  // =========================================

  const getPatientName = (patientId) => {
    const patient = patients.find(
      (p) => p.patient_id === patientId
    );

    return patient ? patient.patient_name : "Unknown Patient";
  };

  const getDoctorName = (doctorId) => {
    const doctor = doctors.find(
      (d) => d.user_id === doctorId
    );

    return doctor ? doctor.full_name : "Unknown Doctor";
  };

  // =========================================
  // 6. SEARCH AND FILTER APPOINTMENTS
  // =========================================

  const filteredAppointments = appointments.filter((appointment) => {
    const patientName = getPatientName(appointment.patient_id);
    const doctorName = getDoctorName(appointment.clinician_user_id);

    const matchesSearch =
      `${appointment.appointment_id} ${patientName} ${doctorName}`
        .toLowerCase()
        .includes(search.toLowerCase());

    const matchesStatus =
      statusFilter === "ALL" ||
      appointment.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  // =========================================
  // 7. DATE AND TIME DISPLAY
  // =========================================

  const getAppointmentDate = (dateTime) => {
    return dateTime ? dateTime.substring(0, 10) : "";
  };

  const getAppointmentTime = (dateTime) => {
    return dateTime ? dateTime.substring(11, 16) : "";
  };

  const getToday = () => {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, "0");
    const day = String(today.getDate()).padStart(2, "0");

    return `${year}-${month}-${day}`;
  };

  const statusClass = (status) => status.toLowerCase();

  // =========================================
  // 8. USER INTERFACE
  // =========================================

  return (
    <div className="appointment-page">

      <div className="appointment-heading">
        <div>
          <h1>Appointment Management</h1>
          <p>Schedule and track patient appointments.</p>
        </div>

        <button
          className="add-appointment-button"
          onClick={() => {
            setShowForm(!showForm);
            setError("");
            setSuccess("");
          }}
        >
          + Schedule Appointment
        </button>
      </div>

      {error && (
        <p className="appointment-error">
          {error}
        </p>
      )}

      {success && (
        <p className="appointment-success">
          {success}
        </p>
      )}

      {/* APPOINTMENT SUMMARY */}

      <div className="appointment-summary">

        <div className="appointment-summary-card">
          <span>Total Appointments</span>
          <h2>{appointments.length}</h2>
        </div>

        <div className="appointment-summary-card">
          <span>Scheduled</span>
          <h2>
            {appointments.filter(
              (a) => a.status === "SCHEDULED"
            ).length}
          </h2>
        </div>

        <div className="appointment-summary-card">
          <span>Attended</span>
          <h2>
            {appointments.filter(
              (a) => a.status === "ATTENDED"
            ).length}
          </h2>
        </div>

        <div className="appointment-summary-card">
          <span>Missed</span>
          <h2>
            {appointments.filter(
              (a) => a.status === "MISSED"
            ).length}
          </h2>
        </div>

      </div>

      {/* ADD APPOINTMENT FORM */}

      {showForm && (
        <div className="appointment-form-card">

          <h2>Schedule New Appointment</h2>

          <form onSubmit={handleAddAppointment}>

            <div className="appointment-form-grid">

              <div>
                <label>Patient Name</label>

                <select
                  name="patient_id"
                  value={formData.patient_id}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select patient</option>

                  {patients.map((patient) => (
                    <option
                      key={patient.patient_id}
                      value={patient.patient_id}
                    >
                      {patient.patient_name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label>Doctor</label>

                <select
                  name="clinician_user_id"
                  value={formData.clinician_user_id}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select doctor</option>

                  {doctors.map((doctor) => (
                    <option
                      key={doctor.user_id}
                      value={doctor.user_id}
                    >
                      {doctor.full_name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label>Appointment Date</label>

                <input
                  type="date"
                  name="date"
                  value={formData.date}
                  onChange={handleChange}
                  min={getToday()}
                  required
                />
              </div>

              <div>
                <label>Appointment Time</label>

                <input
                  type="time"
                  name="time"
                  value={formData.time}
                  onChange={handleChange}
                  required
                />
              </div>

              <div>
                <label>Appointment Type</label>

                <select
                  name="type"
                  value={formData.type}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select type</option>
                  <option value="General Checkup">General Checkup</option>
                  <option value="Follow-up">Follow-up</option>
                  <option value="Consultation">Consultation</option>
                  <option value="Test">Test</option>
                </select>
              </div>

            </div>

            <div className="appointment-form-actions">

              <button
                type="submit"
                className="add-appointment-button"
                disabled={saving}
              >
                {saving ? "Saving..." : "Save Appointment"}
              </button>

              <button
                type="button"
                className="cancel-button"
                onClick={() => setShowForm(false)}
              >
                Cancel
              </button>

            </div>

          </form>
        </div>
      )}

      {/* APPOINTMENT TABLE */}

      <div className="appointment-table-card">

        <div className="appointment-table-heading">
          <h2>Appointment Records</h2>

          <div className="appointment-filters">

            <input
              type="text"
              placeholder="Search patient or appointment ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="ALL">All Statuses</option>
              <option value="SCHEDULED">Scheduled</option>
              <option value="CONFIRMED">Confirmed</option>
              <option value="ATTENDED">Attended</option>
              <option value="MISSED">Missed</option>
              <option value="RESCHEDULED">Rescheduled</option>
              <option value="CANCELLED">Cancelled</option>
            </select>

          </div>
        </div>

        <div className="table-wrapper">

          <table>

            <thead>
              <tr>
                <th>Appointment ID</th>
                <th>Patient</th>
                <th>Doctor</th>
                <th>Date</th>
                <th>Time</th>
                <th>Type</th>
                <th>Status</th>
                <th>Update Status</th>
              </tr>
            </thead>

            <tbody>

              {loading ? (
                <tr>
                  <td colSpan="8">Loading appointments...</td>
                </tr>
              ) : filteredAppointments.length > 0 ? (

                filteredAppointments.map((appointment) => (

                  <tr key={appointment.appointment_id}>

                    <td>{appointment.appointment_id}</td>

                    <td>
                      {getPatientName(appointment.patient_id)}
                    </td>

                    <td>
                      {getDoctorName(appointment.clinician_user_id)}
                    </td>

                    <td>
                      {getAppointmentDate(
                        appointment.appointment_datetime
                      )}
                    </td>

                    <td>
                      {getAppointmentTime(
                        appointment.appointment_datetime
                      )}
                    </td>

                    <td>
                      {appointment.appointment_type || "-"}
                    </td>

                    <td>
                      <span
                        className={`appointment-status ${statusClass(
                          appointment.status
                        )}`}
                      >
                        {appointment.status}
                      </span>
                    </td>

                    <td>
                      <select
                        value={appointment.status}
                        onChange={(e) =>
                          handleStatusChange(
                            appointment.appointment_id,
                            e.target.value
                          )
                        }
                        aria-label={`Update status for ${appointment.appointment_id}`}
                      >
                        <option value="SCHEDULED">Scheduled</option>
                        <option value="CONFIRMED">Confirmed</option>
                        <option value="ATTENDED">Attended</option>
                        <option value="MISSED">Missed</option>
                        <option value="RESCHEDULED">Rescheduled</option>
                        <option value="CANCELLED">Cancelled</option>
                      </select>
                    </td>

                  </tr>

                ))

              ) : (

                <tr>
                  <td colSpan="8">No appointments found.</td>
                </tr>

              )}

            </tbody>

          </table>

        </div>
      </div>

      <p className="appointment-demo-note">
        Appointment records are connected to the backend and stored in MySQL.
      </p>

    </div>
  );
}

export default AppointmentManagement;
