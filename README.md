# SMSKenya - Premium SMS Verification Service

SMSKenya is a robust platform for generating private international phone numbers for SMS verification. Primarily serving Kenyan professionals, it offers real SIM card numbers from 180+ countries to verify services like WhatsApp, Telegram, TikTok, PayPal, and more.

## Key Features

- **Smart HeroSMS V2 Integration:** Utilizes the latest JSON-based provider API with incremental price tiers to ensure the cheapest available numbers are always purchased first.
- **Admin-Managed Whitelists:** Precise control over which services and countries are available to individual users, toggleable globally.
- **Enhanced Telegram Admin Bot:**
    - **User Management:** View quotas, set/add allowed generation limits, and manage paginated whitelists.
    - **Order Management:** View, cancel, or regenerate numbers for any user directly from Telegram.
    - **Mapping Exploration:** List all service and country mappings with regional flags.
    - **HeroSMS Tools:** Check real-time balance and query provider prices via a button-driven 3-step interface (zero typing required).
- **Improved User Dashboard:** Real-time activation tracking with manual 'Cancel' (waiting orders) and 'Try Again' (cancelled/failed orders) functionality.
- **Bilingual Auth Experience:** Clearer Login/Register flow with Swahili/English labels and password persistence tips for non-technical users.
- **Direct Purchase Flow:** Secure, token-based verification links for guest users, requiring no account creation.
- **Dual Currency Support:** Automatic detection and formatting for KES (M-PESA ready) and USD.
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
    *Note: The server will interactively prompt for required environment variables (`SECRET_KEY`, `HERO_SMS_API_KEY`, etc.) on first run if they are not already in your `.env` file.*

## Admin Bot Commands

The Telegram bot (`TELEGRAM_BOT_TOKEN`) provides an interactive interface for admins (`ADMIN_TELEGRAM_ID`).

- **Manage Users:** View current quotas, set new allowed generation limits, and manage whitelists.
- **Manage Tokens:** Generate secure tracking tokens for guest "Direct Purchase" links.
- **HeroSMS Tools:** Check your real-time provider balance and query current provider prices for specific service/country pairs.

## Tech Stack

- **Frontend:** React, Vite, Tailwind CSS, Lucide Icons, React Helmet Async.
- **Backend:** Flask, Flask-CORS, PyJWT, Telebot (pyTelegramBotAPI).
- **Database:** SQLite (Relational mappings for provider IDs, users, and whitelists).
