const form = document.getElementById("chat-form");
const input = document.getElementById("message-input");
const messages = document.getElementById("messages");
const sendButton = document.getElementById("send-button");
const newChatButton = document.getElementById("new-chat");

let threadId = localStorage.getItem("thread_id");


// ================= MESSAGE UI =================

function addMessage(role, content, sources = []) {

    const welcome = document.querySelector(".welcome");

    if (welcome) {
        welcome.remove();
    }

    const message = document.createElement("div");

    message.className = `message ${role}`;

    const avatar = document.createElement("div");

    avatar.className = "message-avatar";

    avatar.textContent =
        role === "user" ? "U" : "AI";


    const body = document.createElement("div");

    body.className = "message-content";

     // Markdown pour l'assistant
    if (role === "assistant") {
        body.innerHTML = DOMPurify.sanitize(
            marked.parse(content)
        );
    } else {
        body.textContent = content;
    }


    message.appendChild(avatar);
    message.appendChild(body);


    // Sources
    if (sources && sources.length > 0) {

        const sourcesContainer =
            document.createElement("div");

        sourcesContainer.className = "sources";

        sources.forEach(source => {

            const badge =
                document.createElement("span");

            badge.className = "source";

            badge.textContent =
                `${source.source || "Document"}`
                + (source.page
                    ? ` · p.${source.page}`
                    : "");

            sourcesContainer.appendChild(badge);
        });

        body.appendChild(sourcesContainer);
    }


    messages.appendChild(message);

    messages.scrollTop = messages.scrollHeight;
}


// ================= LOADING =================

function showLoading() {

    const message = document.createElement("div");

    message.id = "loading";

    message.className = "message assistant";

    message.innerHTML = `
        <div class="message-avatar">AI</div>

        <div class="message-content">
            <div class="typing">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;

    messages.appendChild(message);

    messages.scrollTop = messages.scrollHeight;
}


function removeLoading() {

    const loading =
        document.getElementById("loading");

    if (loading) {
        loading.remove();
    }
}


// ================= CHAT =================

form.addEventListener("submit", async (event) => {

    event.preventDefault();

    const message = input.value.trim();

    if (!message) {
        return;
    }


    // Afficher le message utilisateur
    addMessage("user", message);

    input.value = "";

    sendButton.disabled = true;

    showLoading();


    try {

        const payload = {
            message: message,
            thread_id: threadId
        };

        console.log("SENDING:", payload);

        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        console.log("STATUS:", response.status);
        console.log("RESPONSE:", JSON.stringify(data, null, 2));
        console.log("DETAIL:", data.detail);



        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );
        }




        // Sauvegarde du thread
        threadId = data.thread_id;

        localStorage.setItem(
            "thread_id",
            threadId
        );


        removeLoading();


        addMessage(
            "assistant",
            data.response,
            data.sources
        );


    } catch (error) {

        removeLoading();

        addMessage(
            "assistant",
            "Une erreur est survenue. Veuillez réessayer."
        );

        console.error(error);

    } finally {

        sendButton.disabled = false;

        input.focus();
    }

});


// ================= NEW CHAT =================

newChatButton.addEventListener("click", () => {

    threadId = null;

    localStorage.removeItem("thread_id");

    messages.innerHTML = `
        <div class="welcome">

            <div class="welcome-icon">
                ✦
            </div>

            <h2>
                Comment puis-je vous aider ?
            </h2>

            <p>
                Posez votre question et l'assistant
                vous répondra à partir des connaissances disponibles.
            </p>

        </div>
    `;

    input.focus();
});


// ================= ENTER =================

input.addEventListener("keydown", (event) => {

    if (
        event.key === "Enter" &&
        !event.shiftKey
    ) {

        event.preventDefault();

        form.requestSubmit();
    }

});