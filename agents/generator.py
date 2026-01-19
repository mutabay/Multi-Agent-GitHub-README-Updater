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
            readme_content = llm_service.generate(prompt, temperature=0.7)
            
            # Clean up response if needed
            readme_content = self._clean_response(readme_content)
            
            return readme_content
            
        except Exception as e:
            print(f"⚠️ LLM generation failed: {e}")
            return self._generate_fallback(analysis)
    
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
        sections = ["# Title with relevant badge (language badge from shields.io)"]
        sections.append("## Description (engaging 2-3 sentences about what this does)")
        sections.append("## Features (bullet points based on actual capabilities)")
        
        if languages or frameworks:
            sections.append("## Tech Stack (table format with actual technologies)")
        
        if primary_lang:
            sections.append(f"## Installation (step-by-step for {primary_lang})")
            sections.append("## Usage (realistic code examples)")
        
        if structure:
            sections.append("## Project Structure (explain key directories)")
        
        sections.append("## Contributing (brief guidelines)")
        
        if username:
            sections.append(f"## Author ({username} with GitHub link)")
        
        prompt = f"""Create a professional README.md for this GitHub repository.

{chr(10).join(context_parts)}

**Directory Structure**:
```
{structure_tree}
```

{f"**Existing README (use as reference, improve upon it)**:{chr(10)}{existing_readme[:1000]}" if existing_readme else ""}

**IMPORTANT RULES**:
- NEVER write "Unknown" or "N/A" - if you don't know something, skip that section entirely
- NEVER make up fake features or technologies not mentioned
- NEVER include a License section unless you see a LICENSE file in the structure
- DO use the actual repository name, languages, and frameworks provided
- DO make installation steps realistic for the detected language
- DO infer project purpose from the name and structure if description is empty
- DO use emojis sparingly for section headers (🚀, 📦, ⚙️, etc.)

**Sections to include**:
{chr(10).join(f"{i+1}. {s}" for i, s in enumerate(sections))}

Output ONLY the README markdown, no explanations or comments."""

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
        """Generate basic README if LLM fails - only includes known information"""
        
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
