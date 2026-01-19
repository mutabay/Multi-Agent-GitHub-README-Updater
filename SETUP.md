# Setup and Usage Guide

## Quick Start

### 1. Prerequisites

- Python 3.11+ installed
- Ollama installed and running ([Get Ollama](https://ollama.ai))
- A GitHub Personal Access Token ([Create one](https://github.com/settings/tokens/new))
  - Required scopes: `repo`, `read:user`

### 2. Installation

```bash
# The virtual environment is already set up in .venv
# Activate it:
.\.venv\Scripts\activate  # Windows

# Packages are already installed, but if needed:
pip install -r requirements.txt
```

### 3. Configure Ollama

Make sure Ollama is running and you have a suitable model installed:

```bash
# Check if Ollama is running
ollama list

# If you need to install a model (recommended: llama2, mistral, or codellama)
ollama pull llama2
# OR for better code understanding:
ollama pull codellama
```

### 4. Environment Variables

Create a `.env` file (optional - token can be entered in web UI):

```env
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=True
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

### 5. Run the Application

```bash
# Make sure you're in the project directory and venv is activated
python app.py
```

The application will start at: http://localhost:5000

### 6. Usage Flow

1. **Connect to GitHub**
   - Enter your GitHub Personal Access Token
   - Token is stored only in session (not saved permanently)

2. **Select Repositories**
   - View all your repositories
   - Filter by language or name
   - Select repositories to update

3. **Generate READMEs**
   - Click "Generate READMEs"
   - Existing READMEs are automatically backed up
   - AI analyzes each repository and generates professional README

4. **Preview and Commit**
   - Review generated READMEs
   - Edit if needed
   - Choose: Direct commit or Create Pull Request
   - Commit changes

## Features

✅ **Automatic Backup**: All existing README files are backed up before changes
✅ **Smart Analysis**: Detects languages, frameworks, dependencies
✅ **AI Generation**: Uses Ollama LLM for professional README content
✅ **Preview Mode**: Review before committing
✅ **Flexible Output**: Direct commit or Pull Request

## Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if not running
ollama serve
```

### Port Already in Use

If port 5000 is busy, edit `app.py`:

```python
app.run(debug=True, port=5001)  # Change port
```

### GitHub API Rate Limits

- Authenticated requests: 5,000 per hour
- If you hit limits, wait or use a different token

## Project Structure

```
Multi-Agent-GitHub-README-Updater/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── agents/                # AI Agents
│   ├── discover.py        # Repository discovery
│   ├── analyzer.py        # Repository analysis
│   ├── generator.py       # README generation
│   └── writer.py          # GitHub commits
├── services/              # Service layer
│   ├── github_service.py  # GitHub API
│   ├── backup_service.py  # Backup management
│   └── llm_service.py     # Ollama integration
├── templates/             # HTML templates
├── static/                # CSS & JavaScript
└── backups/               # README backups
```

## Tech Stack

- **Backend**: Flask 3.0
- **Frontend**: Bootstrap 5 + Vanilla JS
- **GitHub API**: PyGithub
- **LLM**: Ollama (llama2/mistral/codellama)
- **Python**: 3.11+

## License

This project is open source and available under the MIT License.
