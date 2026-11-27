
import { useEffect, useState } from "react";
import api from "../api/axios";

function CareInstructionManagement() {
  const [instructions, setInstructions] = useState([]);
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
    instruction_type: "",
    instruction_text: "",
    start_date: "",
    end_date: "",
  });

  // =====================================
  // LOAD PATIENTS, DOCTORS AND INSTRUCTIONS
  // =====================================

  const loadData = async () => {
    setLoading(true);
    setError("");

    try {
      const [patientResponse, doctorResponse, instructionResponse] =
        await Promise.all([
          api.get("/api/patients/"),
          api.get("/api/users/doctors"),
          api.get("/api/care-instructions/"),
        ]);

      setPatients(patientResponse.data);
      setDoctors(doctorResponse.data);
      setInstructions(instructionResponse.data);
    } catch (err) {
      console.error("Care instruction loading error:", err);

      setError(
        err.response?.data?.detail ||
        "Unable to load care instruction data. Please log in again if your session has expired."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // =====================================
  // HANDLE FORM INPUTS
  // =====================================

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  // =====================================
  // CREATE CARE INSTRUCTION
  // =====================================

  const handleAddInstruction = async (e) => {
    e.preventDefault();

    setError("");
    setSuccess("");
    setSaving(true);

    try {
      const requestData = {
        patient_id: formData.patient_id,
        clinician_user_id: formData.clinician_user_id,
        instruction_type: formData.instruction_type,
        instruction_text: formData.instruction_text,
        start_date: formData.start_date || null,
        end_date: formData.end_date || null,
      };

      await api.post("/api/care-instructions/", requestData);

      setSuccess("Care instruction created successfully.");

      setFormData({
        patient_id: "",
        clinician_user_id: "",
        instruction_type: "",
        instruction_text: "",
        start_date: "",
        end_date: "",
      });

      setShowForm(false);

      await loadData();
    } catch (err) {
      console.error("Create instruction error:", err);

      setError(
        err.response?.data?.detail ||
        "Unable to create care instruction."
      );
    } finally {
      setSaving(false);
    }
  };

  // =====================================
  // APPROVE OR CANCEL INSTRUCTION
  // =====================================

  const handleStatusChange = async (instructionId, newStatus) => {
    setError("");
    setSuccess("");

    try {
      if (newStatus === "APPROVED") {
        await api.patch(
          `/api/care-instructions/${instructionId}/approve`
        );

        setSuccess("Care instruction approved successfully.");
      } else if (newStatus === "CANCELLED") {
        await api.patch(
          `/api/care-instructions/${instructionId}/cancel`
        );

        setSuccess("Care instruction cancelled successfully.");
      }

      await loadData();
    } catch (err) {
      console.error("Status update error:", err);

      setError(
        err.response?.data?.detail ||
        "Unable to update care instruction status."
      );
    }
  };

  // =====================================
  // FIND PATIENT AND DOCTOR NAMES
  // =====================================

  const getPatientName = (patientId) => {
    const patient = patients.find(
      (item) => item.patient_id === patientId
    );

    return patient ? patient.patient_name : "Unknown Patient";
  };

  const getDoctorName = (doctorId) => {
    const doctor = doctors.find(
      (item) => item.user_id === doctorId
    );

    return doctor ? doctor.full_name : "Unknown Doctor";
  };

  // =====================================
  // SEARCH AND FILTER
  // =====================================

  const filteredInstructions = instructions.filter((item) => {
    const patientName = getPatientName(item.patient_id);
    const doctorName = getDoctorName(item.clinician_user_id);

    const matchesSearch =
      `${item.instruction_id} ${patientName} ${doctorName} ${item.instruction_text}`
        .toLowerCase()
        .includes(search.toLowerCase());

    const matchesStatus =
      statusFilter === "ALL" ||
      item.approval_status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  // =====================================
  // DATE DISPLAY
  // =====================================

  const formatDate = (value) => {
    if (!value) return "-";
    return value.slice(0, 10);
  };

  // =====================================
  // SUMMARY COUNTS
  // =====================================

  const totalInstructions = instructions.length;

  const draftCount = instructions.filter(
    (item) => item.approval_status === "DRAFT"
  ).length;

  const approvedCount = instructions.filter(
    (item) => item.approval_status === "APPROVED"
  ).length;

  const cancelledCount = instructions.filter(
    (item) => item.approval_status === "CANCELLED"
  ).length;

  // =====================================
  // UI
  // =====================================

  return (
    <div className="care-page">

      <div className="care-heading">
        <div>
          <h1>Care Instructions</h1>
          <p>
            Manage patient medicine, tests and consultation follow-ups.
          </p>
        </div>

        <button
          className="care-add-button"
          onClick={() => setShowForm(!showForm)}
        >
          + Add Care Instruction
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {success && (
        <div className="success-message">
          {success}
        </div>
      )}

      <div className="care-summary">
        <div>
          <span>Total Instructions</span>
          <h2>{totalInstructions}</h2>
        </div>

        <div>
          <span>Draft</span>
          <h2>{draftCount}</h2>
        </div>

        <div>
          <span>Approved</span>
          <h2>{approvedCount}</h2>
        </div>

        <div>
          <span>Cancelled</span>
          <h2>{cancelledCount}</h2>
        </div>
      </div>

      {showForm && (
        <div className="care-form-card">
          <h2>Add New Care Instruction</h2>

          <form onSubmit={handleAddInstruction}>
            <div className="care-form-grid">

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
                <label>Instruction Type</label>

                <select
                  name="instruction_type"
                  value={formData.instruction_type}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select type</option>
                  <option value="MEDICINE">Medicine</option>
                  <option value="TEST">Test</option>
                  <option value="CONSULTATION">Consultation</option>
                </select>
              </div>

              <div>
                <label>Start Date</label>

                <input
                  type="date"
                  name="start_date"
                  value={formData.start_date}
                  onChange={handleChange}
                />
              </div>

              <div>
                <label>End Date</label>

                <input
                  type="date"
                  name="end_date"
                  value={formData.end_date}
                  onChange={handleChange}
                  min={formData.start_date || undefined}
                />
              </div>

              <div className="care-instruction-field">
                <label>Instruction Details</label>

                <textarea
                  name="instruction_text"
                  value={formData.instruction_text}
                  onChange={handleChange}
                  placeholder="Enter care instruction details..."
                  rows="4"
                  required
                />
              </div>

            </div>

            <div className="care-form-actions">

              <button
                type="submit"
                className="care-add-button"
                disabled={saving}
              >
                {saving ? "Saving..." : "Save Instruction"}
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

      <div className="care-table-card">

        <div className="care-table-heading">
          <h2>Care Instruction Records</h2>

          <div className="care-filters">

            <input
              type="text"
              placeholder="Search patient or instruction..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="ALL">All Statuses</option>
              <option value="DRAFT">Draft</option>
              <option value="APPROVED">Approved</option>
              <option value="CANCELLED">Cancelled</option>
            </select>

          </div>
        </div>

        <div className="table-wrapper">

          <table>
            <thead>
              <tr>
                <th>Instruction ID</th>
                <th>Patient</th>
                <th>Doctor</th>
                <th>Type</th>
                <th>Instruction</th>
                <th>Start Date</th>
                <th>End Date</th>
                <th>Status</th>
                <th>Update Status</th>
              </tr>
            </thead>

            <tbody>

              {loading ? (
                <tr>
                  <td colSpan="9">Loading care instructions...</td>
                </tr>
              ) : filteredInstructions.length > 0 ? (

                filteredInstructions.map((item) => (
                  <tr key={item.instruction_id}>

                    <td>{item.instruction_id}</td>

                    <td>{getPatientName(item.patient_id)}</td>

                    <td>
                      {getDoctorName(item.clinician_user_id)}
                    </td>

                    <td>{item.instruction_type}</td>

                    <td>{item.instruction_text}</td>

                    <td>{formatDate(item.start_date)}</td>

                    <td>{formatDate(item.end_date)}</td>

                    <td>
                      <span
                        className={`care-status ${item.approval_status.toLowerCase()}`}
                      >
                        {item.approval_status}
                      </span>
                    </td>

                    <td>
                      <select
                        value={item.approval_status}
                        disabled={item.approval_status !== "DRAFT"}
                        onChange={(e) =>
                          handleStatusChange(
                            item.instruction_id,
                            e.target.value
                          )
                        }
                        aria-label={`Update status for ${item.instruction_id}`}
                      >
                        <option value="DRAFT">Draft</option>
                        <option value="APPROVED">Approve</option>
                        <option value="CANCELLED">Cancel</option>
                      </select>
                    </td>

                  </tr>
                ))

              ) : (
                <tr>
                  <td colSpan="9">
                    No care instructions found.
                  </td>
                </tr>
              )}

            </tbody>
          </table>

        </div>
      </div>

      <p className="care-demo-note">
        Care instructions are managed through the CareConnect backend
        and stored in MySQL.
      </p>

    </div>
  );
}

export default CareInstructionManagement;
