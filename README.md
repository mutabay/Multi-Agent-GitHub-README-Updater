# Multi-Agent-GitHub-README-Updater
GitHub README Updater for having structured README files accross all the repositories.

> A Flask web app that uses AI agents to generate professional README files for your GitHub repositories.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [How It Works](#-how-it-works)
- [Development Phases](#-development-phases)
- [License](#-license)

---

## 🎯 Overview

A Flask web application with a multi-agent backend that:

1. **Connects** to your GitHub account (via Personal Access Token)
2. **Lists** all your repositories with filters
3. **Analyzes** each repo's code, structure, and existing docs
4. **Generates** professional README files using AI
5. **Commits** the new READMEs via PR or direct push

---

## ✨ Features

- 🔐 **Simple Auth** - Just paste your GitHub token
- 📋 **Repository List** - See all repos with stats (stars, language, last update)
- 🔍 **Filtering** - Filter by language, name, or select specific repos
- 🧠 **Smart Analysis** - Detects tech stack, frameworks, dependencies
- ✍️ **AI Generation** - Creates structured READMEs with OpenAI/Claude
- 👁️ **Preview** - Review generated README before committing
- 🔄 **Flexible Output** - Create PR or commit directly

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Flask |
| **Frontend** | Jinja2 + Bootstrap 5 |
| **GitHub API** | PyGithub |
| **LLM** | OpenAI API (GPT-4) |
| **Database** | SQLite (session storage) |

---

## 📁 Project Structure

```
github-readme-agent/
├── app.py                 # Flask application entry point
├── config.py              # Configuration
├── requirements.txt
├── .env.example
│
├── agents/                # AI Agents
│   ├── __init__.py
│   ├── discovery.py       # Fetches repos from GitHub
│   ├── analyzer.py        # Analyzes repo content
│   ├── generator.py       # Generates README with LLM
│   └── writer.py          # Commits to GitHub
│
├── services/
│   ├── __init__.py
│   ├── github_service.py  # GitHub API wrapper
│   └── llm_service.py     # OpenAI/Claude wrapper
│
├── templates/
│   ├── base.html
│   ├── index.html         # Home - enter GitHub token
│   ├── repos.html         # Repository selection
│   ├── preview.html       # Preview generated README
│   └── result.html        # Success/failure result
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
│
└── tests/
    └── test_agents.py
```

---

## 📦 Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/github-readme-agent.git
cd github-readme-agent

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
copy .env.example .env
# Edit .env with your OpenAI API key
```

### Environment Variables

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
SECRET_KEY=your-flask-secret-key
```

---

## 🚀 Usage

```bash
# Run the app
python app.py

# Open browser
# http://localhost:5000
```

### Steps:
1. Enter your GitHub Personal Access Token
2. View your repositories
3. Filter/select repos you want to update
4. Click "Generate READMEs"
5. Preview the generated content
6. Confirm to create PR or commit directly

---

## ⚙️ How It Works

```
┌──────────────────────────────────────────────────────────┐
│                    Flask Web App                          │
│                                                          │
│  [Home] → [Repo List] → [Generate] → [Preview] → [Done]  │
└──────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│                      Agents                               │
│                                                          │
│  1. Discovery Agent  →  Fetch repos from GitHub          │
│  2. Analyzer Agent   →  Analyze code & structure         │
│  3. Generator Agent  →  Create README with LLM           │
│  4. Writer Agent     →  Commit/PR to GitHub              │
└──────────────────────────────────────────────────────────┘
```

### Agent Details

**1. Discovery Agent**
- Fetches all repos for the authenticated user
- Collects metadata: language, stars, description, topics

**2. Analyzer Agent**
- Reads file structure via GitHub API
- Detects: language, frameworks, dependencies
- Parses existing README (if any)

**3. Generator Agent**
- Sends analysis to LLM (OpenAI/Claude)
- Uses structured prompts for each section
- Generates: description, installation, usage, etc.

**4. Writer Agent**
- Creates a new branch (optional)
- Commits the generated README
- Opens a Pull Request (or direct commit)

---

## 📅 Development Phases

### Phase 1: Setup (Day 1)
- [ ] Flask app scaffold
- [ ] GitHub OAuth/token handling
- [ ] Basic templates

### Phase 2: Discovery Agent (Day 2)
- [ ] Fetch user repos
- [ ] Display in web UI
- [ ] Add filtering

### Phase 3: Analyzer Agent (Day 3)
- [ ] Fetch repo contents
- [ ] Detect tech stack
- [ ] Parse existing README

### Phase 4: Generator Agent (Day 4-5)
- [ ] OpenAI integration
- [ ] README template/prompts
- [ ] Generate content

### Phase 5: Writer Agent (Day 6)
- [ ] Commit to GitHub
- [ ] Create PR option
- [ ] Handle errors

### Phase 6: Polish (Day 7)
- [ ] Preview UI
- [ ] Error handling
- [ ] Testing

