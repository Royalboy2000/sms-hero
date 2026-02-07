# SMSKenya - Premium SMS Verification Service

## 🚀 Overview
SMSKenya is Kenya's leading premium virtual number service, providing instant SMS verification for over 500+ services including WhatsApp, Telegram, TikTok, and PayPal. We bridge the gap for Kenyan professionals needing international presence by offering real non-VoIP numbers from Tier-1 carriers globally.

## ✨ Key Features
- **Dynamic Hero Section:** Engaging typewriter animation showcasing global support for US, Canada, UAE, Saudi, and UK numbers.
- **Global Coverage:** Access virtual numbers from 180+ countries with guaranteed delivery rates.
- **Service Integration:** Works seamlessly with WhatsApp, Telegram, PayPal, Google, Airbnb, and more.
- **M-PESA Integration:** Secure and instant local payment processing.
- **WhatsApp Concierge:** Automated and human support via a dedicated WhatsApp concierge service.
- **Privacy & Security:** Privacy-first approach with no long-term data storage of verification codes.
- **Smart Refund System:** Automatic refunds for failed verification attempts ensure customer satisfaction.
- **Currency Support:** Dynamic switching between KES and USD.

## 🛠️ Tech Stack
- **Framework:** [React 18](https://reactjs.org/)
- **Build Tool:** [Vite](https://vitejs.dev/)
- **Language:** [TypeScript](https://www.typescriptlang.org/)
- **Styling:** [Tailwind CSS](https://tailwindcss.com/)
- **Icons:** [Lucide React](https://lucide.dev/)
- **SEO:** [React Helmet Async](https://github.com/staylor/react-helmet-async)

## 📦 Installation & Setup

### Prerequisites
- **Node.js:** version 18.0 or higher
- **npm:** usually comes with Node.js

### 1. Installation
Clone the repository and install dependencies:
```bash
npm install
```

### 2. Configuration
Create a `.env.local` file in the root directory and add your API keys:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Development Mode
Start the development server with hot-module replacement:
```bash
npm run dev
```
By default, the app will be accessible at `http://localhost:5173`.

### 4. Production Build
Generate an optimized production build:
```bash
npm run build
```
The compiled files will be located in the `dist/` directory.

### 5. Production Serving
You can serve the production build using the included Python server, which handles Single Page Application (SPA) routing:
```bash
python3 server.py 8000
```

## 🔍 Debugging & Tuning

### Debugging Common Issues
- **Port Conflicts:** If the default port is taken, run dev with a specific port: `npm run dev -- --port 3000`.
- **Hydration Issues:** Ensure `react-helmet-async` is properly wrapped around the app root.
- **MIME Type Errors:** If serving via a custom server, ensure `.tsx` and `.ts` files are served with `application/javascript` (handled automatically in `server.py`).

### Tuning the Application
- **Animation Speed:** Adjust the `delay` and `pause` props in the `Typewriter` component within `components/LandingPage.tsx` to change the typing speed.
- **Pricing & Services:** Edit `constants.tsx` to update service pricing, add new countries, or change icons.
- **Theme Colors:** Modify `tailwind.config.js` to update the brand's primary emerald color scheme.

## 📁 Repository Structure
- `components/`: Modular React components for the landing page and dashboard.
- `context/`: Global state management for currency and user preferences.
- `services/`: Backend service integrations (e.g., Gemini AI).
- `verification/`: Automated Playwright scripts for UI/UX verification.
- `constants.tsx`: Centralized configuration for the entire application.
- `server.py`: A robust Python-based SPA server for production deployments.

---
*Built for the Kenyan Digital Economy • Based in Mombasa*
