const form = document.getElementById("chat-form");
const input = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const newChatButton = document.getElementById("new-chat-button");
const themeToggle = document.getElementById("theme-toggle");
const themeIcon = document.getElementById("theme-icon");
const messages = document.getElementById("messages");
const welcome = document.getElementById("welcome");
const typingIndicator = document.getElementById("typing-indicator");
const statusText = document.getElementById("status");

const CONVERSATION_KEY = "contextmate-conversation-id";
const THEME_KEY = "contextmate-theme";

let conversationId = getOrCreateConversationId();
let isSending = false;

function getOrCreateConversationId() {
    let id = localStorage.getItem(CONVERSATION_KEY);

    if (!id) {
        id = crypto.randomUUID();
        localStorage.setItem(CONVERSATION_KEY, id);
    }

    return id;
}

function applyTheme(theme) {
    const selectedTheme = theme === "light" ? "light" : "dark";

    document.documentElement.dataset.theme = selectedTheme;
    themeIcon.textContent = selectedTheme === "dark" ? "☀" : "☾";
    themeToggle.setAttribute(
        "aria-label",
        selectedTheme === "dark"
            ? "Switch to light mode"
            : "Switch to dark mode"
    );

    localStorage.setItem(THEME_KEY, selectedTheme);
}

applyTheme(localStorage.getItem(THEME_KEY) || "dark");

themeToggle.addEventListener("click", () => {
    const nextTheme =
        document.documentElement.dataset.theme === "dark"
            ? "light"
            : "dark";

    applyTheme(nextTheme);
});

function setStatus(message, isError = false) {
    statusText.textContent = message;
    statusText.classList.toggle("error", isError);
}

function updateWelcome() {
    welcome.hidden = messages.children.length > 0;
}

function formatTime(date = new Date()) {
    return date.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
    });
}

function addMessage(role, content, timestamp = new Date()) {
    const isUser = role === "user";

    const row = document.createElement("article");
    row.className = `message-row ${isUser ? "user" : "assistant"}`;

    const avatar = document.createElement("span");
    avatar.className = isUser ? "user-avatar" : "assistant-avatar";
    avatar.textContent = isUser ? "●" : "✦";
    avatar.setAttribute("aria-hidden", "true");

    const contentColumn = document.createElement("div");
    contentColumn.className = "message-content";

    const meta = document.createElement("div");
    meta.className = "message-meta";

    const sender = document.createElement("strong");
    sender.textContent = isUser ? "You" : "ContextMate";

    const time = document.createElement("time");
    time.textContent = formatTime(timestamp);
    time.dateTime = timestamp.toISOString();

    meta.append(sender, time);

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";

    // textContent prevents model output from being interpreted as HTML.
    bubble.textContent = content;

    contentColumn.append(meta, bubble);

    if (!isUser) {
        const tools = document.createElement("div");
        tools.className = "message-tools";

        const copyButton = document.createElement("button");
        copyButton.className = "copy-button";
        copyButton.type = "button";
        copyButton.textContent = "Copy response";

        copyButton.addEventListener("click", async () => {
            try {
                await navigator.clipboard.writeText(content);
                copyButton.textContent = "Copied!";
                setTimeout(() => {
                    copyButton.textContent = "Copy response";
                }, 1400);
            } catch {
                setStatus(
                    "Copying is unavailable in this browser context.",
                    true
                );
            }
        });

        tools.append(copyButton);
        contentColumn.append(tools);
    }

    row.append(avatar, contentColumn);
    messages.append(row);

    updateWelcome();
    scrollToLatest();
}


function scrollToLatest() {
    window.requestAnimationFrame(() => {
        messages.scrollTo({
            top: messages.scrollHeight,
            behavior: "smooth",
        });
    });
}


function setBusy(busy) {
    isSending = busy;
    sendButton.disabled = busy;
    input.disabled = busy;
    typingIndicator.hidden = !busy;

    if (busy) {
        setStatus("ContextMate is thinking...");
    } else {
        setStatus(
            "Responses may occasionally be inaccurate. Verify important information."
        );
        input.focus();
    }
}

async function sendMessage(message) {
    const cleanMessage = message.trim();

    if (!cleanMessage || isSending) {
        return;
    }

    addMessage("user", cleanMessage);
    input.value = "";
    input.style.height = "auto";

    setBusy(true);

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                conversation_id: conversationId,
                message: cleanMessage,
            }),
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(
                data.detail || `Request failed (${response.status}).`
            );
        }

        addMessage("assistant", data.response);
    } catch (error) {
        setStatus(
            error.message ||
                "Unable to connect. Check the server and try again.",
            true
        );
    } finally {
        setBusy(false);
    }
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    await sendMessage(input.value);
});

input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        form.requestSubmit();
    }
});

input.addEventListener("input", () => {
    input.style.height = "auto";
    input.style.height = `${Math.min(input.scrollHeight, 180)}px`;
});

document.querySelectorAll("[data-prompt]").forEach((button) => {
    button.addEventListener("click", () => {
        input.value = button.dataset.prompt;
        input.focus();
        input.style.height = "auto";
        input.style.height = `${Math.min(input.scrollHeight, 180)}px`;
    });
});

newChatButton.addEventListener("click", async () => {
    if (isSending) {
        return;
    }

    const oldConversationId = conversationId;

    conversationId = crypto.randomUUID();
    localStorage.setItem(CONVERSATION_KEY, conversationId);

    messages.replaceChildren();
    updateWelcome();
    input.value = "";
    input.style.height = "auto";
    setStatus("Started a new conversation.");

    // Remove the old chat from the database as well.
    // If deletion fails, the new chat still works.
    try {
        await fetch(
            `/conversations/${encodeURIComponent(oldConversationId)}`,
            { method: "DELETE" }
        );
    } catch (error) {
        console.warn("Could not delete the previous conversation.", error);
    }

    input.focus();
});

async function restoreConversation() {
    try {
        const response = await fetch(
            `/conversations/${encodeURIComponent(conversationId)}`
        );

        if (!response.ok) {
            return;
        }

        const data = await response.json();

        for (const message of data.messages || []) {
            addMessage(message.role, message.content);
        }
    } catch (error) {
        console.warn("Conversation history could not be restored.", error);
    }

    updateWelcome();
}

restoreConversation();