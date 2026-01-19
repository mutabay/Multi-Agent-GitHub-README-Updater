"""
Analyzer Agent - Analyzes repository content and structure using LLM

This agent is responsible for:
- Analyzing repository metadata
- Using LLM to understand project purpose and architecture
- Detecting frameworks and dependencies
- Preparing intelligent analysis for README generation
"""

from typing import Dict, List
import re


class AnalyzerAgent:
    """Agent that analyzes repository content using LLM"""
    
    def __init__(self):
        """Initialize Analyzer Agent"""
        pass
    
    def analyze(self, repo_info: Dict, languages: Dict[str, int],
                structure: List[Dict], file_contents: Dict[str, str],
                llm_service=None) -> Dict:
        """
        Analyze repository data and produce intelligent analysis report
        
        Args:
            repo_info: Repository metadata (name, description, etc.)
            languages: Language bytes from GitHub API
            structure: Directory structure from GitHub API  
            file_contents: Dict mapping file paths to content
            llm_service: Optional LLM service for intelligent analysis
            
        Returns:
            Complete analysis dict for README generation
        """
        # Basic analysis (non-LLM)
        analysis = {
            'repo_name': repo_info.get('full_name', ''),
            'repo_short_name': repo_info.get('name', ''),
            'description': repo_info.get('description', 'No description'),
            'topics': repo_info.get('topics', []),
            'stars': repo_info.get('stars', 0),
            'default_branch': repo_info.get('default_branch', 'main'),
            'languages': self._process_languages(languages),
            'primary_language': self._get_primary_language(languages),
            'structure': structure,
            'dependencies': self._detect_dependencies(structure, file_contents),
            'frameworks': [],
            'has_tests': self._has_tests(structure),
            'has_ci': self._has_ci(structure),
            'has_docker': self._has_docker(structure),
            'has_docs': self._has_docs(structure),
            'existing_readme': file_contents.get('README.md', None)
        }
        
        # Detect frameworks
        analysis['frameworks'] = self._detect_frameworks(
            analysis['dependencies'], 
            analysis['primary_language'],
            structure
        )
        
        # LLM-powered intelligent analysis
        if llm_service:
            try:
                intelligent_analysis = self._intelligent_analyze(analysis, file_contents, llm_service)
                analysis.update(intelligent_analysis)
            except Exception as e:
                print(f"Analyzer Agent LLM analysis failed: {e}")
        
        return analysis
    
    def _intelligent_analyze(self, basic_analysis: Dict, file_contents: Dict, llm_service) -> Dict:
        """Use LLM to provide intelligent project insights"""
        
        print("Analyzer Agent: Performing intelligent analysis...")
        
        # Build context for LLM
        structure_summary = self._summarize_structure(basic_analysis.get('structure', []))
        code_snippet = self._get_main_file_snippet(file_contents, basic_analysis.get('primary_language', ''))
        existing_readme = basic_analysis.get('existing_readme', '')
        
        # Build available info
        info_parts = []
        
        repo_name = basic_analysis.get('repo_short_name', '')
        if repo_name:
            info_parts.append(f"**Project Name**: {repo_name}")
        
        description = basic_analysis.get('description', '')
        if description and description != 'No description':
            info_parts.append(f"**Description**: {description}")
        
        lang = basic_analysis.get('primary_language', '')
        if lang:
            info_parts.append(f"**Language**: {lang}")
        
        deps = basic_analysis.get('dependencies', [])
        if deps:
            info_parts.append(f"**Dependencies**: {', '.join(deps[:10])}")
        
        fws = basic_analysis.get('frameworks', [])
        if fws:
            info_parts.append(f"**Frameworks**: {', '.join(fws)}")
        
        prompt = f"""Analyze this software project and provide insights. Be realistic - if there's limited information, say so honestly.

{chr(10).join(info_parts) if info_parts else "Limited project information available."}

**Directory Structure**:
{structure_summary if structure_summary else "Minimal structure"}

{f"**Code Sample**:{chr(10)}```{chr(10)}{code_snippet[:600]}{chr(10)}```" if code_snippet and code_snippet != "No code available" else ""}

{f"**Existing README**:{chr(10)}{existing_readme[:500]}" if existing_readme else ""}

Based on what you can actually see, respond with ONLY a JSON object:
{{
    "project_type": "type based on evidence or empty string if unclear",
    "main_purpose": "what this does based on actual evidence, or empty if unclear",
    "key_features": ["only features you can actually infer"],
    "target_audience": "who would use this based on evidence",
    "complexity": "beginner/intermediate/advanced based on code"
}}

IMPORTANT: Do not make things up. If you can't determine something, use empty string or empty array."""

        try:
            response = llm_service.generate(prompt, temperature=0.2, max_tokens=500)
            
            # Parse JSON from response
            import json
            # Clean response
            response = response.strip()
            if response.startswith('```'):
                response = response.split('```')[1]
                if response.startswith('json'):
                    response = response[4:]
            
            # Find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                response = response[start:end]
            
            insights = json.loads(response)
            print("✅ Analyzer Agent: Intelligent analysis complete!")
            
            # Only return non-empty values
            result = {}
            if insights.get('project_type'):
                result['project_type'] = insights['project_type']
            if insights.get('main_purpose'):
                result['main_purpose'] = insights['main_purpose']
            if insights.get('key_features'):
                result['key_features'] = [f for f in insights['key_features'] if f]
            if insights.get('target_audience'):
                result['target_audience'] = insights['target_audience']
            if insights.get('complexity'):
                result['complexity'] = insights['complexity']
            
            return result
        except Exception as e:
            print(f"Could not parse LLM insights: {e}")
            return {}
    
    def _summarize_structure(self, structure: List[Dict], max_items: int = 20) -> str:
        """Summarize directory structure"""
        if not structure:
            return "No structure available"
        
        dirs = [item['name'] + '/' for item in structure if item.get('type') == 'dir'][:10]
        files = [item['name'] for item in structure if item.get('type') != 'dir'][:10]
        
        return '\n'.join(dirs + files)
    
    def _get_main_file_snippet(self, file_contents: Dict, language: str) -> str:
        """Get a snippet from the main file"""
        main_files = {
            'Python': ['app.py', 'main.py', '__init__.py'],
            'JavaScript': ['index.js', 'app.js', 'main.js'],
            'TypeScript': ['index.ts', 'app.ts', 'main.ts'],
            'Go': ['main.go'],
            'Rust': ['main.rs', 'lib.rs'],
            'Java': ['Main.java', 'App.java'],
        }
        
        candidates = main_files.get(language, []) + ['README.md']
        
        for filename in candidates:
            if filename in file_contents:
                return file_contents[filename][:800]
        
        # Return first available content
        for content in file_contents.values():
            if content:
                return content[:800]
        
        return "No code available"
    
    def _process_languages(self, languages: Dict[str, int]) -> Dict[str, float]:
        """Convert language bytes to percentages"""
        if not languages:
            return {}
        
        total = sum(languages.values())
        return {
            lang: round((bytes_count / total) * 100, 1)
            for lang, bytes_count in languages.items()
        }
    
    def _get_primary_language(self, languages: Dict[str, int]) -> str:
        """Get the primary (most used) language"""
        if not languages:
            return 'Unknown'
        return max(languages, key=languages.get)
    
    def _detect_dependencies(self, structure: List[Dict], 
                            file_contents: Dict[str, str]) -> List[str]:
        """Detect dependencies from manifest files"""
        dependencies = []
        file_names = {item['name'] for item in structure}
        
        # Python
        if 'requirements.txt' in file_names and 'requirements.txt' in file_contents:
            deps = self._parse_requirements(file_contents['requirements.txt'])
            dependencies.extend(deps)
        
        if 'Pipfile' in file_names:
            dependencies.append('pipenv')
        
        if 'pyproject.toml' in file_names:
            content = file_contents.get('pyproject.toml', '')
            if 'poetry' in content.lower():
                dependencies.append('poetry')
        
        # JavaScript/Node.js
        if 'package.json' in file_names and 'package.json' in file_contents:
            deps = self._parse_package_json(file_contents['package.json'])
            dependencies.extend(deps)
        
        # Ruby
        if 'Gemfile' in file_names and 'Gemfile' in file_contents:
            deps = self._parse_gemfile(file_contents['Gemfile'])
            dependencies.extend(deps)
        
        # Go
        if 'go.mod' in file_names:
            dependencies.append('Go modules')
        
        # Java/Kotlin
        if 'pom.xml' in file_names:
            dependencies.append('Maven')
        if 'build.gradle' in file_names or 'build.gradle.kts' in file_names:
            dependencies.append('Gradle')
        
        # Rust
        if 'Cargo.toml' in file_names:
            dependencies.append('Cargo')
        
        return list(set(dependencies))[:20]  # Unique, max 20
    
    def _detect_frameworks(self, dependencies: List[str], 
                          primary_language: str,
                          structure: List[Dict]) -> List[str]:
        """Detect frameworks from dependencies and structure"""
        frameworks = []
        deps_lower = [d.lower() for d in dependencies]
        file_names = {item['name'].lower() for item in structure}
        
        # Python frameworks
        python_mapping = {
            'flask': 'Flask',
            'django': 'Django', 
            'fastapi': 'FastAPI',
            'streamlit': 'Streamlit',
            'pytest': 'pytest',
            'numpy': 'NumPy',
            'pandas': 'Pandas',
            'tensorflow': 'TensorFlow',
            'torch': 'PyTorch',
            'scikit-learn': 'scikit-learn',
            'sklearn': 'scikit-learn',
        }
        
        # JavaScript frameworks  
        js_mapping = {
            'react': 'React',
            'vue': 'Vue.js',
            'angular': 'Angular',
            'next': 'Next.js',
            'express': 'Express.js',
            'nestjs': 'NestJS',
            '@nestjs': 'NestJS',
            'gatsby': 'Gatsby',
            'svelte': 'Svelte',
        }
        
        # Check dependencies against mappings
        for dep in deps_lower:
            for key, framework in {**python_mapping, **js_mapping}.items():
                if key in dep:
                    frameworks.append(framework)
        
        # Check for Docker
        if 'dockerfile' in file_names or 'docker-compose.yml' in file_names:
            frameworks.append('Docker')
        
        return list(set(frameworks))
    
    def _has_tests(self, structure: List[Dict]) -> bool:
        """Check if repository has tests directory"""
        test_indicators = {'test', 'tests', 'spec', 'specs', '__tests__'}
        return any(
            item['name'].lower() in test_indicators 
            for item in structure if item['type'] == 'dir'
        )
    
    def _has_ci(self, structure: List[Dict]) -> bool:
        """Check for CI/CD configuration"""
        ci_indicators = {'.github', '.gitlab-ci.yml', '.travis.yml', 
                        'azure-pipelines.yml', '.circleci', 'Jenkinsfile'}
        return any(item['name'] in ci_indicators for item in structure)
    
    def _has_docker(self, structure: List[Dict]) -> bool:
        """Check for Docker configuration"""
        docker_files = {'dockerfile', 'docker-compose.yml', 'docker-compose.yaml'}
        return any(item['name'].lower() in docker_files for item in structure)
    
    def _has_docs(self, structure: List[Dict]) -> bool:
        """Check for documentation directory"""
        doc_dirs = {'docs', 'doc', 'documentation'}
        return any(
            item['name'].lower() in doc_dirs 
            for item in structure if item['type'] == 'dir'
        )
    
    def _parse_requirements(self, content: str) -> List[str]:
        """Parse Python requirements.txt"""
        deps = []
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('-'):
                match = re.match(r'^([a-zA-Z0-9_\-\.]+)', line)
                if match:
                    deps.append(match.group(1))
        return deps[:15]
    
    def _parse_package_json(self, content: str) -> List[str]:
        """Parse package.json dependencies"""
        import json
        deps = []
        try:
            data = json.loads(content)
            if 'dependencies' in data:
                deps.extend(list(data['dependencies'].keys())[:10])
            if 'devDependencies' in data:
                deps.extend(list(data['devDependencies'].keys())[:5])
        except Exception:
            pass
        return deps[:15]
    
    def _parse_gemfile(self, content: str) -> List[str]:
        """Parse Ruby Gemfile"""
        deps = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('gem '):
                match = re.search(r"gem\s+['\"]([^'\"]+)['\"]", line)
                if match:
                    deps.append(match.group(1))
        return deps[:15]
