from flask import Flask, render_template, request, redirect, session, send_from_directory, flash
from pypdf import PdfReader
from collections import Counter
from werkzeug.utils import secure_filename
import os
import re
import time
from database.db import get_db
from ai.emotion_detector import detect_emotion
from ai.gemini_chat import get_intent_and_response
import random
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key="emocare_secret"

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD").replace(" ", "")

REPORT_FOLDER = "static/uploads/reports"
PROFILE_FOLDER = "static/uploads/profiles"

app.config["REPORT_FOLDER"] = REPORT_FOLDER
app.config["PROFILE_FOLDER"] = PROFILE_FOLDER

for folder in [REPORT_FOLDER, PROFILE_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

def allowed_file(filename):

    return "." in filename and \
           filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS

def is_strong_password(password):

    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&^#])[A-Za-z\d@$!%*?&^#]{8,}$'

    return re.match(pattern, password)

def send_otp(email, otp):

    subject = "EmoCare Password Reset OTP"

    body = f"""
Hello,

Your OTP for resetting your EmoCare password is:

{otp}

This OTP will expire in 5 minutes.

If you didn't request this password reset,
please ignore this email.

Regards,
EmoCare Team
"""

    msg = MIMEText(body)

    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

    server.send_message(msg)

    server.quit()

def generate_local_chat_title(messages):

    if not messages:
        return "New Chat"

    # Combine all user messages
    text = " ".join(
        message.strip()
        for message in messages
        if message and message.strip()
    )

    text_lower = text.lower()

    # Remove common greetings when looking for the topic
    meaningful_messages = [
        message.strip()
        for message in messages
        if message and message.strip().lower() not in [
            "hi",
            "hii",
            "hiii",
            "hello",
            "hey",
            "good morning",
            "good afternoon",
            "good evening"
        ]
    ]

    # -----------------------------
    # EXAMS / RESULTS
    # -----------------------------
    if any(word in text_lower for word in [
        "exam", "exams", "marks", "result", "results", "passed"
    ]):

        if any(word in text_lower for word in [
            "happy", "good", "great", "better", "passed", "excellent"
        ]):
            return "Happy About Exam Results"

        return "Exam & Results"

    # -----------------------------
    # THERAPY / APPOINTMENT
    # -----------------------------
    if any(word in text_lower for word in [
        "therapy", "appointment", "treatment", "doctor"
    ]):

        if any(word in text_lower for word in [
            "stress", "stressed", "nervous", "anxious", "anxiety", "worried"
        ]):
            return "Worried About Treatment"

        return "Therapy & Treatment"

    # -----------------------------
    # LONELINESS
    # -----------------------------
    if any(word in text_lower for word in [
        "lonely", "loneliness"
    ]):

        if any(word in text_lower for word in [
            "activity", "activities", "distract", "exercise"
        ]):
            return "Feeling Lonely & Looking for Activities"

        return "Feeling Lonely"

    # -----------------------------
    # STRESS / ANXIETY
    # -----------------------------
    if any(word in text_lower for word in [
        "stressed", "stress", "anxious", "anxiety", "nervous", "worried"
    ]):

        return "Stress & Anxiety"

    # -----------------------------
    # MUSIC
    # -----------------------------
    if any(word in text_lower for word in [
        "music", "song", "songs"
    ]):

        return "Calming Music Suggestions"

    # -----------------------------
    # ACTIVITIES / EXERCISE
    # -----------------------------
    if any(word in text_lower for word in [
        "activity", "activities", "exercise", "workout"
    ]):

        return "Activities & Exercise"

    # -----------------------------
    # SLEEP
    # -----------------------------
    if any(word in text_lower for word in [
        "sleep", "sleeping", "insomnia"
    ]):

        return "Sleep & Relaxation"

    # -----------------------------
    # SELF CONFIDENCE
    # -----------------------------
    if any(word in text_lower for word in [
        "insecure", "insecurity", "confidence", "self esteem"
    ]):

        return "Self-Confidence & Insecurity"

    # -----------------------------
    # HAPPY / POSITIVE
    # -----------------------------
    if any(word in text_lower for word in [
        "happy", "happiness", "good mood", "feeling good"
    ]):

        return "Happy Moments"

    # -----------------------------
    # FALLBACK
    # -----------------------------
    if meaningful_messages:

        title = meaningful_messages[0]

        if len(title) > 30:
            title = title[:30].rstrip() + "..."

        return title.capitalize()

    return "General Conversation"

def extract_pdf_text(filepath):

    text = ""

    try:

        reader = PdfReader(filepath)

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    except Exception as e:

        print("PDF EXTRACTION ERROR:", e)

    return text

def analyze_medical_report(text):

    # Normalize PDF text
    text = re.sub(r"\s+", " ", text).strip()

    analysis = {
    "diagnosis": "Not detected",
    "stage": "Not detected",
    "tumor_size": "Not detected",
    "treatment": "Not detected",
    "treatment_details": "",
    "molecular_findings": "Not detected",
    "clinical_findings": "Not detected",
    "follow_up": "Not detected",
    "important_symptoms": []
    }

    # --------------------------------
    # 1. Diagnosis
    # --------------------------------

    diagnosis_match = re.search(
        r"Primary diagnosis:\s*(.*?)(?=\s*Stage:)",
        text,
        re.IGNORECASE
    )

    if diagnosis_match:
        analysis["diagnosis"] = diagnosis_match.group(1).strip()

    # --------------------------------
    # 2. Stage
    # --------------------------------

    stage_match = re.search(
        r"Stage:\s*(.*?)(?=\s*Tumor size:)",
        text,
        re.IGNORECASE
    )

    if stage_match:
        analysis["stage"] = stage_match.group(1).strip()

    # --------------------------------
    # 3. Tumor Information
    # --------------------------------

    tumor_match = re.search(
        r"Tumor size:\s*(.*?)(?=\s*Relevant History)",
        text,
        re.IGNORECASE
    )

    if tumor_match:
        analysis["tumor_size"] = tumor_match.group(1).strip()

# --------------------------------
# 4. Treatment
# --------------------------------

        treatment_match = re.search(
            r"the patient underwent\s+(.*?)(?=\.\s*Final pathology)",
            text,
            re.IGNORECASE
            )

        if treatment_match:

            treatment = treatment_match.group(1).strip()

            analysis["treatment"] = treatment

        treatment_details_match = re.search(
            r"Final pathology\s+(.*?)(?=\s*Given tumor characteristics)",
            text,
            re.IGNORECASE
            )

        if treatment_details_match:

            analysis["treatment_details"] = (
                treatment_details_match.group(1).strip()
            )

    # --------------------------------
    # 5. Follow-Up Plan
    # --------------------------------

    followup_match = re.search(
        r"Follow-Up Plan\s*(.*?)(?=\s*Summary)",
        text,
        re.IGNORECASE
    )

    if followup_match:

        followup_text = followup_match.group(1).strip()

        analysis["follow_up"] = [
            item.strip()
            for item in re.split(r"•", followup_text)
            if item.strip()
        ]

    # --------------------------------
    # 6. Dynamic Symptom Extraction
    # --------------------------------

    symptom_match = re.search(
        r"symptoms\s+warranting\s+urgent\s+follow-up\s*\((.*?)\)",
        text,
        re.IGNORECASE
    )

    if symptom_match:

        symptom_text = symptom_match.group(1).strip()

        symptoms = re.split(
            r",|\band\b",
            symptom_text,
            flags=re.IGNORECASE
        )

        analysis["important_symptoms"] = [
            symptom.strip()
            for symptom in symptoms
            if symptom.strip()
        ]

# --------------------------------
# 7. Molecular Findings
# --------------------------------

    molecular_match = re.search(
        r"Molecular testing:\s*(.*?)(?=\s*Former smoker|\s*No significant)",
        text,
        re.IGNORECASE
    )

    if molecular_match:

        analysis["molecular_findings"] = (
            molecular_match.group(1)
            .strip()
            .rstrip("• ")
        )

# --------------------------------
# 8. Clinical Findings
# --------------------------------

    clinical_match = re.search(
        r"Final pathology\s+(.*?)(?=\s*Given tumor characteristics)",
        text,
        re.IGNORECASE
    )

    if clinical_match:

        analysis["clinical_findings"] = (
            clinical_match.group(1).strip()
        )

    return analysis

def generate_wellness_insight(analysis, emotion_counts):

    if not emotion_counts:
        return (
            "No recent emotional history is available. "
            "Continue using EmoCare for regular emotional check-ins "
            "and wellness support."
        )

    total = sum(emotion_counts.values())

    dominant_emotion, dominant_count = emotion_counts.most_common(1)[0]

    percentage = round((dominant_count / total) * 100)

    insight = (
        f"Your recent emotional history shows {dominant_emotion} "
        f"as the most frequently recorded emotion ({percentage}% of "
        f"the recent records). "
    )

    if dominant_emotion == "joy":
        insight += (
            "This suggests a generally positive emotional pattern "
            "in your recent check-ins. Continue engaging in activities "
            "that help you maintain this positive state and use EmoCare "
            "regularly to monitor changes in your emotional wellbeing."
        )

    elif dominant_emotion in ["sadness", "fear", "anger", "disgust"]:
        insight += (
            "Some challenging emotions are present in your recent "
            "check-ins. Consider using EmoCare's relaxation, reflection, "
            "or supportive activities when you feel overwhelmed. "
            "If these feelings persist or become difficult to manage, "
            "consider speaking with a qualified healthcare professional."
        )

    else:
        insight += (
            "Continue monitoring your emotional wellbeing through "
            "regular check-ins and use EmoCare's wellness activities "
            "whenever they are helpful."
        )

    return insight

@app.route("/")
def home():
    return render_template("home.html")

def get_notifications(email):

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM notifications
        WHERE user_email=%s
        ORDER BY created_at DESC
    """,(email,))

    notifications = cursor.fetchall()

    cursor.close()

    return notifications

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]
        remember = request.form.get("remember")

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cursor.fetchone()

        if user:

            session.clear()
            session["user_email"] = user["email"]
            session["user_name"] = user["name"]

            return redirect("/dashboard?success=login")

        else:
            return redirect("/login?error=invalid")

    return render_template("login.html")

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():

    if request.method == "POST":

        email = request.form['email']

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user = cursor.fetchone()
        cursor.close()

        if user:

            otp = str(random.randint(100000, 999999))

            session['reset_email'] = email
            session['otp'] = otp
            session['otp_expiry'] = (datetime.now() + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
            session["otp_sent_time"] = time.time()
            send_otp(email, otp)

            flash("OTP sent successfully.")
            return redirect('/verify_otp')

        else:

            flash("Email not found.")

    return render_template("forgot_password.html")

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():

    if 'otp' not in session:
        return redirect('/forgot_password')

    if request.method == "POST":

        entered = request.form['otp']

        expiry = datetime.strptime(
            session['otp_expiry'],
            "%Y-%m-%d %H:%M:%S"
        )

        if datetime.now() > expiry:
            flash("OTP expired.")
            return redirect('/forgot_password')

        if entered == session['otp']:

            session.pop("otp", None)
            session.pop("otp_expiry", None)
            session.pop("otp_sent_time", None)

            return redirect('/reset_password')

        else:
            flash("Invalid OTP")

    # Calculate remaining resend time
    remaining = 0

    if "otp_sent_time" in session:
        elapsed = int(time.time() - session["otp_sent_time"])
        remaining = max(0, 60 - elapsed)

    return render_template(
        "verify_otp.html",
        remaining=remaining
    )

@app.route("/resend_otp")
def resend_otp():

    if "reset_email" not in session:
        return redirect("/forgot_password")

    elapsed = int(time.time() - session["otp_sent_time"])
    remaining = max(0, 60 - elapsed)

    if elapsed < 60:

        flash(f"Please wait {60-elapsed} seconds before requesting another OTP.")

        return redirect("/verify_otp")

    otp = str(random.randint(100000,999999))

    session["otp"] = otp

    session["otp_expiry"] = (datetime.now() + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
    session["otp_sent_time"] = time.time()

    send_otp(session["reset_email"], otp)

    flash("New OTP sent successfully.")

    return redirect("/verify_otp")

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():

    if 'reset_email' not in session:
        return redirect('/forgot_password')

    if request.method == "POST":

        password = request.form['password']
        confirm = request.form['confirm']

        if not is_strong_password(password):
            flash("Password must contain at least 8 characters, one uppercase letter, one lowercase letter, one number and one special character.")
            return redirect('/reset_password')

        if password != confirm:
            flash("Passwords do not match.")
            return redirect('/reset_password')

        email = session['reset_email']

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "UPDATE users SET password=%s WHERE email=%s",
            (password, email)
        )

        db.commit()

        cursor.close()

        # Clear all password reset session data
        session.pop('reset_email', None)
        session.pop('otp', None)
        session.pop('otp_expiry', None)
        session.pop('otp_sent_time', None)

        flash("Password updated successfully!")

        return redirect('/login')

    return render_template("reset_password.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        password=request.form["password"]

        if not is_strong_password(password):
            flash("Password must contain at least 8 characters, one uppercase letter, one lowercase letter, one number and one special character.")

            return redirect("/register")

        gender = request.form["gender"]

        # Check if email already exists
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
         return render_template(
          "register.html",
            error="Email already registered. Please use another email."
    )

        # Insert new user
        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "INSERT INTO users(name,email,password,gender) VALUES(%s,%s,%s,%s)",
            (name, email, password, gender)
        )

        db.commit()

        return redirect("/login?success=registered")

    return render_template("register.html")

@app.route("/dashboard")
def dashboard():

    if "user_email" not in session:
        return redirect("/login")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # ==========================
    # Logged-in User
    # ==========================
    cursor.execute("""
        SELECT *
        FROM users
        WHERE email=%s
    """, (session["user_email"],))

    user = cursor.fetchone()

    if user and user["name"]:
        name_parts = user["name"].split()

        initials = ""

        for part in name_parts:
            initials += part[0].upper()

            user["initials"] = initials

    # ==========================
    # Current Mood
    # ==========================
    cursor.execute("""
        SELECT emotion
        FROM emotion_history
        WHERE user_email=%s
        ORDER BY created_at DESC
        LIMIT 1
    """, (session["user_email"],))

    latest = cursor.fetchone()

    current_mood = latest["emotion"] if latest else "No mood yet"

    # ==========================
    # Weekly Average
    # ==========================
    cursor.execute("""
        SELECT emotion, COUNT(*) AS total
        FROM emotion_history
        WHERE user_email=%s
        AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        GROUP BY emotion
        ORDER BY total DESC
        LIMIT 1
    """, (session["user_email"],))

    weekly = cursor.fetchone()

    weekly_average = weekly["emotion"] if weekly else "No data"

    # ==========================
    # Sessions Today
    # ==========================
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM emotion_history
        WHERE user_email=%s
        AND DATE(created_at)=CURDATE()
    """, (session["user_email"],))

    today_sessions = cursor.fetchone()["total"]

