"""
Reviewer Agent - Reviews and improves generated README content

This agent is responsible for:
- Reviewing generated README for quality
- Checking for completeness and accuracy
- Suggesting improvements
- Ensuring professional formatting

This is a TRUE AGENT that uses LLM for intelligent review.
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
            print("✅ Reviewer Agent: Review complete!")
            return improved
        except Exception as e:
            print(f"⚠️ Reviewer Agent failed: {e}, returning original")
            return readme_content
    
    def _build_review_prompt(self, readme_content: str, analysis: Dict) -> str:
        """Build prompt for README review"""
        
        repo_name = analysis.get('repo_short_name', 'project')
        primary_lang = analysis.get('primary_language', 'Unknown')
        frameworks = analysis.get('frameworks', [])
        
        prompt = f"""You are a senior technical writer reviewing a README.md file.

**Project**: {repo_name}
**Language**: {primary_lang}
**Frameworks**: {', '.join(frameworks) if frameworks else 'None'}

**README to Review**:
```markdown
{readme_content[:2500]}
```

**Your Task**: Improve this README by:
1. Fixing any formatting issues (proper markdown)
2. Making descriptions more engaging and clear
3. Ensuring code blocks have correct language hints
4. Adding missing emojis for visual appeal (but don't overdo it)
5. Making sure installation steps are accurate for {primary_lang}
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
