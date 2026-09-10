// ==============================
// GLOBAL STORAGE KEY
// ==============================
const STORAGE_KEY = "EAC_USERS";


// ==============================
// HOMEPAGE BUTTON HANDLER
// ==============================
document.addEventListener("DOMContentLoaded", function () {

    // Homepage Buttons
    const getStartedBtn = document.querySelector(".btn-primary");
    const learnMoreBtn = document.querySelector(".btn-secondary");

    if (getStartedBtn) {
        getStartedBtn.addEventListener("click", function () {
            window.location.href = "/login";
        });
    }

    if (learnMoreBtn) {
        learnMoreBtn.addEventListener("click", function () {
            //alert("EAC detects emotions using AI & provides adaptive support 💙");
        });
    }

});


// ================= SHOW / HIDE PASSWORD =================

const togglePassword = document.getElementById("togglePassword");

if (togglePassword) {
    togglePassword.addEventListener("click", function () {

        const passwordInput = document.getElementById("loginPassword");

        if (passwordInput.type === "password") {
            passwordInput.type = "text";
            togglePassword.textContent = "🙈";
        } else {
            passwordInput.type = "password";
            togglePassword.textContent = "👁";
        }

    });
}

document.querySelectorAll(".togglePassword").forEach(icon => {

    icon.addEventListener("click", function () {

        const input = document.getElementById(this.dataset.target);

        if (input.type === "password") {
            input.type = "text";
            this.textContent = "🙈";
        } else {
            input.type = "password";
            this.textContent = "👁";
        }

    });

});

const forgotLink = document.getElementById("forgotPassword");

if (forgotLink) {
    forgotLink.addEventListener("click", function (e) {
    e.preventDefault();
    // Coming soon
});
}

// ==============================
// DASHBOARD FUNCTIONALITY
// ==============================

if (window.location.pathname.includes("dashboard") || 
    window.location.pathname.includes("homepage")) {

    const welcomeText = document.querySelector(".topbar h3");

    if (welcomeText) {
    welcomeText.textContent = "Welcome Back 👋";
}

document.addEventListener("DOMContentLoaded", function () {

    const bell = document.getElementById("notificationBtn");
    const dropdown = document.getElementById("notificationDropdown");

    if (bell && dropdown) {

        bell.addEventListener("click", function (e) {

            e.stopPropagation();

            dropdown.style.display =
                dropdown.style.display === "block"
                ? "none"
                : "block";
            
            });

        document.addEventListener("click", function () {
            dropdown.style.display = "none";
        });

    }

});

// ==============================
// MOOD SELECTOR
// ==============================

const moodButtons = document.querySelectorAll(".moodBtn");
const currentMood = document.getElementById("currentMood");
const quote = document.getElementById("moodQuote");

const quotes = {
    "Happy": "Keep smiling! Your happiness is contagious.",
    "Sad": "Tough times never last, but tough people do.",
    "Angry": "Take a deep breath. Calm mind brings better decisions.",
    "Calm": "Peace begins with a calm mind.",
    "Anxious": "You’ve handled tough things before. You can do it again.",
    "Excited": "Your energy is powerful. Use it to create something amazing."
};

moodButtons.forEach(button => {

    button.addEventListener("click", function () {

        const mood = this.textContent.trim();   // get mood text
        const moodName = mood.replace(/[^\w\s]/gi,'').trim(); // remove emoji

        // Update current mood card
        currentMood.textContent = mood;

        // Update quote
        quote.textContent = quotes[moodName] || "Stay positive!";

        // Save mood
        localStorage.setItem("EMOCARE_CURRENT_MOOD", mood);

    });

});

// Load saved mood
const savedMood = localStorage.getItem("EMOCARE_CURRENT_MOOD");

if (savedMood) {
    currentMood.textContent = savedMood;

    const moodName = savedMood.replace(/[^\w\s]/gi,'').trim();
    quote.textContent = quotes[moodName] || "Stay positive!";
}

    // ==============================
    // SESSION COUNTER
    // ==============================

    let sessions = parseInt(localStorage.getItem("EAC_SESSIONS")) || 0;
    sessions++;

    localStorage.setItem("EAC_SESSIONS", sessions);

    const sessionCard = document.querySelectorAll(".card p")[2];

    if (sessionCard) {
        sessionCard.textContent = sessions;
    }

const tips = [
"Take 5 deep breaths to relax your mind.",
"Drink water and stretch your body.",
"Write one thing you are grateful for.",
"Take a short walk outside.",
"Listen to calming music for 5 minutes."
];

function newTip(){

const randomTip = tips[Math.floor(Math.random()*tips.length)];

document.getElementById("wellnessTip").innerText = randomTip;

}

    // ==============================
    // SIDEBAR MENU ACTIVE STATE
    // ==============================

    const menuItems = document.querySelectorAll(".sidebar li");

    menuItems.forEach(item => {
        item.addEventListener("click", function () {

            menuItems.forEach(i => i.classList.remove("active"));
            this.classList.add("active");

        });
    });


    // ==============================
    // LOGOUT BUTTON
    // ==============================

    const logoutBtn = Array.from(menuItems).find(li =>
    li.textContent.toLowerCase().includes("logout")
);

if (logoutBtn) {
    logoutBtn.addEventListener("click", function () {

        window.location.href = "/logout";

    });
}

    function openChat(){
alert("AI Companion will open here.");
}


    // ==============================
    // NOTIFICATION CLICK
    // ==============================

    const alertIcon = document.querySelector(".alert");

if (alertIcon) {
    alertIcon.addEventListener("click", function () {
        // Future notification code
    });
}

    // ==============================
    // SEARCH FUNCTION (DEMO)
    // ==============================

    const searchInput = document.querySelector(".search-box input");

    if (searchInput) {

        searchInput.addEventListener("keyup", function (e) {

            if (e.key === "Enter") {

                const query = searchInput.value.trim();

                if (query) {
                    console.log("Searching:", query);
                }

            }

        });

    }

}