# ==========================
# Mood Graph Data
# ==========================

    cursor.execute("""
        SELECT emotion, COUNT(*) AS total\
        FROM emotion_history
        WHERE user_email=%s
        GROUP BY emotion
    """, (session["user_email"],))

    graph_data = cursor.fetchall()

    emotion_counts = {
        "Happy": 0,
        "Calm": 0,
        "Sad": 0,
        "Angry": 0,
        "Stressed": 0
    }

    emotion_mapping = {
        "joy": "Happy",
        "happiness": "Happy",

        "sadness": "Sad",
        "sad": "Sad",

        "anger": "Angry",
        "angry": "Angry",

        "stress": "Stressed",
        "stressed": "Stressed",

        "calm": "Calm"
    }

    for row in graph_data:

        emotion = row["emotion"].lower().strip()

        if emotion in emotion_mapping:

            dashboard_emotion = emotion_mapping[emotion]

            emotion_counts[dashboard_emotion] += row["total"]

        # ==========================
        # Patient Treatment Information
        # ==========================

        cursor.execute("""
            SELECT
                cancer_type,
                cancer_stage,
                current_treatment
            FROM users
            WHERE email = %s
        """, (session["user_email"],))

        treatment_info = cursor.fetchone()

    # ==========================
    # Recent Activity
    # ==========================

    recent_activities = []


    # Recent Mood Check-ins
    cursor.execute("""
        SELECT emotion, created_at
        FROM emotion_history
        WHERE user_email=%s
        ORDER BY created_at DESC
        LIMIT 3
    """, (session["user_email"],))

    moods = cursor.fetchall()


    for mood in moods:

        recent_activities.append({
            "icon": "😊",
            "text": f"Mood check-in completed - {mood['emotion'].capitalize()} detected",
            "time": mood["created_at"]
        })


    # Recent Reports
    cursor.execute("""
        SELECT report_name, uploaded_at
        FROM medical_reports
        WHERE user_email=%s
        ORDER BY uploaded_at DESC
        LIMIT 2
    """, (session["user_email"],))

    reports_activity = cursor.fetchall()


    for report in reports_activity:

        recent_activities.append({
            "icon": "📄",
            "text": f"Medical report uploaded - {report['report_name']}",
            "time": report["uploaded_at"]
        })


    # Sort activities by latest time
    recent_activities = sorted(
        recent_activities,
        key=lambda x: x["time"],
        reverse=True
    )[:5]

    # ==========================
    # Notifications
    # ==========================
    cursor.execute("""
        SELECT *
        FROM notifications
        WHERE user_email=%s
        ORDER BY created_at DESC
    """, (session["user_email"],))

    notifications = cursor.fetchall()

    unread = sum(
        1 for n in notifications
        if not n["is_read"]
    )

    cursor.close()

    return render_template(
    "dashboard.html",
    user=user,
    current_mood=current_mood,
    weekly_average=weekly_average,
    today_sessions=today_sessions,
    emotion_counts=emotion_counts,
    notifications=notifications,
    unread=unread,
    treatment_info=treatment_info,
    recent_activities=recent_activities
)


