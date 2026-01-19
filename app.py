"""
Multi-Agent GitHub README Updater - Flask Application

This is the main entry point for the web application.
It coordinates a multi-agent pipeline:
- Services: Handle external operations (GitHub API, backups, LLM)
- Agents: LLM-powered agents that collaborate on README generation
  - AnalyzerAgent: Intelligent project analysis
  - GeneratorAgent: README content generation  
  - ReviewerAgent: Quality review and improvement
"""

from flask import Flask, render_template, request, session, redirect, url_for, jsonify, flash
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Services (handle external operations - no LLM)
from services.github_service import GitHubService
from services.backup_service import BackupService
from services.llm_service import LLMService

# Import Agents (LLM-powered intelligent agents)
from agents.analyzer import AnalyzerAgent
from agents.generator import GeneratorAgent
from agents.reviewer import ReviewerAgent

# Import utility services (non-LLM)
from agents.discover import DiscoveryService
from agents.writer import WriterService

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# LLM Configuration - Supports multiple providers
# Provider Options:
#   - 'ollama' (default): Local models via Ollama
#   - 'openai': OpenAI GPT models (requires OPENAI_API_KEY)
#
# Environment Variables:
#   LLM_PROVIDER=ollama|openai (default: ollama)
#   OLLAMA_MODEL=llama3.1:8b (for Ollama)
#   OLLAMA_BASE_URL=http://localhost:11434 (for Ollama)
#   OPENAI_API_KEY=sk-... (for OpenAI)
#   OPENAI_MODEL=gpt-4|gpt-3.5-turbo (for OpenAI)
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'ollama')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')


# =============================================================================
# ROUTES
# =============================================================================

@app.route('/')
def index():
    """Home page - GitHub token input"""
    return render_template('index.html')


@app.route('/connect', methods=['POST'])
def connect():
    """Connect to GitHub with Personal Access Token"""
    github_token = request.form.get('github_token', '').strip()
    
    if not github_token:
        flash('Please provide a GitHub Personal Access Token', 'error')
        return redirect(url_for('index'))
    
    try:
        # Test token by initializing service
        github_service = GitHubService(github_token)
        user_info = github_service.get_authenticated_user()
        
        # Store in session
        session['github_token'] = github_token
        session['username'] = user_info['login']
        session['user_info'] = user_info
        
        flash(f"Connected as {user_info['login']}", 'success')
        return redirect(url_for('repositories'))
        
    except Exception as e:
        flash(f'Connection failed: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/disconnect')
def disconnect():
    """Disconnect from GitHub"""
    session.clear()
    flash('Disconnected from GitHub', 'info')
    return redirect(url_for('index'))


@app.route('/repositories')
def repositories():
    """List and filter repositories"""
    if 'github_token' not in session:
        flash('Please connect to GitHub first', 'error')
        return redirect(url_for('index'))
    
    try:
        # Initialize services
        github_service = GitHubService(session['github_token'])
        discovery_service = DiscoveryService()
        
        # Get all repositories from GitHub
        all_repos = github_service.fetch_all_repositories()
        
        # Get filter parameters
        filter_language = request.args.get('language') or None
        filter_name = request.args.get('name') or None
        
        # Apply filters
        repos = discovery_service.discover(
            repositories=all_repos,
            filter_language=filter_language,
            filter_name=filter_name
        )
        
        # Sort by most recently updated
        repos = discovery_service.sort_repositories(repos, sort_by='updated_at')
        
        # Get language statistics
        language_stats = discovery_service.get_language_stats(all_repos)
        summary = discovery_service.get_summary(all_repos)
        
        return render_template('repos.html',
            repositories=repos,
            language_stats=language_stats,
            summary=summary,
            username=session.get('username'),
            filter_language=filter_language,
            filter_name=filter_name
        )
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in /repositories: {error_details}")
        flash(f'Error loading repositories: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/generate', methods=['POST'])
