
import { useState } from "react";
import { getKYCStatus } from "../api/kycApi";
import Navbar from "../components/Navbar";

function StatusCheck() {
  const [kycId, setKycId] = useState("");
  const [status, setStatus] = useState("");

  const handleCheck = async () => {
    try {
      const res = await getKYCStatus(kycId);
      setStatus(res.data.status);
    } catch (err) {
      setStatus("Failed to fetch status");
    }
  };

  return (
    <div>
      <Navbar />
      <div className="container">
        <div className="card">
          <h2>Check KYC Status</h2>

          <div className="form-group">
            <input
              placeholder="Enter KYC ID"
              value={kycId}
              onChange={(e) => setKycId(e.target.value)}
            />
          </div>

          <button onClick={handleCheck}>Check Status</button>

          {status && (
            <p className="message">
              Status:{" "}
              <span
                className={`badge ${status === "VERIFIED"
                  ? "verified"
                  : status === "REJECTED"
                    ? "rejected"
                    : "pending"
                  }`}
              >
                {status}
              </span>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export default StatusCheck;
