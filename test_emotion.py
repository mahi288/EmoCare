from ai.emotion_detector import detect_emotion

emotion = detect_emotion(
    "I am feeling very stressed and worried today"
)

print("Detected Emotion:", emotion)