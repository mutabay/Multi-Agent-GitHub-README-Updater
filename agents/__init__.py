"""
AI Agents for GitHub README generation

AGENTS (LLM-powered - use AI for intelligent decisions):
- AnalyzerAgent: Intelligent project analysis using LLM
- GeneratorAgent: README content generation using LLM
- ReviewerAgent: Quality review and improvement using LLM

SERVICES (Non-LLM utilities - deterministic operations):
- DiscoveryService: Repository filtering (moved to services conceptually)
- WriterService: Commit coordination (moved to services conceptually)

Multi-Agent Pipeline:
  AnalyzerAgent → GeneratorAgent → ReviewerAgent
"""

from .analyzer import AnalyzerAgent
from .generator import GeneratorAgent
from .reviewer import ReviewerAgent

# Keep these for backward compatibility but they are Services, not Agents
from .discover import DiscoveryService
from .writer import WriterService

__all__ = ['AnalyzerAgent', 'GeneratorAgent', 'ReviewerAgent', 'DiscoveryService', 'WriterService']

