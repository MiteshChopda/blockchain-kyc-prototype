
import Navbar from "../components/Navbar";
import { useState } from "react";
import { submitKYC } from "../api/kycApi";

function SubmitKYC() {
  const [form, setForm] = useState({
    name: "",
    dob: "",
    address: "",
    documentId: "",
  });
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();

    const formData = new FormData();
    Object.entries(form).forEach(([k, v]) =>
      formData.append(k, v)
    );
    formData.append("file", file);

    try {
      const res = await submitKYC(formData);
      setMessage(`Submitted! KYC ID: ${res.data.kycId}`);
    } catch (err) {
      setMessage("Submission failed");
    }
  };

  return (
    <div>
      <Navbar />
      <div className="container">
        <div className="card">
          <h2>Submit KYC</h2>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <input name="name" placeholder="Name" onChange={handleChange} required />
            </div>

            <div className="form-group">
              <input name="dob" type="date" onChange={handleChange} required />
            </div>

            <div className="form-group">
              <input name="address" placeholder="Address" onChange={handleChange} required />
            </div>

            <div className="form-group">
              <input name="documentId" placeholder="Document ID" onChange={handleChange} required />
            </div>

            <div className="form-group">
              <input type="file" onChange={(e) => setFile(e.target.files[0])} required />
            </div>

            <button type="submit">Submit KYC</button>
          </form>

          {message && <p className="message">{message}</p>}
        </div>
      </div>
    </div>
  );
}

export default SubmitKYC;
