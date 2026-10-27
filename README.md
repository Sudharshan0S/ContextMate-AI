
# ✦ ContextMate AI

### A Context-Aware Conversational AI Assistant

ContextMate AI is a conversational chatbot powered by Google's Gemini API, built with FastAPI and a responsive web interface. It maintains conversation history, uses relevant previous messages to answer follow-up questions, and manages the context supplied to the language model.

The application provides a modern chat experience with dark and light themes, persistent conversation storage, and backend API endpoints for interacting with the assistant.

---

## ✨ Features

- **Gemini AI Integration:** Generates responses using Google's Gemini API.
- **Conversational Memory:** Uses previous messages to answer follow-up questions within a conversation.
- **Context Window Management:** Limits the conversation history sent to the model to manage context size.
- **Persistent Storage:** Stores conversation messages using SQLite.
- **Modern Chat Interface:** Responsive frontend built with HTML, CSS, and JavaScript.
- **Dark and Light Themes:** Switch themes and retain the selected preference across page reloads.
- **Conversation Management:** Start a new conversation and retrieve or delete conversation history.
- **REST API:** Backend endpoints implemented using FastAPI.
- **Error Handling:** Handles API failures and retries selected temporary Gemini errors.
- **Environment-Based Configuration:** Keeps API credentials outside the source code.
- **API Documentation:** Interactive API documentation through Swagger UI.

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| AI Model API | Google Gemini API |
| AI SDK | Google Gen AI SDK |
| Frontend | HTML, CSS, JavaScript |
| Database | SQLite |
| Data Validation | Pydantic |
| Configuration | Python dotenv |
| API Server | Uvicorn |
| Version Control | Git and GitHub |

---

## 🏗️ Project Architecture

```text
contextmate-ai/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── conversation.py
│   └── llm.py
│
├── static/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── tests/
│   ├── __init__.py
│   └── test_chat.py
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── contextmate.db
```

**Note:** The database file is generated locally when the application initializes. It should not be committed to the repository. The `tests/` directory is intended for automated tests.

---

## ⚙️ How It Works

1. The user submits a message through the web interface.
2. The frontend sends the message and conversation ID to the FastAPI backend.
3. The backend retrieves the relevant conversation history from SQLite.
4. The context manager selects recent messages for the current request.
5. The Gemini API generates a response using the system instructions and supplied conversation context.
6. The backend saves the successful user-assistant exchange to SQLite.
7. The frontend displays the response.

### Context Management

ContextMate AI separates persistent conversation storage from the context sent to Gemini.

- **Persistent history:** Stores conversation messages in SQLite.
- **Recent context:** Selects a limited number of recent messages for model input.
- **System instructions:** Defines the assistant's role and response behavior.
- **Conversation isolation:** Uses a separate conversation ID to distinguish different chats.

This approach helps manage the context supplied to the model while retaining conversation history for later retrieval.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or later
- A Google Gemini API key
- Git
- Internet connectivity for Gemini API requests

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/contextmate-ai.git
cd contextmate-ai
```

Replace `YOUR_USERNAME` with your GitHub username and use the actual repository URL.

### 2. Create a Virtual Environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_verified_gemini_model
```

Replace the placeholder values with your actual API key and the Gemini model you have verified.

**Security:** Never upload `.env` or expose your API key in source code, screenshots, logs, or public repositories.

### 5. Start the Application

```bash
uvicorn app.main:app --reload
```

### 6. Open ContextMate AI

| Resource | URL |
|---|---|
| Web Application | http://127.0.0.1:8000 |
| Interactive API Documentation | http://127.0.0.1:8000/docs |
| API Health Check | http://127.0.0.1:8000/health |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Serves the chatbot frontend |
| GET | `/health` | Returns application health information |
| POST | `/chat` | Sends a message and generates a response |
| GET | `/conversations/{conversation_id}` | Retrieves conversation history |
| DELETE | `/conversations/{conversation_id}` | Deletes a conversation's stored messages |

### Example: Chat Request

**POST `/chat`**

```json
{
  "conversation_id": "demo-conversation-001",
  "message": "Explain what a vector database is."
}
```

### Example: Chat Response

```json
{
  "conversation_id": "demo-conversation-001",
  "response": "A vector database stores and retrieves numerical representations of data called embeddings..."
}
```

The response text will vary depending on the prompt, conversation context, and Gemini model.

---

## 🧠 Key Concepts Demonstrated

### 1. Large Language Model Integration
Connects a Python backend to a hosted generative AI model through the Google Gen AI SDK.

### 2. Conversation Memory
Uses stored conversation history to support contextual follow-up questions.

### 3. Context Window Management
Selects recent messages instead of sending the entire conversation on every request.

### 4. RESTful API Development
Uses FastAPI request models, response models, validation, and HTTP error handling.

### 5. Database Persistence
Uses SQLite to preserve messages across application restarts.

### 6. Frontend-Backend Communication
Uses JavaScript's Fetch API to exchange JSON data with the backend.

### 7. Configuration and Error Handling
Uses environment variables for credentials, structured logging, and bounded retries for selected transient API failures.

---

## 🧪 Testing

Run the application and manually verify:

- [ ] Gemini generates a response.
- [ ] Follow-up questions use previous conversation context.
- [ ] Different conversation IDs maintain separate histories.
- [ ] Conversation history remains available after restarting the server.
- [ ] The dark and light theme toggle works.
- [ ] The selected theme persists after refreshing the page.
- [ ] Invalid or empty messages are rejected.
- [ ] API failures produce controlled error responses.
- [ ] Conversation history can be retrieved and deleted.

If automated tests are configured in the `tests/` directory, install pytest and run:

```bash
pip install pytest
python -m pytest -v
```

---

## 🔐 Security Considerations

- Store API credentials in environment variables.
- Exclude `.env`, local databases, virtual environments, and generated files from Git.
- Validate incoming requests using Pydantic.
- Avoid logging sensitive user messages or credentials.
- Protect conversation retrieval and deletion endpoints with authentication before public deployment.
- Apply rate limiting and usage controls before exposing the application publicly.

---

## 🔮 Future Enhancements

- Conversation sidebar with multiple saved chats.
- Markdown rendering and syntax-highlighted code blocks.
- Streaming AI responses.
- Conversation summarization for long-running chats.
- User authentication and per-user conversation ownership.
- Automated unit and integration tests.
- Docker support and cloud deployment.
- Usage monitoring and response-time analytics.

---

## 🎯 Project Objective

The objective of ContextMate AI is to demonstrate how a generative AI application can combine an LLM API, conversational context, persistent storage, backend validation, and an interactive frontend to deliver a context-aware chatbot.

---

## 👨‍💻 Author

**YOUR NAME**

GitHub: https://github.com/YOUR_USERNAME

---

## 📄 License

This project is available for educational and portfolio purposes. Add a license file if you intend to distribute the project under specific reuse terms.
