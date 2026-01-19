"""
GitHub Service - Handles ALL GitHub API operations

This service is responsible for:
- Authentication and connection
- Fetching repositories and their metadata
- Reading file contents
- Committing files
- Creating branches and pull requests
"""

from github import Github, GithubException
from typing import List, Dict, Optional
import base64


class GitHubService:
    """Service for ALL GitHub API interactions"""
    
    def __init__(self, access_token: str):
        """
        Initialize GitHub service with access token
        
        Required token scopes:
        - repo (full control of private repositories - includes read/write)
        - read:user (read user profile data)
        """
        self.github = Github(access_token)
        self.user = self.github.get_user()
        self._token = access_token
    
    def get_authenticated_user(self) -> Dict:
        """Get authenticated user info"""
        return {
            'login': self.user.login,
            'name': self.user.name,
            'avatar_url': self.user.avatar_url,
            'public_repos': self.user.public_repos,
            'private_repos': self.user.owned_private_repos
        }
    
    def fetch_all_repositories(self) -> List[Dict]:
        """
        Fetch all repositories for the authenticated user
        
        Returns:
            List of repository dictionaries with metadata
        """
        repos = []
        try:
            for repo in self.user.get_repos():
                # Check if README exists
                has_readme = False
                try:
                    repo.get_contents('README.md')
                    has_readme = True
                except:
                    pass
                
                repos.append({
                    'name': repo.name,
                    'full_name': repo.full_name,
                    'description': repo.description or 'No description',
                    'language': repo.language or 'Unknown',
                    'stars': repo.stargazers_count,
                    'forks': repo.forks_count,
                    'updated_at': repo.updated_at,  # Keep as datetime object
                    'html_url': repo.html_url,
                    'default_branch': repo.default_branch,
                    'topics': repo.get_topics(),
                    'private': repo.private,
                    'size': repo.size,
                    'open_issues': repo.open_issues_count,
                    'has_readme': has_readme
                })
        except GithubException as e:
            raise Exception(f"Failed to fetch repositories: {e.data.get('message', str(e))}")
        
        return repos
    
    def get_repository(self, repo_full_name: str):
        """Get a specific repository object"""
        try:
            return self.github.get_repo(repo_full_name)
        except GithubException as e:
            raise Exception(f"Repository not found: {repo_full_name}")
    
    def get_repository_languages(self, repo_full_name: str) -> Dict[str, int]:
        """Get programming languages used in repository with byte counts"""
        try:
            repo = self.get_repository(repo_full_name)
            return repo.get_languages()
        except Exception:
            return {}
    
    def get_file_content(self, repo_full_name: str, file_path: str, 
                        branch: str = None) -> Optional[str]:
        """
        Get content of a file from repository
        
        Args:
            repo_full_name: Full repository name (owner/repo)
            file_path: Path to file in repository
            branch: Branch name (defaults to default branch)
            
        Returns:
            File content as string or None if not found
        """
        try:
            repo = self.get_repository(repo_full_name)
            branch = branch or repo.default_branch
            content = repo.get_contents(file_path, ref=branch)
            
            if content.encoding == 'base64':
                return base64.b64decode(content.content).decode('utf-8')
            return content.decoded_content.decode('utf-8')
        except GithubException:
            return None
    
    def get_directory_contents(self, repo_full_name: str, path: str = "", 
                               branch: str = None) -> List[Dict]:
        """
        Get contents of a directory in repository
        
        Returns:
            List of files and directories with metadata
        """
        try:
            repo = self.get_repository(repo_full_name)
            branch = branch or repo.default_branch
            contents = repo.get_contents(path, ref=branch)
            
            items = []
            for content in contents:
                items.append({
                    'name': content.name,
                    'path': content.path,
                    'type': content.type,  # 'file' or 'dir'
                    'size': content.size if content.type == 'file' else 0
                })
            
            return items
        except GithubException:
            return []
    
    def commit_file(self, repo_full_name: str, file_path: str, content: str,
                   commit_message: str, branch: str = None) -> Dict:
        """
        Commit a file to repository (create or update)
        
        Args:
            repo_full_name: Full repository name
            file_path: Path where file should be committed
            content: File content
            commit_message: Commit message
            branch: Branch name (defaults to default branch)
            
        Returns:
            Dict with commit info or raises exception
        """
        try:
            repo = self.get_repository(repo_full_name)
            branch = branch or repo.default_branch
            
            # Check if file exists
            try:
                existing_file = repo.get_contents(file_path, ref=branch)
                # Update existing file
                result = repo.update_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    sha=existing_file.sha,
                    branch=branch
                )
                return {
                    'action': 'updated',
                    'commit_sha': result['commit'].sha,
                    'commit_url': result['commit'].html_url
                }
            except GithubException:
                # Create new file
                result = repo.create_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    branch=branch
                )
                return {
                    'action': 'created',
                    'commit_sha': result['commit'].sha,
                    'commit_url': result['commit'].html_url
                }
                
        except GithubException as e:
            raise Exception(f"Failed to commit file: {e.data.get('message', str(e))}")
    
    def create_branch(self, repo_full_name: str, branch_name: str,
                     from_branch: str = None) -> bool:
        """
        Create a new branch from existing branch
        
        Returns:
            True if successful
        """
        try:
            repo = self.get_repository(repo_full_name)
            from_branch = from_branch or repo.default_branch
            source = repo.get_branch(from_branch)
            
            repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=source.commit.sha
            )
            return True
        except GithubException as e:
            raise Exception(f"Failed to create branch: {e.data.get('message', str(e))}")
    
    def create_pull_request(self, repo_full_name: str, title: str, body: str,
                           head_branch: str, base_branch: str = None) -> Dict:
        """
        Create a pull request
        
        Returns:
            Dict with PR info
        """
        try:
            repo = self.get_repository(repo_full_name)
            base_branch = base_branch or repo.default_branch
            
            pr = repo.create_pull(
                title=title,
                body=body,
                head=head_branch,
                base=base_branch
            )
            
            return {
                'number': pr.number,
                'html_url': pr.html_url,
                'state': pr.state
            }
        except GithubException as e:
            raise Exception(f"Failed to create PR: {e.data.get('message', str(e))}")