@app.route("/detect_emotion", methods=["POST"])
def detect_emotion_route():

    text = request.form["message"]

    emotion = detect_emotion(text)

    suggestions = {
        "sadness": "Try 4-7-8 breathing and a 10-minute meditation.",
        "joy": "Keep a gratitude journal today.",
        "anger": "Take a short walk and practice deep breathing.",
        "fear": "Try grounding exercises and talk to someone you trust.",
        "surprise": "Take a moment to reflect before reacting.",
        "love": "Share your positive feelings with someone.",
        "neutral": "Maintain a healthy routine today."
    }

    return {
        "emotion": emotion,
        "suggestion": suggestions.get(emotion, "Take care of yourself.")
    }

@app.route("/chat")
def chat():

    if "user_email" not in session:
        return redirect("/login")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # ----------------------------
    # Get logged-in user
    # ----------------------------
    cursor.execute("""
        SELECT id, name, profile_photo
        FROM users
        WHERE email=%s
    """, (session["user_email"],))

    user = cursor.fetchone()

    # Generate initials
    if user and user["name"]:
        user["initials"] = "".join(
            part[0].upper()
            for part in user["name"].split()
        )

        cursor.execute("""
        SELECT
        id,
        title
        FROM chat_sessions
        WHERE user_id=%s
        ORDER BY created_at DESC
        """, (user["id"],))

        sessions = cursor.fetchall()

