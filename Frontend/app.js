const loginScreen = document.getElementById("login-screen");
const loginForm = document.getElementById("login-form");
const loginNameInput = document.getElementById("login-name");
const loginEmailInput = document.getElementById("login-email");
const sidebarUserName = document.getElementById("sidebar-user-name");
const logoutButton = document.getElementById("logout-button");
const mobileLogoutButton = document.getElementById("mobile-logout-button");

const input = document.querySelector(".input-wrapper input");
const sendButton = document.querySelector(".send-button");
const chatContainer = document.querySelector(".chat-container");
const recentList = document.querySelector(".recent-list");
const newForecastButton = document.querySelector(".new-forecast");
const aqiValue = document.getElementById("aqi-value");
const aqiStatus = document.getElementById("aqi-status");
const uvValue = document.getElementById("uv-value");
const uvStatus = document.getElementById("uv-status");
const sunriseTime = document.getElementById("sunrise-time");
const sunsetTime = document.getElementById("sunset-time");

const API_URL = "http://127.0.0.1:8000/chat/";
const USER_STORAGE_KEY = "weathergpt_user";
const RECENT_STORAGE_KEY = "weathergpt_recent_searches";

function escapeHTML(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

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
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
}

function showAppForUser(user) {
    if (loginScreen) {
        loginScreen.classList.add("hidden");
    }

    if (sidebarUserName) {
        sidebarUserName.textContent = user.name;
    }

    resetChat(user.name);
    input.focus();
}

function showLoginScreen() {
    if (loginScreen) {
        loginScreen.classList.remove("hidden");
    }

    if (loginNameInput) {
        loginNameInput.focus();
    }
}

function handleLogin(event) {
    event.preventDefault();

    const name = loginNameInput.value.trim();
    const email = loginEmailInput.value.trim();

    if (!name || !email) {
        return;
    }

    const user = {
        name,
        email
    };

    saveUser(user);
    showAppForUser(user);
}

function handleLogout() {
    localStorage.removeItem(USER_STORAGE_KEY);
    localStorage.removeItem(RECENT_STORAGE_KEY);

    resetChat();
    renderRecentSearches();
    showLoginScreen();
}

function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
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

function extractNumberAfterLabel(text, label) {
    const pattern = new RegExp(`${label}\\s*:?\\s*([0-9]+(?:\\.[0-9]+)?)`, "i");
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
    const humidity = extractNumberAfterLabel(reply, "Humidity");
    const windSpeed = extractNumberAfterLabel(reply, "Wind Speed");
    const temperature = extractNumberAfterLabel(reply, "Temperature");

    let estimatedAqi = 42;
    let estimatedUv = 5;

    if (condition.includes("rain") || condition.includes("thunderstorm")) {
        estimatedAqi = 35;
        estimatedUv = 2;
    }

    if (humidity !== null && humidity >= 85) {
        estimatedAqi += 8;
        estimatedUv = Math.max(1, estimatedUv - 1);
    }

    if (windSpeed !== null && windSpeed >= 25) {
        estimatedAqi = Math.max(25, estimatedAqi - 6);
    }

    if (temperature !== null && temperature >= 34) {
        estimatedUv = Math.min(9, estimatedUv + 2);
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
        aqiStatus.textContent = getInsightStatus(insights.aqi, "aqi");
        aqiStatus.className = insights.aqi <= 50
            ? "insight-status status-good"
            : "insight-status status-mod";
    }

    if (uvValue) {
        uvValue.textContent = insights.uv;
    }

    if (uvStatus) {
        uvStatus.textContent = getInsightStatus(insights.uv, "uv");
        uvStatus.className = insights.uv <= 2
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

function getRecentSearches() {
    const searches = localStorage.getItem(RECENT_STORAGE_KEY);

    if (!searches) {
        return [];
    }

    try {
        return JSON.parse(searches);
    } catch (error) {
        localStorage.removeItem(RECENT_STORAGE_KEY);
        return [];
    }
}

function saveRecentSearch(query) {
    let searches = getRecentSearches();

    searches = searches.filter(item => item.toLowerCase() !== query.toLowerCase());
    searches.unshift(query);
    searches = searches.slice(0, 5);

    localStorage.setItem(RECENT_STORAGE_KEY, JSON.stringify(searches));
    renderRecentSearches();
}

function renderRecentSearches() {
    if (!recentList) {
        return;
    }

    const searches = getRecentSearches();

    if (searches.length === 0) {
        recentList.innerHTML = `
            <button class="recent-location" type="button" data-query="Weather in Guwahati">
                <span class="location-icon">⌖</span>
                <span>Guwahati, India</span>
            </button>

            <button class="recent-location" type="button" data-query="Weather in Mumbai">
                <span class="location-icon">⌖</span>
                <span>Mumbai, India</span>
            </button>

            <button class="recent-location" type="button" data-query="Weather in Delhi">
                <span class="location-icon">⌖</span>
                <span>Delhi, India</span>
            </button>
        `;
    } else {
        recentList.innerHTML = searches.map(search => `
            <button class="recent-location" type="button" data-query="${escapeHTML(search)}">
                <span class="location-icon">⌖</span>
                <span>${escapeHTML(search)}</span>
            </button>
        `).join("");
    }

    attachRecentSearchEvents();
}

function attachRecentSearchEvents() {
    const recentButtons = document.querySelectorAll(".recent-location");

    recentButtons.forEach(button => {
        button.addEventListener("click", function () {
            const query = button.dataset.query || button.innerText.trim();
            input.value = query;
            handleQuery();
        });
    });
}

function resetChat(name) {
    const displayName = name || getSavedUser()?.name || "there";

    chatContainer.innerHTML = `
        <article class="welcome-card">
            <div class="welcome-icon">✦</div>

            <div>
                <h1>Hello, ${escapeHTML(displayName)}.</h1>
                <p>
                    Ask for current weather, forecasts, rainfall risk, storm alerts,
                    or travel conditions. <strong>Start with a city or region.</strong>
                </p>
            </div>
        </article>
    `;

    input.value = "";
}

async function handleQuery() {
    const query = input.value.trim();

    if (!query) {
        return;
    }

    appendUserMessage(query);
    saveRecentSearch(query);

    input.value = "";

    const thinkingMessage = showThinkingMessage();

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: query
            })
        });

        if (!response.ok) {
            throw new Error("Server returned an error.");
        }

        const data = await response.json();
        const reply = data.reply || "WeatherGPT did not return a reply.";

        removeThinkingMessage(thinkingMessage);
        appendBotMessage(reply);
        updateDailyInsights(reply);
    } catch (error) {
        removeThinkingMessage(thinkingMessage);

        appendBotMessage(
            "Unable to connect to WeatherGPT.\n\nPlease make sure the FastAPI backend is running at http://127.0.0.1:8000."
        );

        console.error(error);
    }
}

if (loginForm) {
    loginForm.addEventListener("submit", handleLogin);
}

if (logoutButton) {
    logoutButton.addEventListener("click", handleLogout);
}

if (mobileLogoutButton) {
    mobileLogoutButton.addEventListener("click", handleLogout);
}

if (sendButton) {
    sendButton.addEventListener("click", handleQuery);
}

if (input) {
    input.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            handleQuery();
        }
    });
}

if (newForecastButton) {
    newForecastButton.addEventListener("click", function () {
        resetChat();
        input.focus();
    });
}

renderRecentSearches();
updateDailyInsights("");

const savedUser = getSavedUser();

if (savedUser) {
    showAppForUser(savedUser);
} else {
    showLoginScreen();
}
