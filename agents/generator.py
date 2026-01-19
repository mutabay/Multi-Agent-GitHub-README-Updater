"""
Generator Agent - Generates README content using LLM

This agent is responsible for:
- Building prompts for README generation
- Coordinating with LLM service
- Formatting generated content
- Providing fallback content if LLM fails

NOTE: This agent contains README-specific prompts and logic.
      Actual LLM calls go through LLMService.
"""

from typing import Dict


class GeneratorAgent:
    """Agent that generates README content using LLM"""
    
    def __init__(self):
        """Initialize Generator Agent (stateless)"""
        pass
    
    def generate(self, analysis: Dict, llm_service) -> str:
        """
        Generate README content based on repository analysis
        
        Args:
            analysis: Repository analysis data from AnalyzerAgent
            llm_service: LLM service instance for generation
            
        Returns:
            Generated README content in Markdown format
        """
        prompt = self._build_prompt(analysis)
        
        try:
            readme_content = llm_service.generate(prompt, temperature=0.7, max_tokens=2048)
            readme_content = self._clean_response(readme_content)
            
            # Only check for critical quality issues (like too many "Unknown")
            if self._has_critical_issues(readme_content):
                print("Generated README has critical issues, using fallback")
                return self._generate_fallback(analysis)
            
            return readme_content
            
        except Exception as e:
            print(f"LLM generation failed: {e}")
            return self._generate_fallback(analysis)
    
    def _has_critical_issues(self, content: str) -> bool:
        """Check only for critical issues that make README unusable"""
        if len(content) < 50:
            return True
        
        # Only fail if there are MANY unknowns (more than 5)
        if content.lower().count('unknown') > 5:
            return True
        
        # Check for placeholders
        if '[insert' in content.lower() or '[todo]' in content.lower():
            return True
        
        return False
    
    def _build_prompt(self, analysis: Dict) -> str:
        """Build intelligent prompt for README generation"""
        
        repo_name = analysis.get('repo_name', '')
        short_name = analysis.get('repo_short_name', repo_name.split('/')[-1] if repo_name else 'project')
        description = analysis.get('description', '') or ''
        languages = analysis.get('languages', {})
        dependencies = analysis.get('dependencies', [])
        frameworks = analysis.get('frameworks', [])
        primary_lang = analysis.get('primary_language', '')
        structure = analysis.get('structure', [])
        username = analysis.get('username', '')
        existing_readme = analysis.get('existing_readme', '')
        
        # LLM-analyzed insights
        project_type = analysis.get('project_type', '')
        main_purpose = analysis.get('main_purpose', '')
        key_features = analysis.get('key_features', [])
        target_audience = analysis.get('target_audience', '')
        
        # Build context - only include what we have
        context_parts = []
        
        if short_name:
            context_parts.append(f"**Repository**: {short_name}")
        if username:
            context_parts.append(f"**Author**: {username}")
        if description:
            context_parts.append(f"**Description**: {description}")
        if main_purpose and main_purpose != description:
            context_parts.append(f"**Purpose**: {main_purpose}")
        if project_type:
            context_parts.append(f"**Project Type**: {project_type}")
        if target_audience:
            context_parts.append(f"**Target Users**: {target_audience}")
        if languages:
            lang_list = ", ".join(list(languages.keys())[:5])
            context_parts.append(f"**Languages**: {lang_list}")
        if primary_lang and primary_lang not in str(languages):
            context_parts.append(f"**Primary Language**: {primary_lang}")
        if frameworks:
            context_parts.append(f"**Frameworks**: {', '.join(frameworks[:5])}")
        if dependencies:
            context_parts.append(f"**Dependencies**: {', '.join(dependencies[:8])}")
        if key_features:
            context_parts.append(f"**Key Features Detected**: {', '.join(key_features[:5])}")
        
        # Format structure
        structure_tree = self._format_directory_tree(structure, max_items=20)
        
        # Build sections to include based on available data
        sections = ["# Title (just the project name)"]
        
        if description or main_purpose:
            sections.append("## Description (brief and honest)")
        
        if key_features or frameworks or primary_lang:
            sections.append("## Features (ONLY list real, detectable features)")
        
        if languages or frameworks:
            sections.append("## Tech Stack (table with ONLY known technologies)")
        
        if structure and len(structure) > 1:
            sections.append("## Project Structure")
        
        if primary_lang and dependencies:
            sections.append(f"## Installation (ONLY if there are dependencies to install)")
        
        if primary_lang and (key_features or frameworks):
            sections.append("## Usage (ONLY if you can infer how it's used)")
        
        if username:
            sections.append(f"## Author")
        
        # Build existing README context with clear instructions
        if existing_readme:
            readme_context = f"""
**Existing README Content**:
```
{existing_readme[:1000]}
```

**YOUR TASK**: Use the existing README as a FOUNDATION. 
- Extract any good, accurate information from it
- Fix any issues (corporate language, placeholders, "Unknown" values)
- Add missing sections based on detected project structure
- Improve formatting and clarity
- Keep what's already good, enhance what needs work"""
        else:
            readme_context = "**No existing README** - creating from scratch."
        
        prompt = f"""You are writing a README for a PERSONAL GitHub repository (not a company/team project).

{chr(10).join(context_parts) if context_parts else "**WARNING**: Very limited information available."}

**Directory Structure**:
```
{structure_tree}
```

{readme_context}

**CRITICAL RULES - FOLLOW EXACTLY**:
1. ❌ NEVER use "Unknown", "N/A", "[Insert...]", "[TODO]" - if you don't know, SKIP that part entirely
2. ❌ NEVER use corporate language like "our team", "we", "passionate", "revolutionary" for personal repos
3. ❌ NEVER make up features, frameworks, or technologies not explicitly mentioned
4. ❌ NEVER include License section unless there's a LICENSE file in the structure
5. ❌ NEVER include Installation section if there are no dependencies or build steps
6. ✅ DO use simple, direct language (this is ONE person's repo, not a team)
7. ✅ DO skip any section you can't fill with real information
8. ✅ DO keep it minimal and honest - better to have 3 good sections than 10 vague ones
9. ✅ DO extract and preserve good content from existing README (if any)
10. ✅ DO fix issues in existing README (corporate tone, placeholders, errors)

**Tone**: Simple, direct, personal. Write as if YOU are the {username} explaining your own project.

**Sections to consider** (ONLY include if you have real content):
{chr(10).join(f"- {s}" for s in sections)}

Generate the README now. Keep it SHORT and REAL. No fluff, no corporate speak, no placeholders.
If there's an existing README with good content, BUILD ON IT - fix what's wrong and add what's missing."""

        return prompt
    
    def _format_directory_tree(self, structure: list, max_items: int = 30) -> str:
        """Format directory structure as a tree for the prompt"""
        if not structure:
            return "No structure available"
        
        # Sort: directories first, then files
        dirs = sorted([item for item in structure if item.get('type') == 'dir'], key=lambda x: x.get('name', ''))
        files = sorted([item for item in structure if item.get('type') != 'dir'], key=lambda x: x.get('name', ''))
        
        tree_lines = []
        all_items = dirs + files
        
        for i, item in enumerate(all_items[:max_items]):
            name = item.get('name', 'unknown')
            item_type = item.get('type', 'file')
            prefix = "├── " if i < len(all_items) - 1 else "└── "
            
            if item_type == 'dir':
                tree_lines.append(f"{prefix}{name}/")
            else:
                tree_lines.append(f"{prefix}{name}")
        
        if len(all_items) > max_items:
            tree_lines.append(f"└── ... and {len(all_items) - max_items} more items")
        
        return "\n".join(tree_lines) if tree_lines else "Empty repository"
    
    def _clean_response(self, content: str) -> str:
        """Clean up LLM response"""
        # Remove markdown code fence if LLM wrapped it
        if content.startswith('```markdown'):
            content = content[11:]
        if content.startswith('```md'):
            content = content[5:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        
        return content.strip()
    
    def _generate_fallback(self, analysis: Dict) -> str:
        """Generate minimal but well-structured README if LLM fails"""
        
        repo_name = analysis.get('repo_name', '')
        short_name = analysis.get('repo_short_name', 'project')
        description = analysis.get('description', '')
        primary_lang = analysis.get('primary_language', '')
        frameworks = analysis.get('frameworks', [])
        dependencies = analysis.get('dependencies', [])
        username = analysis.get('username', '')
        structure = analysis.get('structure', [])
        topics = analysis.get('topics', [])
        
        # Check if there's a LICENSE file
        has_license = any(item.get('name', '').upper().startswith('LICENSE') for item in structure)
        dependencies = analysis.get('dependencies', [])
        username = analysis.get('username', '')
        structure = analysis.get('structure', [])
        topics = analysis.get('topics', [])
        
        # Check if there's a LICENSE file
        has_license = any(item.get('name', '').upper().startswith('LICENSE') for item in structure)
        
        # Language-specific install commands
        install_commands = {
            'Python': 'pip install -r requirements.txt',
            'JavaScript': 'npm install',
            'TypeScript': 'npm install',
            'Ruby': 'bundle install',
            'Go': 'go mod download',
            'Rust': 'cargo build',
            'Java': 'mvn install',
        }
        
        run_commands = {
            'Python': 'python main.py',
            'JavaScript': 'npm start',
            'TypeScript': 'npm start',
            'Ruby': 'ruby main.rb',
            'Go': 'go run .',
            'Rust': 'cargo run',
            'Java': 'mvn exec:java',
        }
        
        # Start building README
        sections = []
        
        # Title
        sections.append(f"# {short_name}")
        
        # Description
        if description:
            sections.append(f"\n{description}\n")
        
        # Topics as badges
        if topics:
            topic_badges = " ".join([f"`{topic}`" for topic in topics[:5]])
            sections.append(f"\n{topic_badges}\n")
        
        # Features - only if we have real info
        features = []
        if primary_lang:
            features.append(f"- Built with {primary_lang}")
        if frameworks:
            features.append(f"- Powered by {', '.join(frameworks[:3])}")
        if features:
            sections.append("\n## 🚀 Features\n")
            sections.append("\n".join(features))
        
        # Tech Stack - only if we have info
        if primary_lang or frameworks or dependencies:
            sections.append("\n\n## 🛠️ Tech Stack\n")
            sections.append("| Component | Technology |")
            sections.append("|-----------|------------|")
            if primary_lang:
                sections.append(f"| Language | {primary_lang} |")
            if frameworks:
                sections.append(f"| Framework | {', '.join(frameworks[:3])} |")
            if dependencies:
                sections.append(f"| Dependencies | {', '.join(dependencies[:5])} |")
        
        # Project Structure - only if non-empty
        if structure:
            structure_tree = self._format_directory_tree(structure, max_items=15)
            sections.append(f"\n\n## 📁 Project Structure\n\n```\n{structure_tree}\n```")
        
        # Installation - only if we know the language
        if primary_lang and primary_lang in install_commands:
            install_cmd = install_commands[primary_lang]
            clone_url = f"https://github.com/{repo_name}.git" if repo_name else f"https://github.com/username/{short_name}.git"
            sections.append(f"""

## 📦 Installation

```bash
# Clone the repository
git clone {clone_url}
cd {short_name}

# Install dependencies
{install_cmd}
```""")
        
        # Usage - only if we know the language
        if primary_lang and primary_lang in run_commands:
            run_cmd = run_commands[primary_lang]
            sections.append(f"""

## 🔧 Usage

```bash
{run_cmd}
```""")
        
        # Contributing
        sections.append("""

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.""")
        
        # Author - only if known
        if username:
            sections.append(f"""

## 👤 Author

**{username}**
- GitHub: [@{username}](https://github.com/{username})""")
        
        # License - only if LICENSE file exists
        if has_license:
            sections.append("""

## 📝 License

See [LICENSE](LICENSE) file for details.""")
        
        # Footer
        sections.append("""

---
*README generated by Multi-Agent GitHub README Updater*
""")
        
        return "".join(sections)
    
    def refine(self, current_readme: str, feedback: str, llm_service) -> str:
        """
        Refine README based on user feedback
        
        Args:
            current_readme: Current README content
            feedback: User's feedback/requests
            llm_service: LLM service instance
            
        Returns:
            Refined README content
        """
        prompt = f"""You are a technical writer improving a README.md based on feedback.

## Current README:
{current_readme}

## User Feedback:
{feedback}

## Instructions:
Update the README to address the feedback while maintaining good structure.
Return only the complete updated README.md content.

Updated README:"""

        try:
            refined = llm_service.generate(prompt, temperature=0.5)
            return self._clean_response(refined)
        except Exception:
            return current_readme