# ----------------------------
# Create a session only if
# one doesn't already exist
# ----------------------------

        if session.get("chat_session_id"):

            cursor.execute("""
            SELECT
            user_message,
            bot_response,
            timestamp
            FROM chat_history
            WHERE session_id=%s
            ORDER BY timestamp ASC
            """, (session["chat_session_id"],))

            chats = cursor.fetchall()

        else:

            chats = []

    cursor.close()

    return render_template(
        "chat.html",
        user=user,
        chats=chats,
        sessions=sessions
    )


@app.route("/send_message", methods=["POST"])
def send_message():

    if "user_email" not in session:
        return redirect("/login")

    message = request.form.get("message", "").strip()

    if not message:
        return {
            "intent": "NEUTRAL",
            "emotion": None,
            "reply": "Please enter a message so I can help you. 💙"
        }, 400

    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:

        # ----------------------------------
        # 1. Get logged-in user
        # ----------------------------------

        cursor.execute("""
            SELECT id
            FROM users
            WHERE email=%s
        """, (session["user_email"],))

        logged_user = cursor.fetchone()

        if not logged_user:
            session.clear()
            return {"error": "Please log in again."}, 401

        user_id = logged_user["id"]

        # ----------------------------------
        # 2. Create a chat session if needed
        # ----------------------------------

        if "chat_session_id" not in session:

            cursor.execute("""
                INSERT INTO chat_sessions(user_id)
                VALUES(%s)
            """, (user_id,))

            db.commit()

            session["chat_session_id"] = cursor.lastrowid

        chat_session_id = session["chat_session_id"]

        # ----------------------------------
        # 3. Verify session ownership
        # ----------------------------------

        cursor.execute("""
            SELECT id
            FROM chat_sessions
            WHERE id=%s AND user_id=%s
        """, (chat_session_id, user_id))

        chat_session = cursor.fetchone()

        if not chat_session:
            session.pop("chat_session_id", None)

            return {
                "error": "Chat session not found. Please start a new chat."
            }, 404

        # ----------------------------------
        # 4. Classify intent and generate reply
        # ----------------------------------

        result = get_intent_and_response(message)

        intent = result["intent"]
        reply = result["reply"]

        # Always initialize emotion for every message.
        emotion = None

        # ----------------------------------
        # 5. Detect emotion only for emotional
        #    support messages
        # ----------------------------------

        if intent == "EMOTIONAL_SUPPORT":

            try:

                detected_emotion = detect_emotion(message)

                if detected_emotion:

                    detected_emotion = (
                        detected_emotion.lower().strip()
                    )

                    # Neutral output is not recorded as a mood.
                    if detected_emotion != "neutral":
                        emotion = detected_emotion

            except Exception as e:

                print("Emotion Detection Error:", str(e))

        # ----------------------------------
        # 6. Save emotion history when detected
        # ----------------------------------

        if emotion:

            cursor.execute("""
                INSERT INTO emotion_history
                (user_email, message, emotion)
                VALUES (%s, %s, %s)
            """, (
                session["user_email"],
                message,
                emotion
            ))

            cursor.execute("""
                INSERT INTO mood_logs
                (user_id, message, emotion)
                VALUES (%s, %s, %s)
            """, (
                user_id,
                message,
                emotion
            ))

        # ----------------------------------
        # 7. Save chat history
        # ----------------------------------

        cursor.execute("""
            INSERT INTO chat_history
            (
                user_id,
                session_id,
                user_message,
                bot_response
            )
            VALUES (%s, %s, %s, %s)
        """, (
            user_id,
            chat_session_id,
            message,
            reply
        ))

        # ----------------------------------
        # 8. Generate a chat title after
        #    the third message
        # ----------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM chat_history
            WHERE session_id=%s
        """, (chat_session_id,))

        total_messages = cursor.fetchone()["total"]

        if total_messages == 3:

            cursor.execute("""
                SELECT user_message
                FROM chat_history
                WHERE session_id=%s
                ORDER BY timestamp ASC
            """, (chat_session_id,))

            conversation = cursor.fetchall()

            user_messages = [
                chat["user_message"]
                for chat in conversation
            ]

            title = generate_local_chat_title(user_messages)

            cursor.execute("""
                UPDATE chat_sessions
                SET title=%s
                WHERE id=%s AND user_id=%s
            """, (
                title,
                chat_session_id,
                user_id
            ))

        db.commit()

        # ----------------------------------
        # 9. Return data to the frontend
        # ----------------------------------

        return {
            "intent": intent,
            "emotion": emotion,
            "reply": reply
        }

    except Exception as e:

        db.rollback()

        print("Send Message Error:", str(e))

        return {
            "error": "Something went wrong while processing your message."
        }, 500

    finally:
        cursor.close()

@app.route("/reset_chat")
def reset_chat():

    if "chat_session_id" in session:
        session.pop("chat_session_id", None)

    return "OK"

@app.route("/chat/<int:session_id>")
def open_chat(session_id):

    if "user_email" not in session:
        return redirect("/login")

    session["chat_session_id"] = session_id

    return redirect("/chat")

@app.route("/history")
def history():

    if "user_email" not in session:
        return redirect("/login")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Fetch user details
    cursor.execute("""
        SELECT name, profile_photo
        FROM users
        WHERE email=%s
    """, (session["user_email"],))

    user = cursor.fetchone()

    # Generate initials
    if user and user["name"]:
        user["initials"] = "".join(
            part[0].upper()
            for part in user["name"].split()
        )

    # Fetch emotion history
    cursor.execute("""
        SELECT *
        FROM emotion_history
        WHERE user_email=%s
        ORDER BY created_at DESC
    """, (session["user_email"],))

    emotions = cursor.fetchall()

    cursor.close()

    return render_template(
        "history.html",
        emotions=emotions,
        user=user
    )

@app.route("/reports")
def reports():

    if "user_email" not in session:
        return redirect("/login")

    db = get_db()

    cursor = db.cursor(dictionary=True)

    # Get all reports of logged-in user
    cursor.execute("""
        SELECT *
        FROM medical_reports
        WHERE user_email=%s
        ORDER BY uploaded_at DESC
    """, (session["user_email"],))

    reports = cursor.fetchall()

    # Total reports
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM medical_reports
        WHERE user_email=%s
    """, (session["user_email"],))

    total_reports = cursor.fetchone()

    # Latest report
    latest_report = reports[0] if reports else None

    return render_template(
        "reports.html",
        reports=reports,
        total_reports=total_reports,
        latest_report=latest_report
    )

