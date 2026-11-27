
import { useEffect, useState } from "react";
import api from "../api/axios";

function PatientManagement() {
  const [patients, setPatients] = useState([]);
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const emptyForm = {
    patient_name: "",
    date_of_birth: "",
    gender: "",
    phone_number: "",
    email: "",
    consent_sms: false,
    consent_whatsapp: false
  };

  const [formData, setFormData] = useState(emptyForm);

  // FETCH PATIENTS
  const fetchPatients = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/api/patients/");
      setPatients(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Unable to load patients."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, []);

  // CALCULATE AGE
  const calculateAge = (dob) => {
    if (!dob) return "-";

    const birth = new Date(dob);
    const today = new Date();

    let age = today.getFullYear() - birth.getFullYear();

    if (
      today.getMonth() < birth.getMonth() ||
      (
        today.getMonth() === birth.getMonth() &&
        today.getDate() < birth.getDate()
      )
    ) {
      age--;
    }

    return age;
  };

  // HANDLE FORM CHANGES
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    setFormData((previous) => ({
      ...previous,
      [name]: type === "checkbox" ? checked : value
    }));
  };

  // ADD OR UPDATE PATIENT
  const handleSubmit = async (e) => {
    e.preventDefault();

    setSaving(true);
    setError("");
    setSuccess("");

    const patientData = {
      ...formData,
      date_of_birth: formData.date_of_birth || null,
      email: formData.email || null
    };

    try {
      if (editingId) {
        await api.put(
          `/api/patients/${editingId}`,
          patientData
        );

        setSuccess("Patient updated successfully!");
      } else {
        await api.post("/api/patients/", patientData);

        setSuccess("Patient added successfully!");
      }

      setFormData(emptyForm);
      setShowForm(false);
      setEditingId(null);

      await fetchPatients();

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Unable to save patient details."
      );
    } finally {
      setSaving(false);
    }
  };

  // OPEN EDIT FORM
  const handleEdit = (patient) => {
    setEditingId(patient.patient_id);

    setFormData({
      patient_name: patient.patient_name || "",
      date_of_birth: patient.date_of_birth
        ? String(patient.date_of_birth).slice(0, 10)
        : "",
      gender: patient.gender || "",
      phone_number: patient.phone_number || "",
      email: patient.email || "",
      consent_sms: patient.consent_sms,
      consent_whatsapp: patient.consent_whatsapp
    });

    setShowForm(true);
    setError("");
    setSuccess("");
  };

  // DELETE PATIENT (SOFT DELETE)
  const handleDelete = async (patient) => {
    const confirmed = window.confirm(
      `Are you sure you want to deactivate ${patient.patient_name}?`
    );

    if (!confirmed) return;

    setError("");
    setSuccess("");

    try {
      await api.delete(
        `/api/patients/${patient.patient_id}`
      );

      setSuccess("Patient deactivated successfully!");

      await fetchPatients();

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Unable to delete patient."
      );
    }
  };

  // SEARCH ACTIVE PATIENTS
  const filteredPatients = patients.filter((patient) =>
    `${patient.patient_name} ${patient.patient_id} ${patient.phone_number}`
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  return (
    <div className="patient-page">

      <div className="patient-heading">
        <div>
          <h1>Patient Management</h1>
          <p>View and manage registered patients.</p>
        </div>

        <button
          className="add-patient-button"
          onClick={() => {
            setFormData(emptyForm);
            setEditingId(null);
            setShowForm(!showForm);
            setError("");
            setSuccess("");
          }}
        >
          + Add New Patient
        </button>
      </div>

      {success && (
        <p className="success-message">{success}</p>
      )}

      {error && (
        <p className="error-message">{error}</p>
      )}

      <div className="patient-summary">
        <div>
          <span>Total Patients</span>
          <h2>{patients.length}</h2>
        </div>

        <div>
          <span>Active Patients</span>
          <h2>
            {patients.filter((p) => p.is_active).length}
          </h2>
        </div>
      </div>

      {showForm && (
        <div className="patient-form-card">
          <h2>
            {editingId ? "Edit Patient" : "Add New Patient"}
          </h2>

          <form onSubmit={handleSubmit}>
            <div className="patient-form-grid">

              <div>
                <label>Patient Name</label>
                <input
                  name="patient_name"
                  value={formData.patient_name}
                  onChange={handleChange}
                  required
                />
              </div>

              <div>
                <label>Date of Birth</label>
                <input
                  name="date_of_birth"
                  type="date"
                  value={formData.date_of_birth}
                  onChange={handleChange}
                  max={new Date().toISOString().split("T")[0]}
                />
              </div>

              <div>
                <label>Gender</label>
                <select
                  name="gender"
                  value={formData.gender}
                  onChange={handleChange}
                >
                  <option value="">Select gender</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div>
                <label>Phone Number</label>
                <input
                  name="phone_number"
                  type="tel"
                  value={formData.phone_number}
                  onChange={handleChange}
                  required
                />
              </div>

              <div>
                <label>Email Address</label>
                <input
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                />
              </div>

            </div>

            <div style={{ marginTop: "15px" }}>
              <label>
                <input
                  type="checkbox"
                  name="consent_sms"
                  checked={formData.consent_sms}
                  onChange={handleChange}
                />
                {" "}SMS consent
              </label>

              <br />

              <label>
                <input
                  type="checkbox"
                  name="consent_whatsapp"
                  checked={formData.consent_whatsapp}
                  onChange={handleChange}
                />
                {" "}WhatsApp consent
              </label>
            </div>

            <div className="patient-form-actions">
              <button
                type="submit"
                className="add-patient-button"
                disabled={saving}
              >
                {saving
                  ? "Saving..."
                  : editingId
                    ? "Update Patient"
                    : "Save Patient"}
              </button>

              <button
                type="button"
                className="cancel-button"
                onClick={() => {
                  setShowForm(false);
                  setEditingId(null);
                  setFormData(emptyForm);
                }}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="patient-table-card">

        <div className="patient-table-heading">
          <h2>Patient Records</h2>

          <input
            className="patient-search"
            type="text"
            placeholder="Search by name, ID or phone..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Patient ID</th>
                <th>Patient Name</th>
                <th>Age</th>
                <th>Gender</th>
                <th>Phone Number</th>
                <th>Email</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="7">Loading patients...</td>
                </tr>
              ) : filteredPatients.length > 0 ? (
                filteredPatients.map((patient) => (
                  <tr key={patient.patient_id}>
                    <td>{patient.patient_id}</td>
                    <td>{patient.patient_name}</td>
                    <td>{calculateAge(patient.date_of_birth)}</td>
                    <td>{patient.gender || "-"}</td>
                    <td>{patient.phone_number}</td>
                    <td>{patient.email || "-"}</td>

                    <td>
                      <button
                        type="button"
                        onClick={() => handleEdit(patient)}
                      >
                        Edit
                      </button>

                      {" "}

                      <button
                        type="button"
                        onClick={() => handleDelete(patient)}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="7">No patients found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

      </div>

      <p className="patient-demo-note">
        Patient records are managed through the CareConnect backend
        and stored in MySQL.
      </p>

    </div>
  );
}

export default PatientManagement;
