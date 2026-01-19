"""
Discovery Service - Repository discovery and filtering

It handles:
- Filtering and sorting repositories
- Aggregating repository statistics
"""

from typing import List, Dict, Optional


class DiscoveryService:
    """Service that handles repository discovery and filtering"""
    
    def __init__(self):
        """Initialize Discovery Service"""
        pass
    
    def discover(self, repositories: List[Dict], 
                 filter_language: Optional[str] = None,
                 filter_name: Optional[str] = None,
                 include_private: bool = True,
                 include_forks: bool = True) -> List[Dict]:
        """
        Filter and process repositories based on criteria
        
        Args:
            repositories: Raw repository list from GitHubService
            filter_language: Filter by programming language
            filter_name: Filter by name (partial match, case-insensitive)
            include_private: Include private repositories
            include_forks: Include forked repositories
            
        Returns:
            Filtered and processed list of repositories
        """
        filtered = repositories.copy()
        
        # Apply language filter
        if filter_language:
            filtered = [r for r in filtered if r.get('language') == filter_language]
        
        # Apply name filter
        if filter_name:
            name_lower = filter_name.lower()
            filtered = [r for r in filtered 
                       if name_lower in r.get('name', '').lower()]
        
        # Apply privacy filter
        if not include_private:
            filtered = [r for r in filtered if not r.get('private', False)]
        
        return filtered
    
    def sort_repositories(self, repositories: List[Dict], 
                         sort_by: str = 'updated_at',
                         reverse: bool = True) -> List[Dict]:
        """
        Sort repositories by specified field
        
        Args:
            repositories: List of repositories
            sort_by: Field to sort by ('stars', 'updated_at', 'name')
            reverse: Descending order if True
        """
        valid_fields = {'stars', 'updated_at', 'name', 'forks'}
        if sort_by not in valid_fields:
            sort_by = 'updated_at'
        
        return sorted(repositories, key=lambda x: x.get(sort_by, 0), reverse=reverse)
    
    def get_language_stats(self, repositories: List[Dict]) -> Dict[str, int]:
        """
        Aggregate programming language statistics across repositories
        
        Returns:
            Dict mapping language to count of repositories
        """
        stats = {}
        for repo in repositories:
            lang = repo.get('language', 'Unknown')
            if lang and lang != 'Unknown':
                stats[lang] = stats.get(lang, 0) + 1
        
        # Sort by count descending
        return dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))
    
    def get_summary(self, repositories: List[Dict]) -> Dict:
        """
        Generate summary statistics for repository list
        
        Returns:
            Summary dict with total counts and stats
        """
        total = len(repositories)
        public = sum(1 for r in repositories if not r.get('private', False))
        private = total - public
        total_stars = sum(r.get('stars', 0) for r in repositories)
        
        return {
            'total': total,
            'public': public,
            'private': private,
            'total_stars': total_stars,
            'languages': self.get_language_stats(repositories)
        }
