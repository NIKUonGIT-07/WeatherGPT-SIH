const input = document.querySelector(".input-wrapper input");
const sendButton = document.querySelector(".send-button");
const chatContainer = document.querySelector(".chat-container");
const recentList = document.querySelector(".recent-list");
const newForecastButton = document.querySelector(".new-forecast");

const API_URL = "http://127.0.0.1:8000/chat/";

function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function escapeHTML(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
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

function getRecentSearches() {
    return JSON.parse(localStorage.getItem("weathergpt_recent_searches")) || [];
}

function saveRecentSearch(query) {
    let searches = getRecentSearches();

    searches = searches.filter(item => item.toLowerCase() !== query.toLowerCase());
    searches.unshift(query);

    searches = searches.slice(0, 5);

    localStorage.setItem("weathergpt_recent_searches", JSON.stringify(searches));

    renderRecentSearches();
}

function renderRecentSearches() {
    if (!recentList) return;

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

function resetChat() {
    chatContainer.innerHTML = `
        <article class="welcome-card">
            <div class="welcome-icon">✦</div>

            <div>
                <h1>Hello, I am WeatherGPT.</h1>
                <p>
                    Ask for current weather, forecasts, rainfall risk, storm alerts,
                    or travel conditions. <strong>Start with a city or region.</strong>
                </p>
            </div>
        </article>
    `;

    input.value = "";
    input.focus();
}

async function handleQuery() {
    const query = input.value.trim();

    if (!query) return;

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

        removeThinkingMessage(thinkingMessage);
        appendBotMessage(data.reply || "WeatherGPT did not return a reply.");

    } catch (error) {
        removeThinkingMessage(thinkingMessage);

        appendBotMessage(
            "Unable to connect to WeatherGPT.\n\nPlease make sure the FastAPI backend is running at http://127.0.0.1:8000."
        );

        console.error(error);
    }
}

sendButton.addEventListener("click", handleQuery);

input.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        handleQuery();
    }
});

if (newForecastButton) {
    newForecastButton.addEventListener("click", resetChat);
}

renderRecentSearches();