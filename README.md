# SMSKenya - Premium SMS Verification Service

SMSKenya is a robust platform for generating private international phone numbers for SMS verification. Primarily serving Kenyan professionals, it offers real SIM card numbers from 180+ countries to verify services like WhatsApp, Telegram, TikTok, PayPal, and more.

## Key Features

- **Smart HeroSMS V2 Integration:** Utilizes the latest JSON-based provider API with an **Incremental Price Escalator** ($0.50 → $15.00) to ensure the cheapest available numbers are always prioritized, saving costs on every order.
- **Admin-Managed Whitelists:** Precise control over which services (e.g., WhatsApp, Telegram) and countries are available to individual users, toggleable globally via a master switch.
- **Enhanced Telegram Admin Bot (v3):**
    - **Intelligent Quota Management:** View real-time usage, set absolute limits, or incrementally add to existing quotas with one-click buttons.
    - **Remote Order Control:** Full visibility into user order streams with the ability to **Cancel & Refund** or **Regenerate** numbers remotely.
    - **Automated Mapping Discovery:** Instant access to internal provider IDs for 180+ countries and dozens of services, complete with regional emoji flags.
    - **Zero-Typing HeroSMS Tools:** Check real-time API balance and query live provider pricing/stock via an interactive 3-step button menu.
- **Premium User Dashboard:**
    - **Live Polling:** Automatic 10-second status updates for activation codes and remaining quotas.
    - **Smart Cancellation Guard:** Implements a mandatory 120-second wait period for new numbers to maximize code arrival probability, featuring a live countdown timer.
    - **One-Click Retries:** Failed or cancelled orders can be retried instantly with the same configuration.
- **Bilingual Auth Experience:** Optimized for the Kenyan market with a Swahili/English dual-language interface, tabbed navigation, and password persistence reminders.
- **Direct Purchase Flow:** Secure, single-use token system allowing admins to generate temporary access links for guest users, bypassing account creation.
- **Dual Currency & Geolocation:** Automatic detection and formatting for KES and USD based on user IP, with cached preferences to minimize network overhead.
- **Privacy-First Design:** No personal data or verification codes are stored long-term.
- **Based in Germany:** Modern infrastructure with dedicated human support via WhatsApp.

## Local Development

### Frontend (React + Vite)

1.  **Install dependencies:**
    ```bash
    npm install
    ```
2.  **Build production assets:**
    ```bash
    npm run build
    ```
3.  **Run dev server:**
    ```bash
    npm run dev
    ```

### Backend (Python + Flask)

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run the server:**
    ```bash
    python server.py [port]
    ```
    *Note: The server includes an interactive setup wizard that will prompt for required environment variables (`SECRET_KEY`, `HERO_SMS_API_KEY`, `TELEGRAM_BOT_TOKEN`, `ADMIN_TELEGRAM_ID`) and the desired port on first launch.*

## Admin Bot Commands

The Telegram bot (`TELEGRAM_BOT_TOKEN`) provides an interactive interface for admins (`ADMIN_TELEGRAM_ID`).

- **Manage Users:** View current quotas, set new allowed generation limits, and manage whitelists.
- **Manage Tokens:** Generate secure tracking tokens for guest "Direct Purchase" links.
- **HeroSMS Tools:** Check your real-time provider balance and query current provider prices for specific service/country pairs.

## Tech Stack

- **Frontend:** React, Vite, Tailwind CSS, Lucide Icons, React Helmet Async.
- **Backend:** Flask, Flask-CORS, PyJWT, Telebot (pyTelegramBotAPI).
- **Database:** SQLite (Relational mappings for provider IDs, users, and whitelists).
