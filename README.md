# Multi-Agent GitHub README Updater

> A Flask web application that uses a multi-agent AI pipeline with Ollama to automatically generate professional, structured README files for your GitHub repositories.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![Ollama](https://img.shields.io/badge/Ollama-llama3.1-orange.svg)](https://ollama.ai/)

---
## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [Contributing](#-contributing)

---

## 🎯 Overview

Tired of writing and maintaining README files for all your repositories? This tool automates the process using a sophisticated multi-agent AI system that:

1. 🔗 **Connects** to your GitHub account (Personal Access Token)
2. 📚 **Analyzes** repository structure, code, dependencies, and frameworks
3. 💾 **Backs up** existing READMEs before making changes
4. 🤖 **Generates** professional, structured documentation using AI
5. 🔍 **Reviews** and improves quality with a reviewer agent
6. 💻 **Commits** directly to your repositories

Perfect for maintaining consistent documentation across personal or organizational repositories.

---

## ✨ Features

### Core Functionality
- 🔐 **Simple Authentication** - GitHub Personal Access Token (no OAuth complexity)
- 📋 **Repository Management** - View all repos with stats (stars, forks, language, last update)
- ✅ **Select All** - Bulk select repositories with filtering
- 🔍 **Advanced Filtering** - Filter by language, visibility (public/private), README status
- 💾 **Automatic Backups** - Local backup before any changes (restore anytime)
- 👀 **Preview Mode** - Review generated README before committing

### AI-Powered Generation
- 🤖 **Multi-Agent Pipeline** - Three specialized LLM agents collaborate
- 🧠 **Intelligent Analysis** - Understands project type, purpose, and architecture
- ✍️ **Smart Generation** - Creates contextual, relevant documentation
- 🔍 **Quality Review** - Automated review and improvement pass
- 📊 **Quality Scoring** - Rates generated README quality (0-100)

### User Experience
- 🎨 **Modern UI** - Clean Bootstrap 5 interface with gradients
- 📱 **Responsive Design** - Works on desktop and mobile
- ⚡ **Real-time Feedback** - Progress indicators during generation
- 📝 **Edit Before Commit** - Modify generated content in preview
- 🔄 **Restore Backups** - Easy one-click restoration from web UI

---

## 🏗️ Architecture

This project follows a **multi-agent architecture** where specialized AI agents collaborate through a pipeline:

```
┌─────────────────────────────────────────────────────────────┐
│                      Services Layer                          │
│  ┌────────────┐  ┌─────────────┐  ┌────────────────────┐    │
│  │  GitHub    │  │   Backup    │  │     LLM Service    │    │
│  │  Service   │  │   Service   │  │ Ollama or OpenAI   │    │
│  └────────────┘  └─────────────┘  └────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              Multi-Agent Pipeline (LLM-Powered)              │
│                                                              │
│   1️⃣ Analyzer Agent → 2️⃣ Generator Agent → 3️⃣ Reviewer Agent │
│      🧠 Understands      ✍️ Creates           🔍 Improves    │
│      project type        README content       quality        │
└─────────────────────────────────────────────────────────────┘
```

### Agent Responsibilities

| Agent | Type | Purpose |
|-------|------|---------|
| **AnalyzerAgent** | AI Agent (LLM) | Analyzes repository to understand project type, purpose, key features, target audience |
| **GeneratorAgent** | AI Agent (LLM) | Generates comprehensive README with proper structure and sections |
| **ReviewerAgent** | AI Agent (LLM) | Reviews generated content, removes placeholders, improves formatting |
| DiscoveryService | Utility Service | Filters and sorts repositories (no LLM) |
| WriterService | Utility Service | Handles Git commits and PRs (no LLM) |

---

## 🛠️ Tech Stack

| Component | Technology | Version |
|-----------|------------|---------|
| **Backend** | Flask | 3.0.0 |
| **Frontend** | Bootstrap 5 + Jinja2 | 5.3.0 |
| **GitHub API** | PyGithub | 2.1.1 |
| **LLM (Default)** | Ollama (llama3.1:8b) | Latest |
| **LLM (Optional)** | OpenAI GPT-4 / GPT-3.5 | Latest |
| **Language** | Python | 3.11+ |

---

## 📦 Installation

### Prerequisites

- Python 3.11 or higher
- **For Ollama (Default)**: [Ollama](https://ollama.ai/) installed and running
- **For OpenAI (Optional)**: OpenAI API key
- GitHub Personal Access Token with `repo` scope

### Setup Steps

```bash
# Clone the repository
git clone https://github.com/mutabay/Multi-Agent-GitHub-README-Updater.git
cd Multi-Agent-GitHub-README-Updater

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# For Ollama: Install the model (if not already installed)
ollama pull llama3.1:8b

# For OpenAI: Install the OpenAI package
# pip install openai
```

> **Note**: A `.env.example` file is provided as a template. Copy it to `.env` and configure as needed.

---

## ⚙️ Configuration

Create a `.env` file in the root directory (optional - has sensible defaults):

### Option 1: Using Ollama (Default - Local & Free)

```env
# LLM Provider
LLM_PROVIDER=ollama

# Ollama Configuration
OLLAMA_MODEL=llama3.1:8b
OLLAMA_BASE_URL=http://localhost:11434

# Flask
SECRET_KEY=your-secret-key-for-sessions
```

### Option 2: Using OpenAI GPT (Cloud-based)

```env
# LLM Provider
LLM_PROVIDER=openai

# OpenAI Configuration
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo

# Flask
SECRET_KEY=your-secret-key-for-sessions
```

**To switch providers**: Simply change `LLM_PROVIDER` in `.env` and restart the app.

**Installing OpenAI support** (if using OpenAI):
```bash
pip install openai
```

### Getting a GitHub Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name (e.g., "README Updater")
4. Select scope: `repo` (full control of private repositories)
5. Generate and copy the token
6. Paste it when connecting in the web UI

---

## 🚀 Usage

### Starting the Application

```bash
# Make sure Ollama is running
ollama serve

# In another terminal, start the Flask app
python app.py
```

The application will be available at **http://127.0.0.1:5000**

### Workflow

1. **Connect** - Paste your GitHub Personal Access Token
2. **Browse** - View all your repositories with filters
3. **Select** - Choose repos to update (or use "Select All")
4. **Generate** - AI agents analyze and create READMEs
5. **Preview** - Review and edit generated content
6. **Commit** - Save directly to repositories

### Backup Management

All existing READMEs are automatically backed up to `backups/` folder:
- Format: `{username}_{repo}_{timestamp}.md`
- Accessible via `/backups` route in web UI
- One-click restore functionality

---

## 📁 Project Structure

```
Multi-Agent-GitHub-README-Updater/
├── app.py                 # Flask application entry point
├── requirements.txt       # Python dependencies
├── README.md              # This file
│
├── agents/                # AI Agents (LLM-Powered)
│   ├── __init__.py
│   ├── analyzer.py        # Analyzes repo type and features
│   ├── generator.py       # Generates README content
│   ├── reviewer.py        # Reviews and improves quality
│   ├── discover.py        # DiscoveryService - repo filtering
│   └── writer.py          # WriterService - Git operations
│
├── services/              # Non-LLM Services
│   ├── __init__.py
│   ├── github_service.py  # GitHub API integration
│   ├── backup_service.py  # README backup management
│   └── llm_service.py     # Ollama LLM interface
│
├── backups/               # Automatic backup storage
│   └── {username}_{repo}_{timestamp}.md
│
├── templates/             # Jinja2 HTML templates
│   ├── base.html          # Base layout with navbar
│   ├── index.html         # Home - GitHub token input
│   ├── repos.html         # Repository selection page
│   ├── preview.html       # Generated README preview
│   └── result.html        # Success/error messages
│
├── static/                # Frontend assets
│   ├── css/
│   │   └── style.css      # Custom styles
│   └── js/
│       └── app.js         # Client-side interactions
│
└── tests/
    └── test_agents.py     # Unit tests for agents
```

---

## 🔧 How It Works

### Phase 1: Repository Discovery
**DiscoveryService** (non-LLM) fetches all repositories from GitHub and applies filters:
- Active repos (pushed within last year)
- Non-fork repositories
- Significant size (>10KB)

### Phase 2: Analysis
**AnalyzerAgent** (LLM) performs deep project analysis:
- Reads and understands code structure
- Identifies project type (web app, CLI tool, library, etc.)
- Extracts key features and technologies
- Determines target audience

### Phase 3: Generation
**GeneratorAgent** (LLM) creates comprehensive README:
- Uses analysis insights to write contextual content
- Structures with proper markdown sections
- Adapts tone for personal vs. organizational repos
- Avoids generic placeholders like "Unknown"

### Phase 4: Review
**ReviewerAgent** (LLM) performs quality control:
- Checks for placeholder text ("Unknown", "TODO")
- Removes corporate language in personal repos
- Ensures proper formatting and consistency
- Validates content length (not too short or verbose)

### Phase 5: Commit
**WriterService** (non-LLM) handles Git operations:
- Creates backup of existing README
- Commits directly to repository
- Provides rollback via backup restoration

---

## 🤝 Contributing

Contributions are welcome! If you'd like to improve this project:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages (`git commit -m 'Add feature X'`)
6. Push to your fork (`git push origin feature/improvement`)
7. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add docstrings to new functions
- Test with multiple repository types
- Keep LLM prompts clear and specific

---

## 📝 License

This project is open source and available under the MIT License.

---

## 👤 Author

**Bayram Mütevellioğlu**
- GitHub: [@mutabay](https://github.com/mutabay)

---

## ⚠️ Troubleshooting

### Common Issues

**"Model llama3.1:8b not found"**
```bash
ollama pull llama3.1:8b
```

**"Connection refused to Ollama"**
- Make sure Ollama is running: `ollama serve`
- Check Ollama is at http://localhost:11434

**"GitHub API rate limit exceeded"**
- Authenticated requests have 5000/hour limit
- Wait for rate limit reset or use different token

**Generation takes too long**
- Default timeout is 120 seconds
- Large repos with many files may take longer
- Consider adjusting `max_tokens` in [services/llm_service.py](services/llm_service.py)

---

## 🔮 Future Enhancements

- [ ] Batch processing with progress tracking
- [ ] Customizable README templates
- [ ] README version history and comparison

---
