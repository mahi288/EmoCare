# EmoCare – Caring Beyond Cancer

EmoCare is an AI-powered web-based emotional support system designed to provide personalized emotional assistance to cancer patients. The system analyzes a patient's emotional state from their text input and provides supportive responses based on their detected emotion and personal medical information.

The platform combines **emotion recognition, AI-powered conversational support, mood tracking, medical profile management, medical report management, and personalized patient support** in a single web application.

---

## 📌 Project Overview

Cancer treatment can affect a patient's emotional well-being as well as their physical health. Patients may experience emotions such as sadness, fear, anger, anxiety, stress, and emotional distress during different stages of treatment.

EmoCare aims to provide a supportive digital companion that allows patients to:

* Express their feelings through text.
* Detect their emotional state using an AI-based emotion classification model.
* Receive supportive conversational responses.
* Maintain a history of their emotional inputs.
* Track their mood over time.
* Store personal medical information.
* Upload and manage medical reports.
* Receive personalized AI-based assistance using their available medical information.

The system is intended as a **supportive companion and not as a replacement for professional medical advice or treatment**.

---

## ✨ Key Features

### 🔐 User Authentication

* New user registration.
* Secure login system.
* Session-based authentication.
* Forgot-password and OTP verification pages.
* Password reset functionality.

### 🧠 Emotion Recognition

* Accepts emotional input from the user.
* Uses a pre-trained Hugging Face emotion classification model.
* Detects the most relevant emotion from the user's text.
* Stores detected emotions in the database.
* Maintains an emotion history for the patient.

### 💬 AI Chat Companion

* AI-powered conversational support.
* Generates supportive responses based on the user's message.
* Uses the user's available medical profile information for personalization.
* Maintains chat sessions and chat history.
* Generates conversation titles using AI.

### 📊 Emotion & Mood History

* Stores previous emotional inputs.
* Displays detected emotions and timestamps.
* Allows patients to review their emotional history.
* Provides a record of changes in emotional state over time.

### 🏥 Medical Profile

Patients can maintain relevant medical information including:

* Cancer type
* Cancer stage
* Current treatment
* Treatment start date
* Medical notes
* Profile information
* Profile photo

### 📄 Medical Reports

* Upload medical reports in supported formats.
* Store uploaded report information in the database.
* View and manage uploaded reports.
* Dedicated reports section for easier access.

Supported file formats:

```text
PDF
PNG
JPG
JPEG
```

### 🔔 Notifications

The system includes notification management for relevant patient-related activities and alerts.

### 🎨 User Interface

* Responsive web interface.
* Dashboard-based navigation.
* Sidebar navigation.
* Theme customization.
* Dedicated pages for profile, reports, history, settings, and chat.
* Emotion-based dashboard experience.

---

## 🛠️ Technologies Used

### Frontend

* HTML5
* CSS3
* JavaScript
* Chart.js / frontend visualization components where applicable

### Backend

* Python
* Flask

### Database

* MySQL
* MySQL Connector/Python

### Artificial Intelligence

* Hugging Face Transformers
* `j-hartmann/emotion-english-distilroberta-base`
* Google Gemini API

### Development Tools

* Visual Studio Code
* MySQL Workbench
* Git
* GitHub
* Python Virtual Environment

---

## 🏗️ System Architecture

The basic flow of EmoCare is:

```text
                    ┌─────────────────────┐
                    │       Patient       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Web Interface    │
                    │ HTML / CSS / JS     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Flask Backend    │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
        ┌──────────────┐ ┌────────────┐ ┌──────────────┐
        │   Emotion    │ │   Gemini   │ │    Medical   │
        │  Detection   │ │     AI     │ │    Profile   │
        └──────┬───────┘ └─────┬──────┘ └──────┬───────┘
               │               │               │
               └───────────────┼───────────────┘
                               ▼
                    ┌─────────────────────┐
                    │    MySQL Database   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Personalized User  │
                    │     Experience      │
                    └─────────────────────┘
```

---

## 📁 Project Structure

```text
EmoCare/
│
├── ai/
│   ├── emotion_detector.py
│   ├── gemini_chat.py
│   └── gemini_title.py
│
├── database/
│   └── db.py
│
├── static/
│   ├── css/
│   │   ├── chat.css
│   │   ├── dashboard.css
│   │   ├── forgot_password.css
│   │   ├── history.css
│   │   ├── home.css
│   │   ├── login.css
│   │   ├── profile.css
│   │   ├── register.css
│   │   ├── reports.css
│   │   ├── settings.css
│   │   ├── sidebar.css
│   │   └── theme.css
│   │
│   ├── images/
│   └── js/
│       └── script.js
│
├── templates/
│   ├── chat.html
│   ├── dashboard.html
│   ├── forgot_password.html
│   ├── history.html
│   ├── home.html
│   ├── login.html
│   ├── profile.html
│   ├── register.html
│   ├── reports.html
│   ├── reset_password.html
│   ├── settings.html
│   └── verify_otp.html
│
├── app.py
├── list_models.py
├── test_db.py
├── test_emotion.py
├── test_gemini.py
├── .gitignore
└── README.md
```