@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "user_email" not in session:
        return redirect("/login")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM users
        WHERE email=%s
    """, (session["user_email"],))

    user = cursor.fetchone()

    if user and user["name"]:

        name_parts = user["name"].split()

        initials = ""

        for part in name_parts:
            initials += part[0].upper()

            user["initials"] = initials

    # =============================
    # Upload Profile Picture
    # =============================

    if request.method == "POST":

        if "photo" in request.files:

            photo = request.files["photo"]

            if photo.filename != "":

                filename = secure_filename(photo.filename)

                filename = (
                    str(int(time.time()))
                    + "_"
                    + filename
                )

                photo.save(
                    os.path.join(
                        app.config["PROFILE_FOLDER"],
                        filename
                    )
                )

                cursor.execute("""
                    UPDATE users
                    SET profile_photo=%s
                    WHERE email=%s
                """, (
                    filename,
                    session["user_email"]
                ))

                db.commit()

                flash("Profile picture updated successfully!")
                return redirect("/profile")

    # Get uploaded reports
    cursor.execute("""
        SELECT *
        FROM medical_reports
        WHERE user_email=%s
        ORDER BY uploaded_at DESC
    """, (session["user_email"],))

    reports = cursor.fetchall()

    total_reports = len(reports)

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM emotion_history
        WHERE user_email=%s
    """, (session["user_email"],))

    total_logs = cursor.fetchone()

    cursor.execute("""
        SELECT emotion,
               COUNT(*) AS count
        FROM emotion_history
        WHERE user_email=%s
        GROUP BY emotion
        ORDER BY count DESC
        LIMIT 1
    """, (session["user_email"],))

    top_emotion = cursor.fetchone()

