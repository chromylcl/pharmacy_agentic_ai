import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000'; // Adjust to your FastAPI port

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' }
});

export const pharmacyService = {
  // 1. Trigger the 7-Agent Orchestrator
  sendChatMessage: async (message, patientData) => {
    return api.post('/chat', {
      message,
      patient_name: patientData.name,
      patient_age: patientData.age,
      mode: patientData.mode
    });
  },

  // 2. Real-time Inventory Sync
  getInventory: async () => {
    return api.get('/inventory');
  },

  // 3. Prescription Verification (Vision/OCR)
  uploadPrescription: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/upload-rx', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },

  // 4. Final Checkout & DB Update
  processCheckout: async (cartItems, patientName) => {
    return api.post('/checkout', {
      items: cartItems,
      patient: patientName
    });
  }
};