
import { useEffect, useState } from "react";
import { getPendingKYCs } from "../api/kycApi";
import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";

function VerifierDashboard() {
  const [pending, setPending] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchPending();
  }, []);

  const fetchPending = async () => {
    try {
      const res = await getPendingKYCs();
      setPending(res.data.pending || []);
    } catch (err) {
      setError("Failed to load pending KYCs");
    }
  };

  return (
    <div>
      <Navbar />
      <div className="container">
        <div className="card">
          <h2>Pending KYCs</h2>

          {error && <p className="message">{error}</p>}

          {pending.length === 0 && <p className="empty">No pending KYCs</p>}

          {pending.map((id) => (
            <div key={id} className="list-item">
              <Link className="link-primary" to={`/verifier/${id}`}>
                {id}
              </Link>
            </div>
          ))}

        </div>
      </div>
    </div>
  );
  ;
}

export default VerifierDashboard;
