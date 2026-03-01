import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { PharmacyProvider } from './context/PharmacyContext'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <PharmacyProvider>
      <App />
    </PharmacyProvider>
  </StrictMode>,
)