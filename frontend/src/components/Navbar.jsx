
import { Link } from "react-router-dom";

function Navbar() {
  return (
    <div className="navbar">
      <Link to="/">Submit KYC</Link>
      <Link to="/verifier">Verifier</Link>
      <Link to="/status">Check Status</Link>
    </div>
  );
}

export default Navbar;