# =============================
# Get Medical Profile
# =============================

    cursor.execute("""
    SELECT
        cancer_type,
        cancer_stage,
        current_treatment,
        treatment_start_date,
        medical_notes
    FROM users
    WHERE email=%s
    """, (session["user_email"],))

    medical_profile = cursor.fetchone()

    return render_template(
        "profile.html",
        user=user,
        reports=reports,
        total_logs=total_logs,
        top_emotion=top_emotion,
        total_reports=total_reports,
        medical_profile=medical_profile
    )

@app.route("/upload_report", methods=["POST"])
def upload_report():

    if "user_email" not in session:
        return redirect("/login")

    if "report" not in request.files:
        flash("No file selected.")
        return redirect("/profile")

    file = request.files["report"]

    if file.filename == "":
        flash("Please select a file.")
        return redirect("/profile")

    if not allowed_file(file.filename):
        flash("Invalid file type. Please upload PDF, JPG, JPEG, or PNG.")
        return redirect("/profile")

    try:

        filename = secure_filename(file.filename)

        filepath = os.path.join(
            app.config["REPORT_FOLDER"],
            filename
        )

        file.save(filepath)

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO medical_reports
            (user_email, report_name, file_path)
            VALUES (%s, %s, %s)
        """, (
            session["user_email"],
            filename,
            filepath
        ))

        db.commit()

        cursor.close()

        flash("Medical report uploaded successfully!")

    except Exception as e:

        print("UPLOAD ERROR:", e)

        flash("Error uploading medical report.")

    return redirect("/profile")

@app.route("/analyze_report/<int:report_id>")
def analyze_report(report_id):

    if "user_email" not in session:
        return redirect("/login")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Get selected report
    cursor.execute("""
        SELECT *
        FROM medical_reports
        WHERE id=%s
        AND user_email=%s
    """, (
        report_id,
        session["user_email"]
    ))

    report = cursor.fetchone()

    if not report:

        cursor.close()

        flash("Report not found.")

        return redirect("/reports")

    # Extract text from PDF
    text = extract_pdf_text(report["file_path"])


    # Analyze extracted text
    analysis = analyze_medical_report(text)


    # Get recent emotion history
    cursor.execute("""
        SELECT emotion, created_at
        FROM emotion_history
        WHERE user_email=%s
        ORDER BY created_at DESC
        LIMIT 10
    """, (session["user_email"],))

    emotion_history = cursor.fetchall()

    # Get all reports for reports page
    cursor.execute("""
        SELECT *
        FROM medical_reports
        WHERE user_email=%s
        ORDER BY uploaded_at DESC
    """, (session["user_email"],))

    reports = cursor.fetchall()

    # Calculate emotion distribution
    emotion_counts = Counter(
        item["emotion"].lower()
        for item in emotion_history
        if item["emotion"]
    )

    wellness_insight = generate_wellness_insight(
    analysis,
    emotion_counts
    )

    print("\n========== EMOTION DISTRIBUTION ==========\n")
    print(emotion_counts)
    print("\n==========================================\n")

    # Total reports
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM medical_reports
        WHERE user_email=%s
    """, (session["user_email"],))

    total_reports = cursor.fetchone()

    # Latest report
    latest_report = reports[0] if reports else None

    cursor.close()

    return render_template(
        "reports.html",
        reports=reports,
        total_reports=total_reports,
        latest_report=latest_report,
        analysis=analysis,
        analyzed_report=report,
        wellness_insight=wellness_insight
    )

