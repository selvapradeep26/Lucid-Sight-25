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
import time
from pathlib import Path
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(BACKEND_DIR.parent / ".env")

app = Flask(__name__)
CORS(app, origins=["https://lucidsight.netlify.app"], supports_credentials=True)
detection_active = False
detection_thread = None
state_lock = threading.Lock()
ALERT_COOLDOWN_SECONDS = max(
    1,
    int(os.getenv('ALERT_COOLDOWN_SECONDS', '20')),
)
DETECTION_RESET_SECONDS = 2

logging.basicConfig(level=logging.INFO)

# Function to check if the environment is headless (no display)
def is_headless():
    return 'DISPLAY' not in os.environ


def should_show_camera_preview():
    """Only open an OpenCV preview when it was explicitly requested."""
    return os.getenv('SHOW_CAMERA_PREVIEW', 'false').strip().lower() in {
        '1', 'true', 'yes', 'on'
    }


def open_camera():
    """Open the configured webcam with a backend supported by this OS."""
    try:
        camera_index = int(os.getenv('CAMERA_INDEX', '0'))
    except ValueError:
        logging.warning("Invalid CAMERA_INDEX; using camera 0")
        camera_index = 0

    # DirectShow is Windows-only.  V4L2 is the native Linux camera backend.
    backend = cv2.CAP_DSHOW if os.name == 'nt' else cv2.CAP_V4L2
    cap = cv2.VideoCapture(camera_index, backend)
    if not cap.isOpened() and backend != cv2.CAP_ANY:
        cap.release()
        cap = cv2.VideoCapture(camera_index, cv2.CAP_ANY)

    return cap, camera_index

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

    cap, camera_index = open_camera()
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    if not cap.isOpened():
        logging.error(
            "Unable to access camera %s. On Linux, check /dev/video%s access "
            "and try CAMERA_INDEX=1 if your webcam is on that device.",
            camera_index,
            camera_index,
        )
        with state_lock:
            detection_active = False
        return

    last_alert_at = 0.0
    last_human_seen_at = 0.0
    human_present = False
    show_camera_preview = should_show_camera_preview()

    try:
        while detection_active:
            ret, frame = cap.read()
            if not ret:
                logging.error("Unable to read a frame from the camera")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
            now = time.monotonic()

            if len(faces) > 0:
                should_alert = (
                    not human_present
                    or now - last_alert_at >= ALERT_COOLDOWN_SECONDS
                )
                human_present = True
                last_human_seen_at = now

                if should_alert:
                    logging.info("Human detected!")

                    image_path = BACKEND_DIR / "static" / "intruder.jpg"
                    cv2.imwrite(str(image_path), frame)

                    location = get_location()
                    logging.info("Detection location: %s", location)

                    if method == 'Email':
                        if send_alert_via_email(contact, location, image_path):
                            logging.info("Email alert sent successfully.")
                        else:
                            logging.error("Email alert could not be sent.")
                    elif method == 'Telegram':
                        if send_alert_via_telegram(contact, location, image_path):
                            logging.info("Telegram alert sent successfully.")
                        else:
                            logging.error("Telegram alert could not be sent.")
                    else:
                        logging.error("Unsupported alert method: %s", method)

                    last_alert_at = time.monotonic()
            elif human_present and now - last_human_seen_at >= DETECTION_RESET_SECONDS:
                human_present = False
                logging.info("Detection reset; ready for the next human.")

            # Many server OpenCV builds omit GUI support. Preview is opt-in so
            # a missing HighGUI backend can never stop the detection worker.
            if show_camera_preview:
                try:
                    cv2.imshow('LucidSight - Human Detection', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                except cv2.error:
                    logging.warning(
                        "Camera preview is unavailable; continuing detection without it."
                    )
                    show_camera_preview = False
    except Exception:
        logging.exception("Detection worker failed")
    finally:
        cap.release()
        if show_camera_preview:
            try:
                cv2.destroyAllWindows()
            except cv2.error:
                pass
        with state_lock:
            detection_active = False

def send_alert_via_email(contact, location, image_path):
    message = f"🚨 Alert: Human detected at {location} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    sender = os.getenv('EMAIL_FROM', 'sightlucid@gmail.com').strip()

    msg = MIMEMultipart()
    msg['Subject'] = 'LucidSight: Intruder Alert'
    msg['From'] = sender
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
    password = ''.join(password.split())

    try:
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=30) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(msg['From'], msg['To'], msg.as_string())
        logging.info(f"Email alert sent to {contact}")
        return True
    except smtplib.SMTPAuthenticationError:
        logging.error(
            "Gmail authentication failed. EMAIL_FROM must match the Google "
            "account that created EMAILPWD, and EMAILPWD must be an App Password."
        )
        return False
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False

def send_alert_via_telegram(chat_id, location, image_path):
    token = os.getenv('TELEGRAM_BOT_TOKEN')

    if not token:
        logging.error("TELEGRAM_BOT_TOKEN environment variable is not set.")
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
    global detection_active, detection_thread
    method = request.form.get('method', '').strip()
    contact = request.form.get('contact', '').strip()

    if method not in {'Email', 'Telegram'}:
        return jsonify({"error": "Select a supported alert method"}), 400
    if not contact:
        contact_name = "Email address" if method == 'Email' else "Telegram chat ID"
        return jsonify({"error": f"{contact_name} is required"}), 400
    if method == 'Telegram':
        normalized_chat_id = contact.removeprefix('-')
        if not normalized_chat_id.isdigit():
            return jsonify({"error": "Enter a valid numeric Telegram chat ID"}), 400

    with state_lock:
        if detection_active:
            return jsonify({"error": "Detection is already active"}), 409
        if detection_thread is not None and detection_thread.is_alive():
            return jsonify({
                "error": "Previous detection is still stopping. Please wait a moment and try again."
            }), 409
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