def generate():
    """Generate README for selected repositories (AJAX endpoint)"""
    if 'github_token' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        selected_repos = request.json.get('repos', [])
        
        if not selected_repos:
            return jsonify({'error': 'No repositories selected'}), 400
        
        # Initialize services
        github_service = GitHubService(session['github_token'])
        backup_service = BackupService()
        
        # Initialize LLM service based on configuration
        llm_service = LLMService()  # Uses environment variables for provider/model
        
        # Initialize agents (multi-agent pipeline)
        analyzer_agent = AnalyzerAgent()
        generator_agent = GeneratorAgent()
        reviewer_agent = ReviewerAgent()
        
        results = []
        
        for repo_name in selected_repos:
            try:
                print(f"\n{'='*50}")
                print(f"🚀 Processing: {repo_name}")
                print(f"{'='*50}")
                
                # === SERVICE: Fetch data from GitHub ===
                print("📥 Fetching repository data from GitHub...")
                all_repos = github_service.fetch_all_repositories()
                repo_info = next((r for r in all_repos if r['full_name'] == repo_name), {})
                languages = github_service.get_repository_languages(repo_name)
                structure = github_service.get_directory_contents(repo_name)
                
                # Fetch relevant files for analysis
                file_contents = {}
                files_to_fetch = ['README.md', 'requirements.txt', 'package.json', 
                                 'pyproject.toml', 'Gemfile', 'Cargo.toml',
                                 'app.py', 'main.py', 'index.js', 'main.go']
                for fname in files_to_fetch:
                    content = github_service.get_file_content(repo_name, fname)
                    if content:
                        file_contents[fname] = content
                
                # === SERVICE: Backup existing README ===
                backup_info = None
                if 'README.md' in file_contents:
                    backup_info = backup_service.save_backup(repo_name, file_contents['README.md'])
                
                # === AGENT 1: Analyze repository (LLM-powered) ===
                print("\n🔬 AGENT 1: Analyzer Agent")
                analysis = analyzer_agent.analyze(
                    repo_info=repo_info,
                    languages=languages,
                    structure=structure,
                    file_contents=file_contents,
                    llm_service=llm_service  # Pass LLM for intelligent analysis
                )
                analysis['username'] = session.get('username', '')
                
                # === AGENT 2: Generate README (LLM-powered) ===
                print("\n✍️ AGENT 2: Generator Agent")
                readme_content = generator_agent.generate(analysis, llm_service)
                
                # === AGENT 3: Review and improve (LLM-powered) ===
                print("\n🔍 AGENT 3: Reviewer Agent")
                readme_content = reviewer_agent.review(readme_content, analysis, llm_service)
                
                # Quality check
                quality = reviewer_agent.quick_check(readme_content)
                print(f"📊 Quality Score: {quality['quality_score']}/100")
                
                results.append({
                    'repo_name': repo_name,
                    'success': True,
                    'readme': readme_content,
                    'analysis': analysis,
                    'backup': backup_info,
                    'quality_score': quality['quality_score']
                })
                
                print(f"✅ Completed: {repo_name}\n")
                
            except Exception as e:
                print(f"❌ Failed: {repo_name} - {str(e)}")
                results.append({
                    'repo_name': repo_name,
                    'success': False,
                    'error': str(e)
                })
        
        # Store results in session for preview page
        session['generation_results'] = results
        
        return jsonify({
            'success': True,
            'count': len([r for r in results if r['success']]),
            'results': results,
            'redirect': url_for('preview')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/preview')
def preview():
    """Preview generated READMEs before committing"""
    if 'github_token' not in session:
        flash('Please connect to GitHub first', 'error')
        return redirect(url_for('index'))
    
    results = session.get('generation_results', [])
    
    if not results:
        flash('No READMEs to preview. Generate some first.', 'warning')
        return redirect(url_for('repositories'))
    
    return render_template('preview.html', results=results)


@app.route('/commit', methods=['POST'])
def commit():
    """Commit README to GitHub (AJAX endpoint)"""
    if 'github_token' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        repo_name = request.json.get('repo_name')
        readme_content = request.json.get('readme_content')
        create_pr = request.json.get('create_pr', False)
        
        if not repo_name or not readme_content:
            return jsonify({'error': 'Missing repo_name or readme_content'}), 400
        
        # Initialize services
        github_service = GitHubService(session['github_token'])
        writer_service = WriterService()
        
        # Write README to GitHub
        result = writer_service.write(
            repo_full_name=repo_name,
            readme_content=readme_content,
            github_service=github_service,
            create_pr=create_pr
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/backups')
def backups():
    """View all README backups"""
    if 'github_token' not in session:
        flash('Please connect to GitHub first', 'error')
        return redirect(url_for('index'))
    
    backup_service = BackupService()
    all_backups = backup_service.get_all_backups()
    
    return render_template('backups.html', backups=all_backups)


@app.route('/result')
def result():
    """Final result page"""
    repo_name = request.args.get('repo', '')
    method = request.args.get('method', 'direct')
    pr_url = request.args.get('pr_url', '')
    
    result_data = {
        'method': method,
        'pr_url': pr_url,
        'backup_created': True,  # Assume backup was created
        'commit_sha': '',  # Could track this in session
        'branch': 'main' if method == 'direct' else 'readme-update'
    }
    
    return render_template('result.html', repo_name=repo_name, result=result_data)


@app.route('/api/backup/<backup_id>')
def get_backup(backup_id):
    """Get backup content by ID"""
    if 'github_token' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    backup_service = BackupService()
    backup = backup_service.read_backup(backup_id)
    
    if backup:
        return jsonify(backup)
    return jsonify({'error': 'Backup not found'}), 404


@app.route('/restore_backup', methods=['POST'])
def restore_backup():
    """Restore a README from backup"""
    if 'github_token' not in session:
        flash('Please connect to GitHub first', 'error')
        return redirect(url_for('index'))
    
    backup_id = request.form.get('backup_id')
    
    if not backup_id:
        flash('No backup specified', 'error')
        return redirect(url_for('backups'))
    
    try:
        backup_service = BackupService()
        backup = backup_service.read_backup(backup_id)
        
        if not backup:
            flash('Backup not found', 'error')
            return redirect(url_for('backups'))
        
        github_service = GitHubService(session['github_token'])
        writer_service = WriterService()
        
        result = writer_service.write(
            repo_full_name=backup['repo_name'],
            readme_content=backup['content'],
            github_service=github_service,
            create_pr=False,
            commit_message='Restore README from backup'
        )
        
        if result.get('success'):
            flash(f"README restored for {backup['repo_name']}", 'success')
        else:
            flash(f"Failed to restore: {result.get('error')}", 'error')
            
    except Exception as e:
        flash(f'Restore failed: {str(e)}', 'error')
    
    return redirect(url_for('backups'))


@app.route('/delete_backup', methods=['POST'])
def delete_backup():
    """Delete a backup"""
    if 'github_token' not in session:
        flash('Please connect to GitHub first', 'error')
        return redirect(url_for('index'))
    
    backup_id = request.form.get('backup_id')
    
    if not backup_id:
        flash('No backup specified', 'error')
        return redirect(url_for('backups'))
    
    try:
        backup_service = BackupService()
        success = backup_service.delete_backup(backup_id)
        
        if success:
            flash('Backup deleted', 'success')
        else:
            flash('Failed to delete backup', 'error')
            
    except Exception as e:
        flash(f'Delete failed: {str(e)}', 'error')
    
    return redirect(url_for('backups'))


@app.route('/health')
def health():
    """Health check endpoint"""
    llm_service = LLMService(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
    status = llm_service.test_connection()
    
    return jsonify({
        'status': 'healthy' if status['connected'] else 'degraded',
        'ollama': status,
        'model': OLLAMA_MODEL
    })


# =============================================================================
# TEMPLATE HELPERS
# =============================================================================

@app.context_processor
def utility_processor():
    """Add utility functions to templates"""
    from datetime import datetime
    
    def get_language_color(language):
        """Get color for programming language"""
        colors = {
            'Python': '#3572A5',
            'JavaScript': '#f1e05a',
            'TypeScript': '#2b7489',
            'Java': '#b07219',
            'C++': '#f34b7d',
            'C': '#555555',
            'C#': '#178600',
            'Go': '#00ADD8',
            'Rust': '#dea584',
            'Ruby': '#701516',
            'PHP': '#4F5D95',
            'Swift': '#ffac45',
            'Kotlin': '#A97BFF',
            'Dart': '#00B4AB',
            'HTML': '#e34c26',
            'CSS': '#563d7c',
            'Shell': '#89e051',
            'Jupyter Notebook': '#DA5B0B',
        }
        return colors.get(language, '#8b949e')
    
    return dict(
        get_language_color=get_language_color,
        now=datetime.now
    )


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    # Ensure backup directory exists
    os.makedirs('backups', exist_ok=True)
    
    app.run(debug=True, port=5000)