@app.route("/remove_profile_photo", methods=["POST"])
def remove_profile_photo():

    if "user_email" not in session:
        return redirect("/login")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Get current filename
    cursor.execute("""
        SELECT profile_photo
        FROM users
        WHERE email=%s
    """, (session["user_email"],))

    user = cursor.fetchone()

    # Delete file if it exists
    if user and user["profile_photo"]:

        path = os.path.join(
            app.config["PROFILE_FOLDER"],
            user["profile_photo"]
        )

        if os.path.exists(path):
            os.remove(path)

    # Remove filename from database
    cursor.execute("""
        UPDATE users
        SET profile_photo=NULL
        WHERE email=%s
    """, (session["user_email"],))

    db.commit()

    flash("Profile photo removed successfully.")

    return redirect("/profile")

@app.route("/view_report/<int:id>")
def view_report(id):

    if "user_email" not in session:
        return redirect("/login")

    db = get_db()

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM medical_reports
        WHERE id=%s
        """,
        (id,)
    )

    report = cursor.fetchone()

    cursor.close()

    return send_from_directory(
    app.config["REPORT_FOLDER"],
    os.path.basename(report["file_path"])
)

@app.route("/download_report/<int:id>")
def download_report(id):

    if "user_email" not in session:
        return redirect("/login")

    db = get_db()

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM medical_reports
        WHERE id=%s
    """, (id,))

    report = cursor.fetchone()

    cursor.close()

    if not report:
        return "Report not found."

    return send_from_directory(
        app.config["REPORT_FOLDER"],
        report["report_name"],
        as_attachment=True
    )

