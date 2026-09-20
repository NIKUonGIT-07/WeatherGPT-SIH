/* =========================
   DOM ELEMENTS
========================= */

const loginScreen = document.getElementById("login-screen");
const loginForm = document.getElementById("login-form");

const loginNameInput = document.getElementById("login-name");
const loginEmailInput = document.getElementById("login-email");
const loginPasswordInput = document.getElementById("login-password");

const sidebarUserName = document.getElementById("sidebar-user-name");

const logoutButton = document.getElementById("logout-button");
const mobileLogoutButton = document.getElementById("mobile-logout-button");

const input = document.querySelector(".input-wrapper input");
const sendButton = document.querySelector(".send-button");
const voiceButton = document.querySelector(".voice-button");

const chatContainer = document.querySelector(".chat-container");
const recentList = document.querySelector(".recent-list");

const newForecastButton = document.querySelector(".new-forecast");

const aqiValue = document.getElementById("aqi-value");
const aqiStatus = document.getElementById("aqi-status");

const uvValue = document.getElementById("uv-value");
const uvStatus = document.getElementById("uv-status");

const sunriseTime = document.getElementById("sunrise-time");
const sunsetTime = document.getElementById("sunset-time");
const stopVoiceButton = document.querySelector(".stop-voice-button");
let isSpeaking = false;


/* =========================
   CONFIGURATION
========================= */

const API_URL = "http://127.0.0.1:8000/chat/";
const API_BASE_URL = "http://127.0.0.1:8000";

const USER_STORAGE_KEY = "weathergpt_user";
const TOKEN_STORAGE_KEY = "weathergpt_token";
const RECENT_STORAGE_KEY = "weathergpt_recent_searches";

let currentConversationId = null;


/* =========================
   HTML SAFETY
========================= */

function escapeHTML(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}


/* =========================
   USER LOGIN
========================= */

function getSavedUser() {
    const savedUser = localStorage.getItem(USER_STORAGE_KEY);

    if (!savedUser) {
        return null;
    }

    try {
        return JSON.parse(savedUser);
    } catch (error) {
        localStorage.removeItem(USER_STORAGE_KEY);
        return null;
    }
}


function saveUser(user) {
    localStorage.setItem(
        USER_STORAGE_KEY,
        JSON.stringify(user)
    );
}


function showAppForUser(user) {
    if (loginScreen) {
        loginScreen.classList.add("hidden");
    }

    if (sidebarUserName) {
        sidebarUserName.textContent = user.name;
    }

    resetChat(user.name);

    if (input) {
        input.focus();
    }
}


function showLoginScreen() {
    if (loginScreen) {
        loginScreen.classList.remove("hidden");
    }

    if (loginNameInput) {
        loginNameInput.focus();
    }
}


async function handleLogin(event) {
    event.preventDefault();

    const name = loginNameInput.value.trim();
    const email = loginEmailInput.value.trim();
    const password = loginPasswordInput.value;

    if (!name || !email || !password) {
        return;
    }

    const loginButton = loginForm.querySelector(".login-button");
    const originalText = loginButton.textContent;

    loginButton.disabled = true;
    loginButton.textContent = "Signing in...";

    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Login failed.");
        }

        localStorage.setItem(
            TOKEN_STORAGE_KEY,
            data.access_token
        );

        const userResponse = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
                "Authorization": `Bearer ${data.access_token}`
            }
        });

        if (!userResponse.ok) {
            throw new Error("Could not load your account.");
        }

        const user = await userResponse.json();

        localStorage.setItem(
            USER_STORAGE_KEY,
            JSON.stringify(user)
        );

        currentConversationId = null;

        showAppForUser(user);

        await loadConversations();

    } catch (error) {
        console.error("Login error:", error);
        alert(error.message || "Unable to sign in.");

    } finally {
        loginButton.disabled = false;
        loginButton.textContent = originalText;
    }
}


function handleLogout() {
    localStorage.removeItem(USER_STORAGE_KEY);
    localStorage.removeItem(RECENT_STORAGE_KEY);
    currentConversationId = null;

    // Stop speech if it is currently playing
    if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
    }

    // Stop microphone if it is currently listening
    if (recognition && isListening) {
        recognition.stop();
    }

    resetChat();
    renderRecentSearches();
    showLoginScreen();
}


