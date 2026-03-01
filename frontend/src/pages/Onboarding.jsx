import React, { useState } from "react";
import { usePharmacy } from "../context/PharmacyContext";
import { Stethoscope, LogIn, UserPlus } from "lucide-react";
import axios from "axios";

export default function Onboarding() {
  const { handleLogin } = usePharmacy();
  const [isLoginMode, setIsLoginMode] = useState(true);

  // Form states
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    age: "",
    email: "",
    password: "",
  });

  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  const glassBase = "backdrop-blur-[40px] saturate-[200%] bg-white/40 border border-white/60 shadow-[0_24px_48px_-12px_rgba(0,0,0,0.1)]";

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setErrorMsg(null);
  };

  const handleAuthSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg(null);
    setLoading(true);

    try {
      if (isLoginMode) {
        if (!formData.email || !formData.password) {
          setErrorMsg("Please fill in both email and password.");
          setLoading(false);
          return;
        }

        const res = await axios.post("http://localhost:8000/auth/login", {
          email: formData.email,
          password: formData.password,
        });

        if (res.data.status === "success") {
          handleLogin(res.data.patient);
        }
      } else {
        if (!formData.firstName || !formData.lastName || !formData.email || !formData.password) {
          setErrorMsg("Please fill out all required fields.");
          setLoading(false);
          return;
        }
        if (!acceptedTerms) {
          setErrorMsg("You must accept the terms and medical constraints.");
          setLoading(false);
          return;
        }

        const res = await axios.post("http://localhost:8000/auth/register", {
          name: `${formData.firstName} ${formData.lastName}`,
          email: formData.email,
          password: formData.password,
        });

        if (res.data.status === "success") {
          handleLogin(res.data.patient);
        }
      }
    } catch (error) {
      console.error("Auth Error:", error);
      setErrorMsg(error.response?.data?.detail || "Authentication Failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      {/* Background gradients */}
      <div className="absolute top-0 right-0 w-1/3 h-screen bg-gradient-to-l from-blue-100/50 to-transparent pointer-events-none" />
      <div className="absolute top-0 left-0 w-full h-1/2 bg-gradient-to-b from-blue-50 to-transparent pointer-events-none" />

      <div className={`w-full max-w-xl ${glassBase} rounded-[2rem] p-8 md:p-12 relative z-10 animate-fade-in-up`}>

        {/* Header */}
        <div className="text-center mb-10">
          <div className="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-blue-500/30">
            <Stethoscope className="text-white" size={32} />
          </div>
          <h1 className="text-3xl font-bold text-slate-800 mb-2">Welcome to SecureHealth</h1>
          <p className="text-slate-500">
            Intelligent Agentic Pharmacy System
          </p>
        </div>

        {/* Toggle Login/Signup */}
        <div className="flex bg-white/20 backdrop-blur-md rounded-2xl p-1.5 mb-8 border border-white/40 shadow-inner">
          <button
            type="button"
            onClick={() => setIsLoginMode(true)}
            className={`flex-1 py-2.5 text-sm font-bold rounded-xl transition-all ${isLoginMode ? 'bg-white/80 text-blue-600 shadow-[0_4px_12px_rgba(0,0,0,0.05)]' : 'text-slate-500 hover:text-slate-700 hover:bg-white/40'}`}
          >
            Login
          </button>
          <button
            type="button"
            onClick={() => setIsLoginMode(false)}
            className={`flex-1 py-2.5 text-sm font-bold rounded-xl transition-all ${!isLoginMode ? 'bg-white/80 text-blue-600 shadow-[0_4px_12px_rgba(0,0,0,0.05)]' : 'text-slate-500 hover:text-slate-700 hover:bg-white/40'}`}
          >
            Sign Up
          </button>
        </div>

        <form onSubmit={handleAuthSubmit} className="space-y-6">

          {!isLoginMode && (
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">First Name</label>
                <input
                  type="text"
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleChange}
                  className="w-full bg-white/40 backdrop-blur-md border border-white/60 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:bg-white/60 transition-all font-medium text-slate-800 placeholder-slate-400 shadow-[inset_0_2px_4px_rgba(0,0,0,0.02)]"
                  placeholder="John"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Last Name</label>
                <input
                  type="text"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleChange}
                  className="w-full bg-white/40 backdrop-blur-md border border-white/60 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:bg-white/60 transition-all font-medium text-slate-800 placeholder-slate-400 shadow-[inset_0_2px_4px_rgba(0,0,0,0.02)]"
                  placeholder="Doe"
                />
              </div>
              <div className="space-y-2 col-span-2">
                <label className="text-sm font-medium text-slate-700">Age (Optional for Sign up)</label>
                <input
                  type="number"
                  name="age"
                  value={formData.age}
                  onChange={handleChange}
                  className="w-full bg-white/40 backdrop-blur-md border border-white/60 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:bg-white/60 transition-all font-medium text-slate-800 placeholder-slate-400 shadow-[inset_0_2px_4px_rgba(0,0,0,0.02)]"
                  placeholder="30"
                />
              </div>
            </div>
          )}

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700">Email Address</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full bg-white/40 backdrop-blur-md border border-white/60 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:bg-white/60 transition-all font-medium text-slate-800 placeholder-slate-400 shadow-[inset_0_2px_4px_rgba(0,0,0,0.02)]"
              placeholder="john@example.com"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700">Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="w-full bg-white/40 backdrop-blur-md border border-white/60 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:bg-white/60 transition-all font-medium text-slate-800 placeholder-slate-400 shadow-[inset_0_2px_4px_rgba(0,0,0,0.02)]"
              placeholder="••••••••"
            />
          </div>

          {!isLoginMode && (
            <div className="flex items-start gap-3 p-4 bg-white/30 backdrop-blur-sm rounded-xl border border-white/60 shadow-sm">
              <input
                type="checkbox"
                id="terms"
                checked={acceptedTerms}
                onChange={(e) => setAcceptedTerms(e.target.checked)}
                className="mt-1 w-4 h-4 text-blue-600 rounded border-white/60 border-2 focus:ring-blue-500/50 bg-white/50"
              />
              <label htmlFor="terms" className="text-sm text-slate-600 leading-relaxed font-medium">
                I agree to the <span className="font-bold text-slate-800">Medical Safety Constraints</span> and acknowledge that this system enforces strict dosage limits and prescription requirements.
              </label>
            </div>
          )}

          {errorMsg && (
            <div className="p-4 bg-red-50 text-red-600 border border-red-100 rounded-xl text-sm font-medium">
              {errorMsg}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 rounded-xl transition-all shadow-lg shadow-blue-600/30 active:scale-[0.98] disabled:opacity-70 flex items-center justify-center gap-2"
          >
            {loading ? "Processing..." : isLoginMode ? (
              <><LogIn size={20} /> Login Securely</>
            ) : (
              <><UserPlus size={20} /> Create Account</>
            )}
          </button>
        </form>

      </div>
    </div >
  );
}