import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000", // adjust if needed
});

// Submit KYC
export const submitKYC = (formData) =>
  API.post("/kyc/submit", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

// Get pending KYCs
export const getPendingKYCs = () =>
  API.get("/kyc/pending");

// Get KYC details
export const getKYCDetails = (kycId) =>
  API.get(`/kyc/${kycId}`);

// Verify KYC
export const verifyKYC = (kycId, decision) =>
  API.post(`/kyc/verify/${kycId}`, { decision });

// Check status
export const getKYCStatus = (kycId) =>
  API.get(`/kyc/status/${kycId}`);
