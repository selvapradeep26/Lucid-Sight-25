# SightLucid — React + Flask

SightLucid uses a **React (Vite) frontend** with a **Flask backend** for real-time YOLOv8 object detection.

## Project Structure

```text
sightlucid/
├── backend/
│   ├── app.py
│   ├── detection.py
│   └── requirements.txt
├── src/
│   ├── components/
│   ├── App.jsx
│   ├── main.jsx
│   └── styles.css
├── index.html
├── vite.config.js
└── package.json
```

## Architecture

The browser handles camera access and captures video frames. React sends frames to Flask for YOLOv8 processing, and the detection results are returned to React.

```text
Browser Camera
      ↓
    React
      ↓
 POST /process_frame
      ↓
    Flask
      ↓
   YOLOv8
      ↓
 Detection Results
      ↓
    React UI
```

The backend no longer directly accesses the camera or depends on `/dev/video0`.

## Run

### 1. Start Flask

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Backend:

```text
http://localhost:5000
```

### 2. Start React

```bash
npm install
npm run dev
```

Frontend:

```text
http://localhost:3000
```

Vite proxies API requests to the Flask backend.

## Telegram Bot

Configure the backend `.env`:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
```

Keep the token on the backend. Users provide their own Telegram chat ID through the detection form.

## Gmail Alerts

Configure:

```env
EMAIL_FROM=sightlucid@gmail.com
EMAILPWD=xxxx xxxx xxxx xxxx
```

Use a Google App Password. Never collect recipients' Gmail passwords.

## Production Build

```bash
npm run build
```

The production frontend is generated in:

```text
dist/
```

### Key Change

**Old:** Flask accessed the camera directly.

**New:** React/browser captures frames → Flask processes them → React displays the results.
