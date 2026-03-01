import { useState } from 'react';
import { usePharmacy } from './context/PharmacyContext';
import Onboarding from './pages/Onboarding';
import Navbar from './components/UI/Navbar';
import UserChat from './pages/UserChat';
import Storefront from './pages/Storefront';
import AdminPortal from './pages/AdminPortal';
import BillingModal from './components/Checkout/BillingModal';

function App() {
  const { isAuth, isBillingOpen, setIsBillingOpen } = usePharmacy();
  const [activeTab, setActiveTab] = useState('chat');

  return (
    <div className="relative min-h-screen overflow-hidden">
      
      {/* Main App Container - Blurs out beautifully if Onboarding is active */}
      <div className={`relative z-10 h-screen flex flex-col transition-all duration-1000 ${
        !isAuth ? 'blur-2xl scale-95 opacity-40 pointer-events-none' : 'blur-0 scale-100 opacity-100'
      }`}>
        
        

        {/* The Premium Floating Navbar */}
        <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
        
        {/* The Main Content Area (Cockpit) */}
        <main className="flex-1 w-full flex flex-col overflow-hidden">
          {activeTab === 'chat' && <UserChat />}
          {activeTab === 'store' && <Storefront />}
          {activeTab === 'admin' && <AdminPortal />}
        </main>
      </div>

      {/* Full Screen Onboarding Gate Overlay */}
      {!isAuth && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-white/10 backdrop-blur-md">
          <Onboarding />
        </div>
      )}

      {/* Global Checkout & Billing Modal */}
      <BillingModal isOpen={isBillingOpen} onClose={() => setIsBillingOpen(false)} />
    </div>
  );
}

export default App;