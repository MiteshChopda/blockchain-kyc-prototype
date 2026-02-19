
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getKYCDetails, verifyKYC, getKYCStatus } from "../api/kycApi";
import Navbar from "../components/Navbar";

function KYCDetails() {
  const { kycId } = useParams();

  const [data, setData] = useState(null);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchAll();
  }, [kycId]);

  const fetchAll = async () => {
    try {
      setLoading(true);

      const [detailsRes, statusRes] = await Promise.all([
        getKYCDetails(kycId),
        getKYCStatus(kycId),
      ]);

      setData(detailsRes.data);
      setStatus(statusRes.data.status);
    } catch (err) {
      setMessage("Failed to load KYC details");
    } finally {
      setLoading(false);
    }
  };

  const handleDecision = async (decision) => {
    if (status !== "PENDING") return;

    try {
      setSubmitting(true);
      await verifyKYC(kycId, decision);
      setStatus(decision);
      setMessage(`KYC ${decision}`);
    } catch (err) {
      setMessage("Verification failed");
    } finally {
      setSubmitting(false);
    }
  };

  // ✅ Loading state
  if (loading) {
    return (
      <div>
        <Navbar />
        <div className="container">
          <div className="card">
            <p>Loading KYC details...</p>
          </div>
        </div>
      </div>
    );
  }

  // ✅ Not found safety
  if (!data || data.error) {
    return (
      <div>
        <Navbar />
        <div className="container">
          <div className="card">
            <p>KYC not found</p>
          </div>
        </div>
      </div>
    );
  }

  const isLocked = status !== "PENDING";

  return (
    <div>
      <Navbar />

      <div className="container">
        <div className="card">
          <h2>KYC Review</h2>

          {/* Status badge */}
          <p style={{ marginBottom: "16px" }}>
            <strong>Status:</strong>{" "}

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

          {/* User data */}
          <p><strong>Name:</strong> {data.name}</p>
          <p><strong>DOB:</strong> {data.dob}</p>
          <p><strong>Address:</strong> {data.address}</p>
          <p><strong>Document ID:</strong> {data.documentId}</p>

          {/* ✅ Document view link */}
          {data.document_path && (
            <p style={{ marginTop: "12px" }}>
              <a
                href={`http://localhost:8000/${data.document_path}`}
                target="_blank"
                rel="noreferrer"
                className=" link-primary"
              >
                View Uploaded Document →
              </a>
            </p>
          )}

          {/* Actions */}
          <div style={{ marginTop: "24px" }}>
            <button
              onClick={() => handleDecision("VERIFIED")}
              disabled={isLocked || submitting}
            >
              Approve
            </button>

            <button
              className="secondary"
              onClick={() => handleDecision("REJECTED")}
              disabled={isLocked || submitting}
              style={{ marginLeft: "10px" }}
            >
              Reject
            </button>
          </div>

          {/* Lock notice */}
          {isLocked && (
            <p className="message">
              This KYC has already been processed.
            </p>
          )}

          {/* Message */}
          {message && <p className="message">{message}</p>}
        </div>
      </div>
    </div >
  );
}

export default KYCDetails;

