"""
Services for external integrations

Services handle EXTERNAL OPERATIONS and DATA ACCESS.
They make API calls, read/write files, and communicate with external systems.

Service Responsibilities:
- GitHubService: ALL GitHub API interactions (fetch, commit, PR, branches)
- BackupService: Local filesystem backup operations
- LLMService: Ollama/LLM API interactions
"""

from .github_service import GitHubService
from .backup_service import BackupService
from .llm_service import LLMService

__all__ = ['GitHubService', 'BackupService', 'LLMService']

