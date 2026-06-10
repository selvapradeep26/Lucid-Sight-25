# SightLucid (React Edition)

Traditional React (Vite) frontend converted from the original Flask + Jinja
template. Functionality is preserved: the React app talks to the same Flask
backend endpoints (`/start_detection`, `/stop_detection`).

## Project Structure

```
sightlucid/
├── backend/           # Original Flask app (unchanged)
│   ├── app.py
│   ├── detection.py
│   └── requirements.txt
├── src/
│   ├── components/    # React components (Navbar, Hero, Detection, ...)
│   ├── App.jsx
│   ├── main.jsx
│   └── styles.css
├── index.html
├── vite.config.js
└── package.json
```

## Run

### 1) Start the Flask backend
```bash
cd backend
pip install -r requirements.txt
python app.py        # http://localhost:5000
```

### 2) Start the React dev server
```bash
npm install
npm run dev          # http://localhost:3000
```

Vite is configured to proxy `/start_detection` and `/stop_detection` to the
Flask backend on port 5000, so the React UI behaves identically to the
original template.

## Telegram bot access

Set `TELEGRAM_BOT_TOKEN` in the project `.env` file. Do not expose this token
in the React app. Each user must open the bot, tap **Start**, and enter their
own numeric Telegram chat ID in the detection form. The backend uses that chat
ID only for the current detection session.

## Gmail alerts

Create a Google App Password for the Gmail account used to send alerts, then
configure the project `.env` file:

```env
EMAIL_FROM=sightlucid@gmail.com
EMAILPWD=xxxx xxxx xxxx xxxx
```

`EMAIL_FROM` must be the same Google account that created the App Password.
Recipients enter their own email address in the detection form. Never use or
collect a recipient's Gmail password.

## Production build
```bash
npm run build        # outputs static files to dist/
```
You can serve `dist/` from any static host, or have Flask serve it.
