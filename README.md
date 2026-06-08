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

## Production build
```bash
npm run build        # outputs static files to dist/
```
You can serve `dist/` from any static host, or have Flask serve it.