@app.route("/delete_report/<int:id>")
def delete_report(id):

    if "user_email" not in session:
        return redirect("/login")

    db = get_db()

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM medical_reports
        WHERE id=%s
        """,
        (id,)
    )

    report = cursor.fetchone()

    if report:

        if os.path.exists(report["file_path"]):
            os.remove(report["file_path"])

        cursor = db.cursor()

        cursor.execute(
            """
            DELETE FROM medical_reports
            WHERE id=%s
            """,
            (id,)
        )

        db.commit()

    return redirect("/profile")

@app.route("/upload_profile_picture", methods=["POST"])
def upload_profile_picture():

    if "user_email" not in session:
        return redirect("/login")

    if "profile_picture" not in request.files:
        flash("No file selected.")
        return redirect("/profile")

    photo = request.files["profile_picture"]

    if photo.filename == "":
        flash("No file selected.")
        return redirect("/profile")

    filename = secure_filename(photo.filename)
    filename = f"{int(time.time())}_{filename}"

    photo.save(os.path.join(app.config["PROFILE_FOLDER"], filename))

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        UPDATE users
        SET profile_photo=%s
        WHERE email=%s
        """,
        (filename, session["user_email"])
    )

    db.commit()
    cursor.close()

    flash("Profile picture updated successfully!")

    return redirect("/profile")

@app.route("/update_profile", methods=["POST"])
def update_profile():

    if "user_email" not in session:
        return redirect("/login")

    name = request.form["name"]
    gender = request.form["gender"]
    password = request.form["password"]

    db = get_db()
    cursor = db.cursor()

    if password.strip() == "":
        cursor.execute("""
            UPDATE users
            SET name=%s,
                gender=%s
            WHERE email=%s
        """, (
            name,
            gender,
            session["user_email"]
        ))

    else:
        cursor.execute("""
            UPDATE users
            SET name=%s,
                gender=%s,
                password=%s
            WHERE email=%s
        """, (
            name,
            gender,
            password,
            session["user_email"]
        ))

    db.commit()

    flash("Profile updated successfully!")

    return redirect("/profile")

@app.route("/save_medical_profile", methods=["POST"])
def save_medical_profile():

    if "user_email" not in session:
        return redirect("/login")

    user_email = session["user_email"]

    cancer_type = request.form.get("cancer_type")
    cancer_stage = request.form.get("cancer_stage")
    current_treatment = request.form.get("current_treatment")
    treatment_start_date = request.form.get("treatment_start_date")
    medical_notes = request.form.get("medical_notes")

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE users
        SET
            cancer_type=%s,
            cancer_stage=%s,
            current_treatment=%s,
            treatment_start_date=%s,
            medical_notes=%s
        WHERE email=%s
    """, (
        cancer_type,
        cancer_stage,
        current_treatment,
        treatment_start_date if treatment_start_date else None,
        medical_notes,
        user_email
    ))

    db.commit()

    cursor.close()

    flash("Medical profile saved successfully!")

    return redirect("/profile")

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

@app.route("/settings")
def settings():

    if "user_email" not in session:
        return redirect("/login")

    db = get_db()

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM users WHERE email=%s",
        (session["user_email"],)
    )

    user = cursor.fetchone()

    cursor.close()

    return render_template(
        "settings.html",
        user=user
    )

@app.route("/delete_account")
def delete_account():

    if "user_email" not in session:
        return redirect("/login")

    db = get_db()

    cursor = db.cursor()

    # Delete user's reports
    cursor.execute(
        "DELETE FROM medical_reports WHERE user_email=%s",
        (session["user_email"],)
    )

    # Delete emotion history
    cursor.execute(
        "DELETE FROM emotion_history WHERE user_email=%s",
        (session["user_email"],)
    )

    # Delete user
    cursor.execute(
        "DELETE FROM users WHERE email=%s",
        (session["user_email"],)
    )

    db.commit()

    session.clear()

    return redirect("/login?success=account_deleted")

@app.route("/test_report/<int:report_id>")
def test_report(report_id):

    if "user_email" not in session:
        return redirect("/login")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM medical_reports
        WHERE id=%s
        AND user_email=%s
    """, (
        report_id,
        session["user_email"]
    ))

    report = cursor.fetchone()

    cursor.close()

    if not report:
        return "Report not found"

    text = extract_pdf_text(report["file_path"])

    analysis = analyze_medical_report(text)

    print("\n========== MEDICAL ANALYSIS ==========\n")
    print(analysis)
    print("\n======================================\n")
    return "<pre>" + str(analysis) + "</pre>"

if __name__ == "__main__":
    app.run(debug=True)
