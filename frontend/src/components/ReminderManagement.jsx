
import { useEffect, useState } from "react";
import api from "../api/axios";

function ReminderManagement() {

  const [reminders, setReminders] = useState([]);
  const [patients, setPatients] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [instructions, setInstructions] = useState([]);

  const [showForm, setShowForm] = useState(false);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [formData, setFormData] = useState({
    patient_id: "",
    type: "",
    linked_record_id: "",
    channel: "",
    scheduledAt: "",
    message: ""
  });

  // ---------------------------------------
  // LOAD ALL DATA FROM BACKEND
  // ---------------------------------------

  const loadData = async () => {

    try {

      setLoading(true);
      setError("");

      const [
        reminderResponse,
        patientResponse,
        appointmentResponse,
        instructionResponse
      ] = await Promise.all([
        api.get("/api/reminders/"),
        api.get("/api/patients/"),
        api.get("/api/appointments/"),
        api.get("/api/care-instructions/")
      ]);

      setReminders(reminderResponse.data);
      setPatients(patientResponse.data);
      setAppointments(appointmentResponse.data);
      setInstructions(instructionResponse.data);

    } catch (err) {

      console.error("Error loading reminders:", err);

      setError(
        err.response?.data?.detail ||
        "Unable to load reminder information."
      );

    } finally {

      setLoading(false);

    }
  };


  useEffect(() => {
    loadData();
  }, []);


  // ---------------------------------------
  // FORM INPUT CHANGE
  // ---------------------------------------

  const handleChange = (e) => {

    const { name, value } = e.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value
    }));

    if (name === "patient_id" || name === "type") {

      setFormData((previous) => ({
        ...previous,
        [name]: value,
        linked_record_id: ""
      }));

    }
  };


  // ---------------------------------------
  // CREATE REMINDER
  // ---------------------------------------

  const handleAddReminder = async (e) => {

    e.preventDefault();

    setError("");
    setSuccess("");

    try {

      const payload = {

        patient_id: formData.patient_id,

        instruction_id:
          formData.type === "APPOINTMENT"
            ? null
            : formData.linked_record_id,

        appointment_id:
          formData.type === "APPOINTMENT"
            ? formData.linked_record_id
            : null,

        channel: formData.channel,

        reminder_type: formData.type,

        scheduled_at: formData.scheduledAt,

        message_text: formData.message,

        idempotency_key: crypto.randomUUID()

      };

      await api.post("/api/reminders/", payload);

      setSuccess("Reminder created successfully!");

      setFormData({
        patient_id: "",
        type: "",
        linked_record_id: "",
        channel: "",
        scheduledAt: "",
        message: ""
      });

      setShowForm(false);

      await loadData();

    } catch (err) {

      console.error("Error creating reminder:", err);

      setError(
        err.response?.data?.detail ||
        "Unable to create reminder."
      );

    }

  };


  // ---------------------------------------
  // SIMULATE REMINDER
  // ---------------------------------------

  const handleSimulateReminder = async (id) => {

    setError("");
    setSuccess("");

    try {

      await api.patch(
        `/api/reminders/${id}/simulate`
      );

      setSuccess("Reminder delivery simulated successfully!");

      await loadData();

    } catch (err) {

      console.error("Error simulating reminder:", err);

      setError(
        err.response?.data?.detail ||
        "Unable to simulate reminder."
      );

    }

  };


  // ---------------------------------------
  // CANCEL REMINDER
  // ---------------------------------------

  const handleCancelReminder = async (id) => {

    setError("");
    setSuccess("");

    try {

      await api.patch(
        `/api/reminders/${id}/cancel`
      );

      setSuccess("Reminder cancelled successfully!");

      await loadData();

    } catch (err) {

      console.error("Error cancelling reminder:", err);

      setError(
        err.response?.data?.detail ||
        "Unable to cancel reminder."
      );

    }

  };


  // ---------------------------------------
  // GET PATIENT NAME
  // ---------------------------------------

  const getPatientName = (patientId) => {

    const patient = patients.find(
      (p) => p.patient_id === patientId
    );

    return patient?.patient_name || "Unknown Patient";

  };


  // ---------------------------------------
  // GET AVAILABLE LINKED RECORDS
  // ---------------------------------------

  const availableRecords = formData.type === "APPOINTMENT"

    ? appointments.filter(
        (appointment) =>
          appointment.patient_id === formData.patient_id &&
          !["CANCELLED", "MISSED"].includes(appointment.status)
      )

    : instructions.filter(
        (instruction) =>
          instruction.patient_id === formData.patient_id &&
          instruction.instruction_type === formData.type &&
          instruction.approval_status === "APPROVED"
      );


  // ---------------------------------------
  // SEARCH AND STATUS FILTER
  // ---------------------------------------

  const filteredReminders = reminders.filter((reminder) => {

    const patientName = getPatientName(reminder.patient_id);

    const matchesSearch =
      `${reminder.reminder_id} ${patientName} ${reminder.reminder_type}`
        .toLowerCase()
        .includes(search.toLowerCase());

    const matchesStatus =
      statusFilter === "ALL" ||
      reminder.status === statusFilter;

    return matchesSearch && matchesStatus;

  });


  // ---------------------------------------
  // SUMMARY COUNTS
  // ---------------------------------------

  const pendingCount = reminders.filter(
    (r) => r.status === "PENDING"
  ).length;

  const simulatedCount = reminders.filter(
    (r) => r.status === "SIMULATED"
  ).length;

  const failedCount = reminders.filter(
    (r) => r.status === "FAILED"
  ).length;


  // ---------------------------------------
  // FORMAT DATE
  // ---------------------------------------

  const formatDate = (dateValue) => {

    if (!dateValue) return "-";

    return new Date(dateValue).toLocaleString();

  };


  // ---------------------------------------
  // FRONTEND
  // ---------------------------------------

  return (

    <div className="reminder-page">

      <div className="reminder-heading">

        <div>
          <h1>Reminder Management</h1>
          <p>Schedule and track patient follow-up reminders.</p>
        </div>

        <button
          className="reminder-add-button"
          onClick={() => {
            setShowForm(!showForm);
            setError("");
            setSuccess("");
          }}
        >
          + Create Reminder
        </button>

      </div>


      {/* SUCCESS AND ERROR MESSAGES */}

      {success && (
        <p className="success-message">{success}</p>
      )}

      {error && (
        <p className="error-message">{error}</p>
      )}


      {/* SUMMARY CARDS */}

      <div className="reminder-summary">

        <div>
          <span>Total Reminders</span>
          <h2>{reminders.length}</h2>
        </div>

        <div>
          <span>Pending</span>
          <h2>{pendingCount}</h2>
        </div>

        <div>
          <span>Simulated</span>
          <h2>{simulatedCount}</h2>
        </div>

        <div>
          <span>Failed</span>
          <h2>{failedCount}</h2>
        </div>

      </div>


      {/* CREATE REMINDER FORM */}

      {showForm && (

        <div className="reminder-form-card">

          <h2>Create New Reminder</h2>

          <form onSubmit={handleAddReminder}>

            <div className="reminder-form-grid">

              {/* PATIENT */}

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


              {/* REMINDER TYPE */}

              <div>

                <label>Reminder Type</label>

                <select
                  name="type"
                  value={formData.type}
                  onChange={handleChange}
                  required
                >

                  <option value="">Select type</option>

                  <option value="APPOINTMENT">Appointment</option>

                  <option value="MEDICINE">Medicine</option>

                  <option value="TEST">Test</option>

                  <option value="CONSULTATION">Consultation</option>

                </select>

              </div>


              {/* LINKED APPOINTMENT OR INSTRUCTION */}

              <div>

                <label>
                  {formData.type === "APPOINTMENT"
                    ? "Select Appointment"
                    : "Select Approved Care Instruction"}
                </label>

                <select
                  name="linked_record_id"
                  value={formData.linked_record_id}
                  onChange={handleChange}
                  required
                  disabled={!formData.patient_id || !formData.type}
                >

                  <option value="">
                    Select linked record
                  </option>

                  {availableRecords.map((record) => (

                    <option
                      key={
                        formData.type === "APPOINTMENT"
                          ? record.appointment_id
                          : record.instruction_id
                      }
                      value={
                        formData.type === "APPOINTMENT"
                          ? record.appointment_id
                          : record.instruction_id
                      }
                    >

                      {formData.type === "APPOINTMENT"

                        ? `${formatDate(record.appointment_datetime)} - ${record.appointment_type}`

                        : `${record.instruction_type} - ${record.instruction_text}`

                      }

                    </option>

                  ))}

                </select>

                {formData.patient_id &&
                  formData.type &&
                  availableRecords.length === 0 && (

                    <small>
                      No matching records found for this patient.
                    </small>

                  )}

              </div>


              {/* CHANNEL */}

              <div>

                <label>Reminder Channel</label>

                <select
                  name="channel"
                  value={formData.channel}
                  onChange={handleChange}
                  required
                >

                  <option value="">Select channel</option>

                  <option value="SMS">SMS</option>

                  <option value="WHATSAPP">WhatsApp</option>

                </select>

              </div>


              {/* SCHEDULED DATE */}

              <div>

                <label>Scheduled Date and Time</label>

                <input
                  type="datetime-local"
                  name="scheduledAt"
                  value={formData.scheduledAt}
                  onChange={handleChange}
                  min={new Date().toLocaleString("sv-SE").replace(" ", "T").slice(0, 16)}
                  required
                />

              </div>


              {/* MESSAGE */}

              <div className="reminder-message-field">

                <label>Reminder Message</label>

                <textarea
                  name="message"
                  value={formData.message}
                  onChange={handleChange}
                  placeholder="Enter reminder message..."
                  rows="4"
                  required
                />

              </div>

            </div>


            {/* FORM BUTTONS */}

            <div className="reminder-form-actions">

              <button
                type="submit"
                className="reminder-add-button"
              >
                Save Reminder
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


      {/* REMINDER TABLE */}

      <div className="reminder-table-card">

        <div className="reminder-table-heading">

          <h2>Reminder Records</h2>

          <div className="reminder-filters">

            <input
              type="text"
              placeholder="Search patient or reminder ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >

              <option value="ALL">All Statuses</option>

              <option value="PENDING">Pending</option>

              <option value="SIMULATED">Simulated</option>

              <option value="SENT">Sent</option>

              <option value="FAILED">Failed</option>

              <option value="CANCELLED">Cancelled</option>

            </select>

          </div>

        </div>


        <div className="table-wrapper">

          <table>

            <thead>

              <tr>
                <th>Reminder ID</th>
                <th>Patient</th>
                <th>Type</th>
                <th>Channel</th>
                <th>Scheduled At</th>
                <th>Message</th>
                <th>Status</th>
                <th>Action</th>
              </tr>

            </thead>


            <tbody>

              {loading ? (

                <tr>
                  <td colSpan="8">Loading reminders...</td>
                </tr>

              ) : filteredReminders.length > 0 ? (

                filteredReminders.map((reminder) => (

                  <tr key={reminder.reminder_id}>

                    <td>{reminder.reminder_id}</td>

                    <td>
                      {getPatientName(reminder.patient_id)}
                    </td>

                    <td>{reminder.reminder_type}</td>

                    <td>{reminder.channel}</td>

                    <td>{formatDate(reminder.scheduled_at)}</td>

                    <td>{reminder.message_text}</td>

                    <td>

                      <span
                        className={`reminder-status ${reminder.status.toLowerCase()}`}
                      >
                        {reminder.status}
                      </span>

                    </td>

                    <td>

                      {reminder.status === "PENDING" ? (

                        <div className="reminder-form-actions">

                          <button
                            className="simulate-button"
                            onClick={() =>
                              handleSimulateReminder(reminder.reminder_id)
                            }
                          >
                            Simulate
                          </button>

                          <button
                            className="cancel-button"
                            onClick={() =>
                              handleCancelReminder(reminder.reminder_id)
                            }
                          >
                            Cancel
                          </button>

                        </div>

                      ) : (

                        "-"

                      )}

                    </td>

                  </tr>

                ))

              ) : (

                <tr>
                  <td colSpan="8">No reminders found.</td>
                </tr>

              )}

            </tbody>

          </table>

        </div>

      </div>


      <p className="reminder-demo-note">
        Demo only. Delivery simulation records a status change in the
        database. No real SMS or WhatsApp messages are sent.
      </p>

    </div>

  );

}

export default ReminderManagement;
