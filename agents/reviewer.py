"""
Reviewer Agent - Reviews and improves generated README content

This agent is responsible for:
- Reviewing generated README for quality
- Checking for completeness and accuracy
- Suggesting improvements
- Ensuring professional formatting
"""

from typing import Dict


class ReviewerAgent:
    """Agent that reviews and improves README content using LLM"""
    
    def __init__(self):
        """Initialize Reviewer Agent"""
        pass
    
    def review(self, readme_content: str, analysis: Dict, llm_service) -> str:
        """
        Review and improve the generated README
        
        Args:
            readme_content: The generated README to review
            analysis: Original repository analysis
            llm_service: LLM service for intelligent review
            
        Returns:
            Improved README content
        """
        prompt = self._build_review_prompt(readme_content, analysis)
        
        try:
            print("🔍 Reviewer Agent: Reviewing and improving README...")
            improved = llm_service.generate(prompt, temperature=0.3, max_tokens=2048)
            improved = self._clean_response(improved)
            print("Reviewer Agent: Review complete!")
            return improved
        except Exception as e:
            print(f"Reviewer Agent failed: {e}, returning original")
            return readme_content
    
    def _build_review_prompt(self, readme_content: str, analysis: Dict) -> str:
        """Build prompt for README review"""
        
        repo_name = analysis.get('repo_short_name', 'project')
        primary_lang = analysis.get('primary_language', '')
        frameworks = analysis.get('frameworks', [])
        username = analysis.get('username', '')
        
        # Check if README has problems
        has_unknown = 'unknown' in readme_content.lower()
        has_placeholders = '[insert' in readme_content.lower() or '[todo' in readme_content.lower()
        has_corporate = 'our team' in readme_content.lower()
        
        prompt = f"""Review and improve this README for a PERSONAL repository.

**Project**: {repo_name} (by {username})
**Language**: {primary_lang or 'Not specified'}
**Frameworks**: {', '.join(frameworks) if frameworks else 'None detected'}

**README to Review**:
```markdown
{readme_content[:2000]}
```

**Critical Issues to Fix**:
{f"- ❌ Remove ALL instances of 'Unknown', 'N/A', placeholders" if has_unknown or has_placeholders else ""}
{f"- ❌ Remove corporate language ('our team', 'we', 'passionate') - this is a personal repo" if has_corporate else ""}
- ❌ Remove any sections that don't have real content
- ❌ Remove License section if there's no LICENSE file mentioned

**Improvements**:
1. Fix markdown formatting issues
2. Make language simple and direct (personal, not corporate)
3. Remove fluff and placeholder text
4. Keep only sections with real information
5. Ensure code blocks have correct language hints
6. Use minimal emojis (1-2 per section header max)

**Output ONLY the improved README**, no explanations.
6. Ensuring professional tone throughout

Output ONLY the improved README, no explanations or comments."""

        return prompt
    
    def _clean_response(self, content: str) -> str:
        """Clean up LLM response"""
        if content.startswith('```markdown'):
            content = content[11:]
        if content.startswith('```md'):
            content = content[5:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        return content.strip()
    
    def quick_check(self, readme_content: str) -> Dict:
        """
        Quick non-LLM check for README quality
        
        Returns:
            Dict with quality metrics
        """
        lines = readme_content.split('\n')
        
        checks = {
            'has_title': any(line.startswith('# ') for line in lines),
            'has_description': len(readme_content) > 200,
            'has_installation': 'install' in readme_content.lower(),
            'has_usage': 'usage' in readme_content.lower(),
            'has_code_blocks': '```' in readme_content,
            'has_badges': 'shields.io' in readme_content or '![' in readme_content,
            'word_count': len(readme_content.split()),
            'section_count': readme_content.count('## '),
        }
        
        checks['quality_score'] = sum([
            checks['has_title'] * 20,
            checks['has_description'] * 15,
            checks['has_installation'] * 20,
            checks['has_usage'] * 15,
            checks['has_code_blocks'] * 15,
            checks['has_badges'] * 5,
            min(checks['section_count'] * 2, 10),
        ])
        
        return checks
