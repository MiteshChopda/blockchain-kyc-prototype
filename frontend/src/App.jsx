
import { BrowserRouter, Routes, Route } from "react-router-dom";
import SubmitKYC from "./pages/SubmitKYC";
import VerifierDashboard from "./pages/VerifierDashboard";
import KYCDetails from "./pages/KYCDetails";
import StatusCheck from "./pages/StatusCheck";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<SubmitKYC />} />
        <Route path="/verifier" element={<VerifierDashboard />} />
        <Route path="/verifier/:kycId" element={<KYCDetails />} />
        <Route path="/status" element={<StatusCheck />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
