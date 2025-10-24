// Credit: https://emma-delaney.medium.com/how-to-create-your-own-chatgpt-in-html-css-and-javascript-78e32b70b4be
// Modified and optimized by JDP and ChatGPT

const chatInput = document.querySelector("#chat-input");
const sendButton = document.querySelector("#send-btn");
const chatContainer = document.querySelector(".chat-container");
const themeButton = document.querySelector("#theme-btn");
const deleteButton = document.querySelector("#delete-btn");
const micButton = document.querySelector("#mic-btn");

let sessionID = "";
let userText = null;
const initialInputHeight = chatInput.scrollHeight;

const defaultText = `<div class="default-text">
                        <h1>Ask LISA</h1>
                        <p>I'm LISA, your Language-Integrated Stock Analyst.<br />How can I help you today?</p>
                    </div>`;

const init = () => {
    sessionID = "";
    const themeColor = localStorage.getItem("themeColor");
    document.body.classList.toggle("light-mode", themeColor === "light_mode");
    themeButton.innerText = document.body.classList.contains("light-mode") ? "dark_mode" : "light_mode";
    chatContainer.innerHTML = defaultText;
    chatContainer.scrollTo(0, chatContainer.scrollHeight);
};

const createChatElement = (content, className) => {
    const chatDiv = document.createElement("div");
    chatDiv.classList.add("chat", className);
    chatDiv.innerHTML = content;
    return chatDiv;
};

const streamChatResponse = async (incomingChatDiv) => {
    const divElement = document.createElement("div");
    divElement.classList.add("markdown-output");
    const chatDetails = incomingChatDiv.querySelector(".chat-details");
    chatDetails.appendChild(divElement);

    const fileName = `${crypto.randomUUID()}.png`
    let accumulatedText = "";

    try {
        let url = `/streaming_chat?input=${userText}&file_name=${fileName}`;

        let response = await fetch(url, {
            headers: { "X-Session-ID": sessionID }
        });

        sessionID = response.headers.get("X-Session-ID");
        incomingChatDiv.querySelector(".typing-animation")?.remove();

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
 
            // Parse and render markdown incrementally
            accumulatedText += decoder.decode(value, { stream: true });
            divElement.innerHTML = marked.parse(accumulatedText);
            chatContainer.scrollIntoView({ behavior: "smooth", block: "end" });
        }

        // If a chart was generated, fetch it and display it
        url = `/get_image?file_name=${fileName}`;
        response = await fetch(url, { headers: { "X-Session-ID": sessionID }});
        src = await response.text();

        if (src.length > 0) {
            let imgElement = document.createElement("img");
            imgElement.src = src;
            imgElement.setAttribute("class", "chart");
            imgElement.setAttribute("alt", "ai-generated chart")
            divElement.parentNode.parentNode.appendChild(imgElement);
            chatContainer.scrollIntoView({ behavior: "smooth", block: "end" });
        }
    }
    catch (error) {
        console.error(error);
        incomingChatDiv.querySelector(".typing-animation")?.remove();

        const errorMessage = accumulatedText.length === 0
            ? `I'm sorry, but something went wrong (${error.message}).`
            : `...I'm sorry, but something went wrong (${error.message}).`;

        accumulatedText += errorMessage;
        divElement.innerHTML = marked.parse(accumulatedText);
    }
};

const showTypingAnimation = () => {
    const html = `<div class="chat-content">
                    <div class="chat-details">
                        <img src="/static/chatbot.jpg" class="avatar" alt="chatbot-img">
                        <div class="typing-animation">
                            <div class="typing-dot" style="--delay: 0.2s"></div>
                            <div class="typing-dot" style="--delay: 0.3s"></div>
                            <div class="typing-dot" style="--delay: 0.4s"></div>
                        </div>
                    </div>
                </div>`;

    const incomingChatDiv = createChatElement(html, "incoming");
    chatContainer.append(incomingChatDiv);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);
    streamChatResponse(incomingChatDiv);
};

const handleOutgoingChat = () => {
    userText = chatInput.value.trim();
    if (!userText) return;

    chatInput.value = "";
    chatInput.style.height = `${initialInputHeight}px`;

    const html = `<div class="chat-content">
                    <div class="chat-details">
                        <img src="/static/user.jpg" class="avatar" alt="user-img">
                        <div class="markdown-output">
                            <p>${userText}</p>
                        </div>
                    </div>
                </div>`;

    const outgoingChatDiv = createChatElement(html, "outgoing");
    chatContainer.querySelector(".default-text")?.remove();
    chatContainer.append(outgoingChatDiv);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);
    setTimeout(showTypingAnimation, 500);
};

deleteButton.addEventListener("click", () => {
    if (confirm("Are you sure you want to delete the conversation?")) {
        init();
    }
});

themeButton.addEventListener("click", () => {
    const isLight = document.body.classList.toggle("light-mode");
    localStorage.setItem("themeColor", isLight ? "light_mode" : "dark_mode");
    themeButton.innerText = isLight ? "dark_mode" : "light_mode";
});

chatInput.addEventListener("input", () => {
    chatInput.style.height = `${initialInputHeight}px`;
    chatInput.style.height = `${chatInput.scrollHeight}px`;
});

chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
        e.preventDefault();
        handleOutgoingChat();
    }
});

async function typewriter(text, el, delay = 5) {
    for (let i = 0; i < text.length; i++) {
        await new Promise(resolve => setTimeout(resolve, delay));
        el.value += text[i];
        el.style.height = `${initialInputHeight}px`;
        el.style.height = `${el.scrollHeight}px`;
    }
}

micButton.addEventListener("click", () => {
    chatInput.value = "";

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        console.log("Speech recognition is not supported in this browser.");
        micButton.style.display = 'none';
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.interimResults = false;

    recognition.addEventListener("result", async (e) => {
        const query = Array.from(e.results)
            .map(result => result[0].transcript)
            .join('');
        await typewriter(query, chatInput);
        handleOutgoingChat();
    });

    recognition.start();
});

init();
sendButton.addEventListener("click", handleOutgoingChat);
