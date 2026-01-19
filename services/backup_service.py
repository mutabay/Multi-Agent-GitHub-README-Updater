"""
Backup Service - Handles local file backup operations

This service is responsible for:
- Saving README backups to local filesystem
- Listing and retrieving backups
- Managing backup lifecycle (delete old backups)
"""

import os
from datetime import datetime
from typing import Optional, List, Dict


class BackupService:
    """Service for managing local README backups"""
    
    def __init__(self, backup_dir: str = None):
        """
        Initialize backup service
        
        Args:
            backup_dir: Directory to store backups (defaults to ./backups)
        """
        if backup_dir is None:
            backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backups')
        
        self.backup_dir = backup_dir
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def save_backup(self, repo_full_name: str, content: str) -> Dict:
        """
        Save a README backup to local storage
        
        Args:
            repo_full_name: Full repository name (owner/repo)
            content: README content to backup
            
        Returns:
            Dict with backup info (path, filename, timestamp)
        """
        # Create safe filename from repo name
        safe_name = repo_full_name.replace('/', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{safe_name}_{timestamp}.md"
        filepath = os.path.join(self.backup_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            'filename': filename,
            'path': filepath,
            'repo': repo_full_name,
            'timestamp': timestamp,
            'size': len(content)
        }
    
    def get_all_backups(self) -> List[Dict]:
        """
        Get list of all backups
        
        Returns:
            List of backup metadata sorted by date (newest first)
        """
        backups = []
        
        if not os.path.exists(self.backup_dir):
            return backups
        
        for filename in os.listdir(self.backup_dir):
            if not filename.endswith('.md'):
                continue
            
            filepath = os.path.join(self.backup_dir, filename)
            stat = os.stat(filepath)
            
            # Parse repo name from filename (format: owner_repo_timestamp.md)
            # e.g., "bayram_my-repo_20240101_120000.md" -> "bayram/my-repo"
            parts = filename.rsplit('_', 2)
            if len(parts) >= 3:
                # Extract owner_repo part and convert back
                owner_repo_part = filename.rsplit('_', 2)[0]
                # Find the first underscore to split owner and repo
                first_underscore = owner_repo_part.find('_')
                if first_underscore > 0:
                    owner = owner_repo_part[:first_underscore]
                    repo = owner_repo_part[first_underscore + 1:]
                    repo_name = f"{owner}/{repo}"
                else:
                    repo_name = owner_repo_part
            else:
                repo_name = filename.replace('.md', '')
            
            # Read preview (first 500 chars)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    preview = f.read(500)
            except Exception:
                preview = "Unable to load preview"
            
            backups.append({
                'id': filename,  # Use filename as ID
                'filename': filename,
                'path': filepath,
                'repo_name': repo_name,  # Template expects repo_name
                'preview': preview,
                'size': stat.st_size,
                'size_kb': round(stat.st_size / 1024, 2),
                'timestamp': datetime.fromtimestamp(stat.st_mtime),  # datetime object for template
                'created_at': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['timestamp'], reverse=True)
        return backups
    
    def get_backups_for_repo(self, repo_full_name: str) -> List[Dict]:
        """Get all backups for a specific repository"""
        safe_name = repo_full_name.replace('/', '_')
        all_backups = self.get_all_backups()
        return [b for b in all_backups if b['filename'].startswith(safe_name)]
    
    def read_backup(self, backup_id: str) -> Optional[Dict]:
        """
        Read backup file content by ID (filename)
        
        Args:
            backup_id: Backup ID (filename)
            
        Returns:
            Dict with content and metadata, or None if not found
        """
        filepath = os.path.join(self.backup_dir, backup_id)
        
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse repo name from filename
        parts = backup_id.rsplit('_', 2)
        if len(parts) >= 3:
            owner_repo_part = backup_id.rsplit('_', 2)[0]
            first_underscore = owner_repo_part.find('_')
            if first_underscore > 0:
                owner = owner_repo_part[:first_underscore]
                repo = owner_repo_part[first_underscore + 1:]
                repo_name = f"{owner}/{repo}"
            else:
                repo_name = owner_repo_part
        else:
            repo_name = backup_id.replace('.md', '')
        
        return {
            'id': backup_id,
            'content': content,
            'repo_name': repo_name
        }
    
    def delete_backup(self, backup_id: str) -> bool:
        """
        Delete a backup file
        
        Args:
            backup_id: Backup ID (filename)
        
        Returns:
            True if deleted successfully
        """
        filepath = os.path.join(self.backup_dir, backup_id)
        
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    
    def cleanup_old_backups(self, keep_last: int = 5) -> int:
        """
        Delete old backups, keeping only the most recent ones per repo
        
        Args:
            keep_last: Number of backups to keep per repository
            
        Returns:
            Number of backups deleted
        """
        deleted = 0
        
        # Group backups by repository
        backups_by_repo = {}
        for backup in self.get_all_backups():
            repo = backup['repo']
            if repo not in backups_by_repo:
                backups_by_repo[repo] = []
            backups_by_repo[repo].append(backup)
        
        # Delete excess backups for each repo
        for repo, backups in backups_by_repo.items():
            # Already sorted newest first
            for backup in backups[keep_last:]:
                if self.delete_backup(backup['filename']):
                    deleted += 1
        
        return deleted

