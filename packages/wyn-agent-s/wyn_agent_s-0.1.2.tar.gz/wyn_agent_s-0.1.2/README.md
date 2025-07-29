# 🤖 WYN Agent-S

**WYN Agent-S** is an agentic framework that seamlessly integrates a built-in router, intent classifier, and dependency resolver to enable conversational AI with external API interactions. Designed with modularity and extensibility in mind, it simplifies building intelligent chatbots and assistants with structured, goal-driven behavior.

---

## 📦 Installation

Install the package from PyPI:

```bash
pip install wyn-agent-s
````

---

## 🚀 Quick Start

Here's how to set up and start chatting with `Agent_S` in a Colab notebook:

```python
from google.colab import userdata
OPENAI_API_KEY = userdata.get('OPENAI_API_KEY')
SERPAPI_API_KEY = userdata.get('SERPAPI_API_KEY')

from wyn_agent_s.main import Agent_S

# Initialize the agent
agent = Agent_S(
    openai_api_key=OPENAI_API_KEY,
    serpapi_key=SERPAPI_API_KEY
)

# Start chat session
agent.start_chat()
```

---

## 💬 Sample Interaction

```text
👋 Welcome! Press 'EXIT' to quit the chat at any time.
👤 User: how are you?
🤖 Bot Response: As an artificial intelligence, I don't have feelings, but I'm here and ready to help you. How can I assist you today?
👀 No API call found in the event stream. Exiting.

👤 User: I want to do a google search
Match found for trigger: 'google search'
👀 Intent detected for API call: google_search
Please provide engine: Google
Please provide query: today's weather in New York
Please provide location: New York, NY
Please provide num: 3

Run google search API using:
query=today's weather in New York,
location=New York, NY

👀 Results:
| Title | Link | Snippet |
| :--- | :--- | :--- |
| Weather Forecast and Conditions for New York City, NY | [Link](https://weather.com/weather/today/l/...) | Occasional rain likely to continue for the next several hours. |
| New York, NY Weather Forecast | [Link](https://www.accuweather.com/en/us/new-york/...) | 10-Day Weather Forecast ... |
| New York - BBC Weather | [Link](https://www.bbc.com/weather/...) | Day by day forecast ... |

👤 User: EXIT
👋 Thanks for chatting! Have a great day! 🌟
```

---

## 🧠 Key Features

* **🧭 Built-in Router:** Dynamically selects the correct function based on user intent.
* **🎯 Intent Classifier:** Detects user goals using natural language prompts.
* **🧩 Dependency Resolver:** Gathers required parameters for API calls through dialogue.
* **📑 Modular Design:** Clean separation between core logic, helpers, and API definitions.
* **🧪 Test Suite:** Includes unit tests for framework robustness.

---

## 🗂️ Project Structure

```
wyn-agent-s/
├── wyn_agent_s/
│   ├── __init__.py
│   ├── main.py            # Core Agent_S logic
│   ├── helper.py          # Utility functions
│   ├── list_of_apis.py    # Registered APIs and triggers
│   └── metadata.json      # API metadata config
├── tests/
│   ├── __init__.py
│   └── test.py            # Unit tests
├── dist/                  # Distribution artifacts
├── LICENSE
├── pyproject.toml         # Poetry project config
└── README.md              # This file
```

---

## 🧪 Run Tests

To run unit tests:

```bash
python -m unittest discover tests
```

---

## 📜 License

This project is licensed under the terms of the [MIT License](./LICENSE).

---

## 🙌 Contributing

Contributions are welcome! Please fork the repo and submit a pull request.

---

## 🔗 Links

* [PyPI Package](https://pypi.org/project/wyn-agent-s/)
* [GitHub Repo](https://github.com/yiqiao-yin/wyn-agent-s)

```