---

## 🗄️ Database Structure

The application uses a MySQL database named:

```text
eac_system
```

The current implementation uses the following tables:

### `users`

Stores user authentication and medical profile information.

Main fields include:

* `id`
* `name`
* `email`
* `password`
* `gender`
* `profile_image`
* `profile_photo`
* `cancer_type`
* `cancer_stage`
* `current_treatment`
* `treatment_start_date`
* `medical_notes`

### `emotion_history`

Stores patient emotional inputs and detected emotions.

### `mood_logs`

Stores mood-related patient activity.

### `chat_sessions`

Stores individual AI chat sessions.

### `chat_history`

Stores messages exchanged during AI conversations.

### `medical_reports`

Stores information about uploaded medical reports.

### `notifications`

Stores system notifications and alerts.

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/mahi288/EmoCare.git
cd EmoCare
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

> `requirements.txt` should be generated from the working development environment before another developer attempts to run the project.

### 4. Configure Environment Variables

Create a `.env` file in the project root.

Example:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=eac_system

GEMINI_API_KEY=your_gemini_api_key
```

**Never commit the `.env` file to GitHub.**

The project uses environment variables so database credentials and API keys are not stored directly in the source code.

### 5. Create the MySQL Database

Open MySQL Workbench or MySQL command line and create:

```sql
CREATE DATABASE eac_system;
```

Then create the required tables according to the database structure used by the application.

### 6. Start the Application

Activate the virtual environment and run:

```bash
python app.py
```

The Flask development server will normally start at:

```text
http://127.0.0.1:5000
```

Open the address in a web browser.

---

## 🤖 Emotion Recognition

EmoCare uses the pre-trained:

```text
j-hartmann/emotion-english-distilroberta-base
```

model from Hugging Face Transformers.

The user's text is passed to the emotion classification component, which predicts the most likely emotion label.

The detected result is then stored in the `emotion_history` table and can be used by the application to support the user's conversational experience.

Because the model is trained on a predefined set of emotion categories, its prediction may not always exactly match the emotion word used by the user. For example, a message describing stress may sometimes be classified under another related emotion.

---

## 💬 AI Conversational Support

The AI chat component uses the Gemini API to generate conversational responses.

The system can use available patient information such as:

* Cancer type
* Cancer stage
* Current treatment
* Treatment start date
* Medical notes

to provide more context-aware conversational support.

The application also maintains chat sessions and chat history so users can continue previous conversations.

---

## 🔒 Security Considerations

The project follows basic security practices including:

* Environment variables for sensitive credentials.
* `.gitignore` protection for `.env`.
* Session-based authentication.
* Secure filename handling for uploaded files.
* Restricted medical report file extensions.
* Uploaded patient reports and profile files excluded from Git tracking.

### Important

Medical information is sensitive data. A production deployment should additionally implement:

* HTTPS
* Strong password hashing
* Proper authentication and authorization
* Secure session configuration
* File size restrictions
* Malware scanning for uploads
* Encryption of sensitive data
* Database access controls
* Secure API-key management
* Production-grade logging and monitoring

---

## 🧪 Testing

The project includes separate testing scripts for important components.

### Database Test

```bash
python test_db.py
```

This verifies connectivity with the MySQL database.

### Emotion Detection Test

```bash
python test_emotion.py
```

This tests the emotion classification component.

### Gemini Test

```bash
python test_gemini.py
```

This verifies the Gemini integration.

---

## 📌 Current Application Pages

The current application includes:

* Home
* Register
* Login
* Forgot Password
* OTP Verification
* Password Reset
* Dashboard
* Emotion History
* Chat Companion
* Reports
* Profile
* Settings

---

## 🚀 Future Enhancements

Possible future improvements include:

* Mobile application support.
* Improved emotion classification for healthcare-specific language.
* Multilingual emotional analysis.
* Voice-based emotional input.
* Advanced mood trend visualization.
* Real-time emergency alert integration.
* Doctor/caregiver dashboard.
* Appointment and medication reminders.
* Advanced medical report analysis.
* Secure cloud deployment.
* Improved personalization using long-term emotional patterns.
* Integration with wearable devices for additional health-related signals.

---

## ⚠️ Disclaimer

EmoCare is an academic/software engineering project designed to provide emotional and conversational support.

It is **not a medical diagnostic system** and should not be used as a substitute for doctors, psychologists, oncologists, or other qualified healthcare professionals.

Users experiencing severe emotional distress or a medical emergency should seek immediate professional assistance.

---

## 👩‍💻 Project

**Project Name:** EmoCare – Caring Beyond Cancer

**Domain:** Artificial Intelligence / Healthcare / Web Application

**Backend:** Flask + Python

**Database:** MySQL

**AI:** Hugging Face Transformers + Google Gemini

**Repository:**
https://github.com/mahi288/EmoCare

---

## 📄 License

This project is developed for academic and educational purposes.

A suitable open-source license can be added if the project is intended for public redistribution.
