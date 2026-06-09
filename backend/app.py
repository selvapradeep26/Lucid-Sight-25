from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import threading
import cv2
import requests
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(BACKEND_DIR.parent / ".env")

app = Flask(__name__)
CORS(app, origins=["https://lucidsight.netlify.app"], supports_credentials=True)
detection_active = False
state_lock = threading.Lock()

logging.basicConfig(level=logging.INFO)

# Function to check if the environment is headless (no display)
def is_headless():
    return 'DISPLAY' not in os.environ

def get_location():
    try:
        response = requests.get("https://ipinfo.io/json", timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("city") or data.get("region") or data.get("country") or "Unknown"
    except (requests.RequestException, ValueError) as exc:
        logging.warning("Unable to determine location: %s", exc)
        return "Unknown"

@app.route('/api/endpoint', methods=["OPTIONS"])
def handle_options():
    response = jsonify({'message': 'CORS preflight passed'})
    response.headers.add('Access-Control-Allow-Origin', 'https://lucidsight.netlify.app')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response

def detect_human(method, contact):
    global detection_active

    # Use default webcam (0 or cv2.CAP_DSHOW) for webcam input
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    if not cap.isOpened():
        logging.error("Unable to access camera")
        with state_lock:
            detection_active = False
        return

    try:
        while detection_active:
            ret, frame = cap.read()
            if not ret:
                logging.error("Unable to read a frame from the camera")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))

            if len(faces) > 0:
                logging.info("Human detected!")

                image_path = BACKEND_DIR / "static" / "intruder.jpg"
                cv2.imwrite(str(image_path), frame)

                location = get_location()
                logging.info("Detection location: %s", location)

                if method == 'Email':
                    if send_alert_via_email(contact, location, image_path):
                        logging.info("Alert sent successfully.")
                    else:
                        logging.error("Alert could not be sent.")
                elif method == 'Telegram':
                    if send_alert_via_telegram(location, image_path):
                        logging.info("Telegram alert sent successfully.")
                    else:
                        logging.error("Telegram alert could not be sent.")
                else:
                    logging.error("Unsupported alert method: %s", method)
                break

            # Only show the camera feed if not in a headless environment
            if not is_headless():
                cv2.imshow('LucidSight - Human Detection', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    except Exception:
        logging.exception("Detection worker failed")
    finally:
        cap.release()
        if not is_headless():
            cv2.destroyAllWindows()
        with state_lock:
            detection_active = False

def send_alert_via_email(contact, location, image_path):
    message = f"🚨 Alert: Human detected at {location} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    msg = MIMEMultipart()
    msg['Subject'] = 'LucidSight: Intruder Alert'
    msg['From'] = 'sightlucid@gmail.com'
    msg['To'] = contact

    msg.attach(MIMEText(message))

    with open(image_path, 'rb') as img_file:
        img = MIMEImage(img_file.read())
        img.add_header('Content-Disposition', 'attachment', filename="intruder.jpg")
        msg.attach(img)

    password = os.getenv('EMAILPWD')
    if not password:
        logging.error("EMAILPWD environment variable is not set.")
        return False

    try:
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=30) as server:
            server.starttls()
            server.login('sightlucid@gmail.com', password)
            server.sendmail(msg['From'], msg['To'], msg.as_string())
        logging.info(f"Email alert sent to {contact}")
        return True
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False

def send_alert_via_telegram(location, image_path):
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not token or not chat_id:
        logging.error(
            "TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables must be set."
        )
        return False

    caption = (
        "LucidSight: Human detected\n"
        f"Location: {location}\n"
        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    try:
        with open(image_path, 'rb') as image:
            response = requests.post(
                f"https://api.telegram.org/bot{token}/sendPhoto",
                data={"chat_id": chat_id, "caption": caption},
                files={"photo": ("intruder.jpg", image, "image/jpeg")},
                timeout=15,
            )
        try:
            result = response.json()
        except ValueError:
            result = {}

        if not response.ok or not result.get("ok"):
            description = result.get("description", "Unknown Telegram API error")
            logging.error(
                "Telegram rejected the alert (%s): %s",
                response.status_code,
                description,
            )
            return False
        return True
    except OSError as exc:
        logging.error("Unable to read the detection image: %s", exc)
        return False
    except requests.RequestException as exc:
        logging.error(
            "Telegram request failed: %s",
            exc.__class__.__name__,
        )
        return False

# ---------- Flask Routes ----------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start_detection', methods=['POST'])
def start_detection():
    global detection_active
    method = request.form.get('method', '').strip()
    contact = request.form.get('contact', '').strip()

    if method not in {'Email', 'Telegram'}:
        return jsonify({"error": "Select a supported alert method"}), 400
    if method == 'Email' and not contact:
        return jsonify({"error": "Email address is required"}), 400

    with state_lock:
        if detection_active:
            return jsonify({"error": "Detection is already active"}), 409
        detection_active = True

    detection_thread = threading.Thread(
        target=detect_human,
        args=(method, contact),
        daemon=True,
    )
    detection_thread.start()

    return jsonify({"status": "Detection Started"})

@app.route('/stop_detection', methods=['POST'])
def stop_detection():
    global detection_active
    with state_lock:
        detection_active = False
    return jsonify({"status": "Detection Stopped"})

if __name__ == '__main__':
    app.run(debug=True)