/* =========================
   CHAT UI
========================= */

function scrollToBottom() {
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}


function appendUserMessage(message) {
    const row = document.createElement("div");

    row.className = "message-row user-row";

    row.innerHTML = `
        <div class="user-message">
            ${escapeHTML(message)}
        </div>
    `;

    chatContainer.appendChild(row);

    scrollToBottom();
}


function appendBotMessage(message) {
    const row = document.createElement("div");

    row.className = "message-row ai-row";

    row.innerHTML = `
        <div class="ai-avatar">✦</div>

        <div class="forecast-card">
            <pre style="
                white-space: pre-wrap;
                font-family: Inter, sans-serif;
                margin: 0;
                line-height: 1.6;
                color: inherit;
            ">${escapeHTML(message)}</pre>
        </div>
    `;

    chatContainer.appendChild(row);

    scrollToBottom();
}


function showThinkingMessage() {
    const row = document.createElement("div");

    row.className = "message-row ai-row thinking-row";

    row.innerHTML = `
        <div class="ai-avatar">✦</div>

        <div class="forecast-card">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;

    chatContainer.appendChild(row);

    scrollToBottom();

    return row;
}


function removeThinkingMessage(row) {
    if (row) {
        row.remove();
    }
}


/* =========================
   DAILY INSIGHTS
========================= */

function extractNumberAfterLabel(text, label) {
    const pattern = new RegExp(
        `${label}\\s*:?\\s*([0-9]+(?:\\.[0-9]+)?)`,
        "i"
    );

    const match = text.match(pattern);

    if (!match) {
        return null;
    }

    return Number(match[1]);
}


function getInsightStatus(value, type) {
    if (type === "aqi") {
        if (value <= 50) return "Good";
        if (value <= 100) return "Moderate";
        return "Poor";
    }

    if (value <= 2) return "Low";
    if (value <= 5) return "Moderate";
    if (value <= 7) return "High";

    return "Very High";
}


function estimateDailyInsights(reply) {
    const condition = reply.toLowerCase();

    const humidity = extractNumberAfterLabel(
        reply,
        "Humidity"
    );

    const windSpeed = extractNumberAfterLabel(
        reply,
        "Wind Speed"
    );

    const temperature = extractNumberAfterLabel(
        reply,
        "Temperature"
    );

    let estimatedAqi = 42;
    let estimatedUv = 5;

    if (
        condition.includes("rain") ||
        condition.includes("thunderstorm")
    ) {
        estimatedAqi = 35;
        estimatedUv = 2;
    }

    if (humidity !== null && humidity >= 85) {
        estimatedAqi += 8;
        estimatedUv = Math.max(
            1,
            estimatedUv - 1
        );
    }

    if (windSpeed !== null && windSpeed >= 25) {
        estimatedAqi = Math.max(
            25,
            estimatedAqi - 6
        );
    }

    if (temperature !== null && temperature >= 34) {
        estimatedUv = Math.min(
            9,
            estimatedUv + 2
        );
    }

    return {
        aqi: estimatedAqi,
        uv: estimatedUv,
        sunrise: "↑ 5:05 AM",
        sunset: "↓ 5:39 PM"
    };
}


function updateDailyInsights(reply) {
    const insights = estimateDailyInsights(reply);

    if (aqiValue) {
        aqiValue.textContent = insights.aqi;
    }

    if (aqiStatus) {
        aqiStatus.textContent = getInsightStatus(
            insights.aqi,
            "aqi"
        );

        aqiStatus.className =
            insights.aqi <= 50
                ? "insight-status status-good"
                : "insight-status status-mod";
    }

    if (uvValue) {
        uvValue.textContent = insights.uv;
    }

    if (uvStatus) {
        uvStatus.textContent = getInsightStatus(
            insights.uv,
            "uv"
        );

        uvStatus.className =
            insights.uv <= 2
                ? "insight-status status-good"
                : "insight-status status-mod";
    }

    if (sunriseTime) {
        sunriseTime.textContent = insights.sunrise;
    }

    if (sunsetTime) {
        sunsetTime.textContent = insights.sunset;
    }
}


/* =========================
   RECENT SEARCHES
========================= */

function getRecentSearches() {
    const searches = localStorage.getItem(
        RECENT_STORAGE_KEY
    );

    if (!searches) {
        return [];
    }

    try {
        return JSON.parse(searches);
    } catch (error) {
        localStorage.removeItem(
            RECENT_STORAGE_KEY
        );

        return [];
    }
}


function saveRecentSearch(query) {
    let searches = getRecentSearches();

    searches = searches.filter(
        item =>
            item.toLowerCase() !==
            query.toLowerCase()
    );

    searches.unshift(query);

    searches = searches.slice(0, 5);

    localStorage.setItem(
        RECENT_STORAGE_KEY,
        JSON.stringify(searches)
    );

    renderRecentSearches();
}


function renderRecentSearches() {
    if (!recentList) {
        return;
    }

    const searches = getRecentSearches();

    if (searches.length === 0) {
        recentList.innerHTML = `
            <button
                class="recent-location"
                type="button"
                data-query="Weather in Guwahati"
            >
                <span class="location-icon">⌖</span>
                <span>Guwahati, India</span>
            </button>

            <button
                class="recent-location"
                type="button"
                data-query="Weather in Mumbai"
            >
                <span class="location-icon">⌖</span>
                <span>Mumbai, India</span>
            </button>

            <button
                class="recent-location"
                type="button"
                data-query="Weather in Delhi"
            >
                <span class="location-icon">⌖</span>
                <span>Delhi, India</span>
            </button>
        `;
    } else {
        recentList.innerHTML = searches
            .map(
                search => `
                    <button
                        class="recent-location"
                        type="button"
                        data-query="${escapeHTML(search)}"
                    >
                        <span class="location-icon">⌖</span>
                        <span>${escapeHTML(search)}</span>
                    </button>
                `
            )
            .join("");
    }

    attachRecentSearchEvents();
}


function attachRecentSearchEvents() {
    const recentButtons =
        document.querySelectorAll(
            ".recent-location"
        );

    recentButtons.forEach(button => {
        button.addEventListener(
            "click",
            function () {
                const query =
                    button.dataset.query ||
                    button.innerText.trim();

                input.value = query;

                handleQuery();
            }
        );
    });
}


/* =========================
   RESET CHAT
========================= */

function resetChat(name) {
    const displayName =
        name ||
        getSavedUser()?.name ||
        "there";

    chatContainer.innerHTML = `
        <article class="welcome-card">

            <div class="welcome-icon">✦</div>

            <div>
                <h1>Hello, ${escapeHTML(displayName)}.</h1>

                <p>
                    Ask for current weather,
                    forecasts, rainfall risk,
                    storm alerts, or travel
                    conditions.

                    <strong>
                        Start with a city or region.
                    </strong>
                </p>
            </div>

        </article>
    `;

    input.value = "";
}


/* =========================
   VOICE SUPPORT
========================= */
/*
   Browser Speech Recognition

   Chrome usually provides:
   window.SpeechRecognition
   or
   window.webkitSpeechRecognition
*/
const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;
let recognition = null;
let isListening = false;
/* =========================
   CREATE SPEECH RECOGNITION
========================= */
if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    // Only one sentence/request at a time
    recognition.continuous = false;
    // We only need the final transcript
    recognition.interimResults = false;
    // Indian English
    recognition.lang = "en-IN";
    recognition.onstart = function () {
        isListening = true;
        if (voiceButton) {
            voiceButton.classList.add(
                "listening"
            );
            voiceButton.setAttribute(
                "aria-label",
                "Stop listening"
            );
            voiceButton.title =
                "Listening...";
        }
    };
    recognition.onresult = function (event) {
        const transcript =
            event.results[0][0].transcript.trim();
        if (
            input &&
            transcript
        ) {
            // Put speech into the normal
            // chat input
            input.value = transcript;
            // Use the existing chat function
            handleQuery();
        }
    };
    recognition.onerror = function (event) {
        console.error(
            "Speech recognition error:",
            event.error
        );
        if (
            event.error ===
            "not-allowed"
        ) {
            appendBotMessage(
                "Microphone access was denied. Please allow microphone access in your browser."
            );
        } else if (
            event.error ===
            "no-speech"
        ) {
            console.log(
                "No speech detected."
            );
        } else if (
            event.error ===
            "audio-capture"
        ) {
            appendBotMessage(
                "No microphone was detected. Please check your microphone and try again."
            );
        }
    };
    recognition.onend = function () {
        isListening = false;
        if (voiceButton) {
            voiceButton.classList.remove(
                "listening"
            );
            voiceButton.setAttribute(
                "aria-label",
                "Start voice input"
            );
            voiceButton.title =
                "Voice input";
        }
    };
}
/* =========================
   START / STOP VOICE INPUT
========================= */
function startVoiceInput() {
    if (!recognition) {
        appendBotMessage(
            "Voice input is not supported by this browser. Please use Google Chrome."
        );
        return;
    }
    if (isListening) {
        recognition.stop();
        return;
    }
    try {
        recognition.start();
    } catch (error) {
        console.error(
            "Unable to start speech recognition:",
            error
        );
    }
}
/* =========================
   TEXT TO SPEECH
========================= */
function speakReply(text) {

    if (!("speechSynthesis" in window)) {
        console.warn("Speech synthesis is not supported.");
        return;
    }

    // Stop anything currently speaking
    window.speechSynthesis.cancel();

    if (!text || !text.trim()) {
        return;
    }

    const utterance = new SpeechSynthesisUtterance(
        text.replace(/\n+/g, ". ")
    );

    utterance.rate = 1;
    utterance.pitch = 1;
    utterance.volume = 1;

    // Detect language
    utterance.lang = detectSpeechLanguage(text);

    utterance.onstart = function () {

        isSpeaking = true;

        if (stopVoiceButton) {
            stopVoiceButton.style.display = "flex";
        }
    };

    utterance.onend = function () {

        isSpeaking = false;

        if (stopVoiceButton) {
            stopVoiceButton.style.display = "none";
        }
    };

    utterance.onerror = function (event) {

        console.error(
            "Speech synthesis error:",
            event
        );

        isSpeaking = false;

        if (stopVoiceButton) {
            stopVoiceButton.style.display = "none";
        }
    };

    window.speechSynthesis.speak(
        utterance
    );
}
function stopSpeaking() {

    if (!("speechSynthesis" in window)) {
        return;
    }

    window.speechSynthesis.cancel();

    isSpeaking = false;

    if (stopVoiceButton) {
        stopVoiceButton.style.display = "none";
    }
}
/* =========================
   SPEECH LANGUAGE DETECTION
========================= */
function detectSpeechLanguage(text) {
    /*Hindi / Devanagari*/
    if (
        /[\u0900-\u097F]/.test(text)
    ) {
        return "hi-IN";
    }
    /*
       Bengali / Assamese script

       Both use the Bengali-Assamese
       Unicode block, so the browser
       may select a Bengali voice.
    */
    if (
        /[\u0980-\u09FF]/.test(text)
    ) {
        return "bn-IN";
    }
    /*Default*/
    return "en-IN";
}
function getAuthToken() {
    return localStorage.getItem(TOKEN_STORAGE_KEY);
}
async function loadConversations() {
    const token = getAuthToken();

    if (!token) {
        return;
    }

    try {
        const response = await fetch(
            `${API_BASE_URL}/conversations/`,
            {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        if (!response.ok) {
            if (response.status === 401) {
                handleLogout();
            }
            return;
        }

        const conversations = await response.json();

        renderConversations(conversations);

    } catch (error) {
        console.error("Failed to load conversations:", error);
    }
}
function renderConversations(conversations) {
    if (!recentList) return;

    recentList.innerHTML = "";

    if (!conversations.length) {
        const emptyMessage = document.createElement("div");

        emptyMessage.className = "recent-empty";
        emptyMessage.textContent = "No conversations yet.";

        recentList.appendChild(emptyMessage);
        return;
    }

    conversations.forEach(conversation => {
        const button = document.createElement("button");

        button.type = "button";
        button.className = "recent-location";

        if (conversation.id === currentConversationId) {
            button.classList.add("active");
        }

        button.dataset.conversationId = conversation.id;

        const icon = document.createElement("span");
        icon.className = "location-icon";
        icon.textContent = "◌";

        const title = document.createElement("span");
        title.textContent = conversation.title;

        button.appendChild(icon);
        button.appendChild(title);

        button.addEventListener("click", () => {
            loadConversation(conversation.id);
        });

        recentList.appendChild(button);
    });
}
async function loadConversation(conversationId) {
    const token = getAuthToken();

    if (!token) {
        return;
    }

    try {
        const response = await fetch(
            `${API_BASE_URL}/conversations/${conversationId}`,
            {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        if (!response.ok) {
            throw new Error("Could not load conversation.");
        }

        const conversation = await response.json();

        currentConversationId = conversation.id;

        chatContainer.innerHTML = "";

        conversation.messages.forEach(message => {
            if (message.role === "user") {
                appendUserMessage(message.content);
            } else if (message.role === "assistant") {
                appendBotMessage(message.content);
                updateDailyInsights(message.content);
            }
        });

        await loadConversations();

        chatContainer.scrollTop = chatContainer.scrollHeight;

    } catch (error) {
        console.error("Conversation loading error:", error);

        appendBotMessage(
            "Unable to load this conversation."
        );
    }
}
/* =========================
   MAIN CHAT FUNCTION
========================= */
async function handleQuery() {
    const query =
        input.value.trim();
    if (!query) {
        return;
    }
    appendUserMessage(query);
    saveRecentSearch(query);
    input.value = "";
    const thinkingMessage =
        showThinkingMessage();
    try {
        const requestBody = {
            message: query
        };
        
        if (currentConversationId !== null) {
            requestBody.conversation_id = currentConversationId;
        }
        
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${getAuthToken()}`
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            throw new Error("Server returned an error.");
        }
        
        const data = await response.json();
        
        if (data.conversation_id) {
            currentConversationId = data.conversation_id;
        }
        const reply =
            data.reply ||
            "WeatherGPT did not return a reply.";
        removeThinkingMessage(
            thinkingMessage
        );
        appendBotMessage(
            reply
        );
        await loadConversations();
        updateDailyInsights(
            reply
        );
        /*
           Read the response aloud
           when voice support is available.
        */
        speakReply(reply);
    } catch (error) {
        removeThinkingMessage(
            thinkingMessage
        );
        appendBotMessage(
            "Unable to connect to WeatherGPT.\n\n" +
            "Please make sure the FastAPI backend is running at " +
            "http://127.0.0.1:8000."
        );
        console.error(error);
    }
}
/* =========================
   EVENT LISTENERS
========================= */
/* Login */
if (loginForm) {
    loginForm.addEventListener(
        "submit",
        handleLogin
    );
}
/* Logout */
if (logoutButton) {
    logoutButton.addEventListener(
        "click",
        handleLogout
    );
}
if (mobileLogoutButton) {
    mobileLogoutButton.addEventListener(
        "click",
        handleLogout
    );
}
/* Send button */
if (sendButton) {
    sendButton.addEventListener(
        "click",
        handleQuery
    );
}
/* Voice button */
if (voiceButton) {
    voiceButton.addEventListener(
        "click",
        startVoiceInput
    );
}
/* Enter key */
if (input) {
    input.addEventListener(
        "keydown",
        function (event) {
            if (
                event.key ===
                "Enter"
            ) {
                handleQuery();
            }
        }
    );
}
/* New forecast */
newForecastButton.addEventListener("click", () => {
    currentConversationId = null;
    resetChat();
    loadConversations();
    input.focus();
});
if (stopVoiceButton) {
    stopVoiceButton.addEventListener(
        "click",
        stopSpeaking
    );
}
/* INITIALIZATION*/
renderRecentSearches();
updateDailyInsights("");
async function restoreSession() {
    const token = getAuthToken();

    if (!token) {
        showLoginScreen();
        return;
    }

    try {
        const response = await fetch(
            `${API_BASE_URL}/auth/me`,
            {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        if (!response.ok) {
            throw new Error("Session expired");
        }

        const user = await response.json();

        localStorage.setItem(
            USER_STORAGE_KEY,
            JSON.stringify(user)
        );

        showAppForUser(user);

        await loadConversations();

    } catch (error) {
        console.error("Session restore failed:", error);

        localStorage.removeItem(TOKEN_STORAGE_KEY);
        localStorage.removeItem(USER_STORAGE_KEY);

        showLoginScreen();
    }
}

restoreSession();