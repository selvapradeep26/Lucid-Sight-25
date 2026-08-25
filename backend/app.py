from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import threading
import cv2
import requests
from datetime import datetime
import smtplib
import socket
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
detection_method = None
detection_contact = None
last_alert_at = 0.0
last_human_seen_at = 0.0
human_present = False
state_lock = threading.Lock()
ALERT_COOLDOWN_SECONDS = max(
    1,
    int(os.getenv('ALERT_COOLDOWN_SECONDS', '20')),
)
DETECTION_RESET_SECONDS = 2

logging.basicConfig(level=logging.INFO)

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

def process_frame(frame, method, contact):
    global last_alert_at
    global last_human_seen_at
    global human_present

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades +
        "haarcascade_frontalface_default.xml"
    )

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

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

            image_path = (
                BACKEND_DIR /
                "static" /
                "intruder.jpg"
            )

            cv2.imwrite(
                str(image_path),
                frame
            )

            location = get_location()

            if method == "Email":

                send_alert_via_email(
                    contact,
                    location,
                    image_path
                )

            elif method == "Telegram":

                send_alert_via_telegram(
                    contact,
                    location,
                    image_path
                )

            last_alert_at = now

        return True

    if (
        human_present
        and now - last_human_seen_at >= DETECTION_RESET_SECONDS
    ):
        human_present = False

        logging.info(
            "Detection reset; ready for next human."
        )

    return False

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

    smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com').strip()
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_timeout = int(os.getenv('SMTP_TIMEOUT', '12'))

    try:
        probe = socket.create_connection((smtp_host, smtp_port), smtp_timeout)
        probe.close()
    except OSError as exc:
        logging.error(
            "SMTP is unreachable at %s:%s (%s). Outbound SMTP appears blocked on this network.",
            smtp_host,
            smtp_port,
            exc,
        )
        return False

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
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
    return jsonify({
        "status": "ok",
        "service": "LucidSight Backend"
    })

@app.route('/start_detection', methods=['POST'])
def start_detection():
    global detection_active, detection_method, detection_contact
    global last_alert_at, last_human_seen_at, human_present
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
        detection_active = True
        detection_method = method
        detection_contact = contact
        last_alert_at = 0.0
        last_human_seen_at = 0.0
        human_present = False

    return jsonify({"status": "Detection Started"})

@app.route('/stop_detection', methods=['POST'])
def stop_detection():
    global detection_active, detection_method, detection_contact
    with state_lock:
        detection_active = False
        detection_method = None
        detection_contact = None
    return jsonify({"status": "Detection Stopped"})

@app.route("/process_frame", methods=["POST"])
def process_frame_route():

    with state_lock:

        if not detection_active:
            return jsonify({
                "error": "Detection is not active"
            }), 400

        method = detection_method
        contact = detection_contact

    if "frame" not in request.files:
        return jsonify({
            "error": "No frame received"
        }), 400

    try:

        import numpy as np

        image_bytes = request.files["frame"].read()

        image_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8
        )

        frame = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        if frame is None:
            return jsonify({
                "error": "Invalid image"
            }), 400

        detected = process_frame(
            frame,
            method,
            contact
        )

        return jsonify({
            "detected": detected
        })

    except Exception:

        logging.exception(
            "Frame processing failed"
        )

        return jsonify({
            "error": "Frame processing failed"
        }), 500

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False
    )
