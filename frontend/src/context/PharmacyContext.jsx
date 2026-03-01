import { createContext, useContext, useState } from 'react';

const PharmacyContext = createContext();

export const PharmacyProvider = ({ children }) => {
  // 1. Patient Session State
  const [patient, setPatient] = useState({ name: '', age: '', mode: 'standard' });
  const [isAuth, setIsAuth] = useState(false);

  // 2. Chat & 7-Agent Status Tracking
  const [messages, setMessages] = useState([]);
  const [agentStatus, setAgentStatus] = useState({
    orchestrator: 'idle',
    pharmacist: 'idle',
    physician: 'idle',
    regulatory: 'idle',
    inventory: 'idle',
    billing: 'idle',
    refill: 'idle'
  });

  // 3. Storefront & Cart Persistence
  const [cart, setCart] = useState([]);
  const [isBillingOpen, setIsBillingOpen] = useState(false);

  return (
    <PharmacyContext.Provider value={{ 
      patient, setPatient, 
      isAuth, setIsAuth, 
      messages, setMessages,
      agentStatus, setAgentStatus,
      cart, setCart,
      isBillingOpen, setIsBillingOpen 
    }}>
      {children}
    </PharmacyContext.Provider>
  );
};

export const usePharmacy = () => useContext(PharmacyContext);