function setMood(mood){

    const body=document.body;

    // In Dark Mode, don't change the background
    if(body.classList.contains("dark-mode")){

        body.style.background="var(--bg)";
        return;

    }

    // Light Mode backgrounds

    if(mood==="happy"){

        body.style.background=
        "linear-gradient(135deg,#fff8dc,#fff3b0)";

    }

    else if(mood==="calm"){

        body.style.background=
        "linear-gradient(135deg,#eef7ff,#d6eaff)";

    }

    else if(mood==="sad"){

        body.style.background=
        "linear-gradient(135deg,#eef2ff,#dbe4ff)";

    }

    else if(mood==="angry"){

        body.style.background=
        "linear-gradient(135deg,#ffecec,#ffd6d6)";

    }

    else if(mood==="stressed"){

        body.style.background=
        "linear-gradient(135deg,#f5e9ff,#ead5ff)";

    }

}


async function detectEmotion() {

    let text =
        document.getElementById("emotionText").value;

    let formData = new FormData();

    formData.append("message", text);

    let response = await fetch("/detect_emotion", {
        method: "POST",
        body: formData
    });

    let data = await response.json();

    document.getElementById("result").innerHTML =
        "Detected Emotion: " + data.emotion;

    document.getElementById("suggestion").innerHTML =
        "Suggested Activity: " + data.suggestion;
}

// ======================
// CHAT COMPANION
// ======================

function sendMessage() {

    let input = document.getElementById("userMessage");

    if (!input) return;

    let message = input.value.trim();

    if (message === "") return;

    let chatBox = document.getElementById("chatMessages");

    chatBox.innerHTML += `
        <div class="user-message">
            ${message}
        </div>
    `;

    fetch("/send_message", {

        method: "POST",

        headers: {
            "Content-Type":
            "application/x-www-form-urlencoded"
        },

        body:
        "message=" +
        encodeURIComponent(message)

    })

    .then(response => response.json())

    .then(data => {

        // Remove Markdown ** from Gemini response
        let botReply = data.reply
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.*?)\*/g, "<em>$1</em>");
        
        chatBox.innerHTML += `
            <div class="bot-message">
                ${botReply}
            </div>
        `;

        chatBox.scrollTop =
        chatBox.scrollHeight;

    })
    .catch(error => {
        console.error("Chat error:", error);
    });

    input.value = "";
}

