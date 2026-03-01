# 🏥 Agentic AI Pharmacy System

An AI-powered multi-agent pharmacy management system that ensures safe medicine ordering, prescription validation, stock management, refill alerts, and intelligent voice interaction.

## 🚀 Project Overview

This project is an AI-driven pharmacy platform built using a multi-agent architecture. 

**It allows users to:**
* Browse medicines
* Upload prescriptions
* Consult AI for medicine queries
* Get refill alerts
* Use voice input (Hinglish supported)
* Place safe and validated medicine orders

**It allows admins to:**
* Monitor inventory
* Track stock levels
* View refill warnings
* Analyze agent execution history
* Monitor safety completion score
* Refill stock

---

## 🧠 AI & Agentic Architecture

We use a Multi-Agent System powered by LLMs. Instead of one big AI doing everything, we divide responsibilities to make the system safer, faster, more modular, easy to debug, and transparent in its reasoning.

### 🔹 Agents Used

| Agent | Role / Intent |
| :--- | :--- |
| **Intent Agent** | Detects user intention (Buy, Consult, Refill, Upload prescription, etc.) |
| **Orchestrator Agent** | Decides which agent should handle the request |
| **Safety Agent** | Checks prescription requirements & overdose risks |
| **Stock Agent** | Checks availability & stock levels |
| **Refill Agent** | Monitors medicine refill schedules |
| **Database Agent** | Reads/Writes data securely in database |
| **Action Agent** | Executes final operations (place order, update stock, notify admin) |

---

## 📊 Role of Langfuse

Langfuse is utilized for observability of AI workflows. It helps judges and admins see exactly *“Which agent did what and why?”* **Langfuse is used for:**
* Agent thinking visualization
* Tracking execution history
* Monitoring safety scores
* Debugging agent decisions

---

## 🤖 AI Stack

* **Groq API (Llama 3.3 - 70B Versatile):** Main brain of the system. Provides ultra-fast inference with no quota issues like OpenAI.
* **LangChain:** Connects multiple agents, manages orchestration logic, and implements the Supervisor pattern.
* **Whisper (via Groq):** Converts voice to text, handles fuzzy/mumbling speech, and supports Hinglish input.

---

## ⚙️ Backend Stack

* **FastAPI:** High-performance backend framework that handles API routes and integrates easily with the frontend.
* **Uvicorn:** Extremely fast ASGI server that runs FastAPI.
* **SQLAlchemy:** ORM (Object Relational Mapper) that securely connects Python code to the database and manages records.
* **SQLite:** Lightweight database that stores medicines, users, orders, stock levels, and prescription flags.
* **Python Audio Libraries (`sounddevice`, `numpy`, `scipy`):** Used for capturing microphone input and processing audio for Whisper.
* **Python-dotenv:** Stores API keys securely to prevent key leaks on GitHub.

---

## 🎨 Frontend Stack

* **React (v19):** Builds robust UI components.
* **Vite:** Very fast development server and build tool.
* **Tailwind CSS:** Modern styling framework for clean UI design.
* **Axios:** Sends HTTP requests to the backend.
* **React Router DOM:** Handles navigation between pages.
* **Lucide React:** Provides beautiful icons for the UI.
* **ESLint:** Maintains code quality.

---

## 📦 Core Features

### 👤 User Features
* Secure Login & Registration
* Browse Store
* Upload Prescription
* AI Consultation
* Refill Alerts & SMS notifications
* Quantity (+/-) selection with overdose warnings
* Voice input (Hinglish)

### 🛠 Admin Features
* Inventory dashboard
* Stock monitoring & low stock alerts
* Refill warning of users
* Agent safety completion score & execution history
* Stock refill management

---

## 🧾 Safe Ordering Workflow

When a user selects multiple medicines, the system automatically runs the following workflow:
1. **Checks Prescription Requirement:** If required, the user must upload a valid prescription.
2. **Checks Safe Dosage:** Issues an overdose warning if high quantities are requested.
3. **Checks Stock Availability:** Ensures the pharmacy can fulfill the order.
4. **Execution:** If all checks pass, the order is placed, stock is updated, and a notification is sent.
5. **Billing:** Generates a bill including dosage instructions and the next refill date.

---

## 🗂 Database Structure

**Database:** `pharmacy.db`
SQLAlchemy securely manages all database operations for the following tables:
* Users
* Orders
* Medicines
* Prescription flags
* Stock levels
* Refill history

---

## 🎤 Voice Integration

* One-to-one AI voice chat
* Voice → Text conversion
* Hinglish language support
* Noisy environment tolerance

---

## 🔐 Security Features

* OTP phone verification
* Prescription validation
* Overdose alerts
* Secure API key storage
* Admin safety monitoring

---

## 🏗 Installation

```bash
# Clone repo
git clone <your-repo-url>

# Backend setup
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend setup
cd frontend
npm install
npm run dev
