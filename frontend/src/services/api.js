import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

export const pharmacyService = {
  // MAIN CHAT
  sendChatMessage: async (message, patient) => {
    return api.post("/chat", {
      user_id: patient.name, // must match backend
      message: message,
    });
  },

  // QUANTITY CONTINUATION
  sendQuantity: async (userId, medicine, quantity) => {
    return api.post("/chat/quantity", {
      user_id: userId,
      medicine: medicine,
      quantity: quantity,
    });
  },

  // UPLOAD RX
  uploadPrescription: async (userId, medicineName, file) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post(`/upload-prescription/${userId}/${medicineName}`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  // FINAL CHECKOUT
  finalizeCheckout: async (patientId, items) => {
    return api.post("/finalize-checkout", {
      patient_id: patientId,
      items: items,
    });
  },

  getProducts: async () => {
    return api.get("/products");
  },

  // ADMIN
  getInventory: async () => {
    return api.get("/admin/inventory");
  },

  getLowStock: async () => {
    return api.get("/admin/low-stock");
  },

  getRefillAlerts: async () => {
    return api.get("/admin/refill-alerts");
  },

  getTraces: async () => {
    return api.get("/admin/traces");
  },

  refillStock: async (medicineName, amount) => {
    return api.post("/admin/refill-stock", {
      medicine_name: medicineName,
      amount: amount
    });
  },

  testRefillEmail: async (userId, medicineName) => {
    return api.post("/admin/test-refill-email", {
      user_id: userId,
      medicine_name: medicineName
    });
  }
};