document.addEventListener("DOMContentLoaded", () => {

    const input =
    document.getElementById("userMessage");

    if(input){

        input.addEventListener("keypress", function(e){

            if(e.key === "Enter"){

                sendMessage();

            }

        });

    }

});

function showToast(message){

const toast=document.getElementById("toast");

if(!toast) return;

toast.innerHTML=message;

toast.classList.add("show");

setTimeout(function(){

toast.classList.remove("show");

},2500);

}

document.addEventListener("DOMContentLoaded",function(){

const params=new URLSearchParams(window.location.search);

if(params.get("success")=="registered"){
showToast("🎉 Registration Successful!");
}

if(params.get("success")=="login"){
showToast("✅ Login Successful!");
}

if(params.get("success")=="logout"){
showToast("👋 Logged Out Successfully!");
}

if(params.get("error")=="invalid"){
    showToast("❌ Invalid Email or Password");
}

if(params.get("success")=="updated"){
    showToast("✅ Profile Updated Successfully!");
}

});

// ===============================
// PROFILE MODAL
// ===============================

function openProfileModal(){

    document.getElementById("profileModal").style.display="block";

}

function closeProfileModal(){

    document.getElementById("profileModal").style.display="none";

}

window.onclick=function(event){

    let modal=document.getElementById("profileModal");

    if(modal && event.target==modal){

        modal.style.display="none";

    }

}

// ===============================
// PROFILE PICTURE UPLOAD
// ===============================

document.addEventListener("DOMContentLoaded", function () {

    const fileInput = document.getElementById("profilePictureInput");

    if(fileInput){

        fileInput.addEventListener("change", function(){

            if(this.files.length > 0){

                document.getElementById("profileUploadForm").submit();

            }

        });

    }

});

function deleteAccount(){

    if(confirm("Are you sure you want to permanently delete your account?")){

        window.location.href="/delete_account";

    }

}

// ==========================
// GLOBAL THEME
// ==========================

function applyTheme(theme){

    if(theme === "dark"){

        document.body.classList.add("dark-mode");

    }else{

        document.body.classList.remove("dark-mode");

    }

}

function setTheme(theme){

    localStorage.setItem("emocare_theme", theme);

    applyTheme(theme);

}

document.addEventListener("DOMContentLoaded", function(){

    const savedTheme =
        localStorage.getItem("emocare_theme") || "light";

    applyTheme(savedTheme);

});

const profileInput = document.getElementById("profilePictureInput");

if (profileInput) {
    profileInput.addEventListener("change", function () {
        document.getElementById("profileUploadForm").submit();
    });
}

const chartCanvas = document.getElementById("moodChart");

if(chartCanvas){

    const ctx = chartCanvas.getContext("2d");

    new Chart(ctx,{
        type:"doughnut",

        data:{

            labels:[
                "Happy",
                "Calm",
                "Sad",
                "Angry",
                "Stressed"
            ],

            datasets:[{

                label:"Mood Count",

                data: [
                    emotionCounts.Happy,
                    emotionCounts.Calm,
                    emotionCounts.Sad,
                    emotionCounts.Angry,
                    emotionCounts.Stressed
                ],

                backgroundColor:[
                    "#FFD93D",
                    "#4CAF50",
                    "#5DADE2",
                    "#FF6B6B",
                    "#9B59B6"
                ],

                borderWidth:2
            }]
        },

        options:{

            responsive:true,
            maintainAspectRatio: false,

            plugins:{

                legend:{
                    position:"bottom"
                }
            }
        }
    });

}

const historyBtn=document.getElementById("historyBtn");

const historyMenu=document.getElementById("historyMenu");

if(historyBtn){

historyBtn.onclick=function(){

if(historyMenu.style.display==="block"){

historyMenu.style.display="none";

}

else{

historyMenu.style.display="block";

}

};

window.onclick=function(e){

if (
    !historyBtn.contains(e.target) &&
    !historyMenu.contains(e.target)
) {
    historyMenu.style.display = "none";
}

};
}

document.getElementById("newChatBtn").onclick = async function () {

    await fetch("/reset_chat");

    window.location.href = "/chat";

};