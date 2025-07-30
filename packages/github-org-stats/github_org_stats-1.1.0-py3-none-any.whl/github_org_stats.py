#!/usr/bin/env python3
"""
GitHub Organization Statistics Tool
==================================

A comprehensive tool for analyzing GitHub organization statistics including:
- Repository metrics and analysis
- Contributor activity and engagement
- Code quality and security insights
- Multi-organization support with GitHub Apps

This is an open-source tool for analyzing GitHub organizations and repositories.
It provides detailed insights into repository activity, contributor engagement,
code quality metrics, and organizational health indicators.

Author: Zohar Babin
License: MIT
Version: 1.1.0
Homepage: https://github.com/zoharbabin/github-org-stats/
"""

# =============================================================================
# IMPORTS AND DEPENDENCIES
# =============================================================================

import argparse
import logging
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
import json
import time
from pathlib import Path
import re
from collections import defaultdict
import base64
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import signal
from contextlib import contextmanager
import pytz
from datetime import timezone

# Third-party imports
try:
    import requests
    import pandas as pd
    import numpy as np
    from github import Github
    from github.GithubException import GithubException, RateLimitExceededException, UnknownObjectException
    import jwt
    from tqdm import tqdm
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils.dataframe import dataframe_to_rows
    from openpyxl.worksheet.datavalidation import DataValidation
except ImportError as e:
    print(f"Error: Missing required dependency: {e}")
    print("Please install required packages: pip install requests pandas PyGithub PyJWT tqdm openpyxl pytz numpy")
    sys.exit(1)


# =============================================================================
# CONFIGURATION AND CONSTANTS
# =============================================================================

# API Configuration
GITHUB_API_BASE_URL = "https://api.github.com"
DEFAULT_RATE_LIMIT_DELAY = 1.0
MAX_RETRIES = 3
RETRY_BACKOFF_FACTOR = 2.0
RATE_LIMIT_BUFFER = 100  # Keep this many requests in reserve

# Output Configuration
DEFAULT_OUTPUT_DIR = "output"
DEFAULT_LOG_LEVEL = "INFO"

# Data Collection Defaults
DEFAULT_DAYS_BACK = 30
DEFAULT_MAX_REPOS = 100

# Caching for forbidden operations
FORBIDDEN_CACHE = set()

# Bot account patterns for detection
BOT_PATTERNS = [
    r'.*bot$',
    r'.*\[bot\]$',
    r'^dependabot.*',
    r'^renovate.*',
    r'^github-actions.*',
    r'^codecov.*',
    r'^greenkeeper.*',
    r'^snyk.*',
    r'^whitesource.*',
    r'^sonarcloud.*',
    r'^imgbot$',
    r'^allcontributors.*',
    r'^semantic-release.*',
    r'^stale.*',
    r'^mergify.*',
    r'^pre-commit-ci.*'
]

# Compile bot patterns for efficiency
COMPILED_BOT_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in BOT_PATTERNS]

# Excel Configuration
EXCEL_BATCH_SIZE = 100
EXCEL_MAX_CELL_LENGTH = 32767
EXCEL_SHEET_MAX_ROWS = 1048576
DEFAULT_TIMEZONE = 'UTC'

# Progress tracking
PROGRESS_UPDATE_INTERVAL = 10


# =============================================================================
# GITHUB APP AUTHENTICATION SYSTEM
# =============================================================================

def generate_jwt(app_id: int, private_key: str) -> str:
    """
    Generate a JWT token for GitHub App authentication.
    
    Args:
        app_id: GitHub App ID
        private_key: Private key content (PEM format)
    
    Returns:
        JWT token string
    """
    now = int(time.time())
    payload = {
        'iat': now - 60,  # Issued at time (60 seconds ago to account for clock skew)
        'exp': now + 600,  # Expires in 10 minutes
        'iss': app_id     # Issuer (GitHub App ID)
    }
    
    return jwt.encode(payload, private_key, algorithm='RS256')


class GitHubAppTokenManager:
    """
    Manages GitHub App authentication tokens with caching and automatic refresh.
    """
    
    def __init__(self, app_id: int, private_key: str):
        """
        Initialize the token manager.
        
        Args:
            app_id: GitHub App ID
            private_key: Private key content (PEM format)
        """
        self.app_id = app_id
        self.private_key = private_key
        self._installation_tokens = {}
        self._jwt_token = None
        self._jwt_expires_at = 0
    
    def get_jwt_token(self) -> str:
        """
        Get a valid JWT token, generating a new one if needed.
        
        Returns:
            JWT token string
        """
        now = time.time()
        if not self._jwt_token or now >= self._jwt_expires_at - 60:  # Refresh 1 minute early
            self._jwt_token = generate_jwt(self.app_id, self.private_key)
            self._jwt_expires_at = now + 600  # JWT expires in 10 minutes
        
        return self._jwt_token
    
    def get_installation_token(self, installation_id: int) -> str:
        """
        Get an installation access token, using cache if available.
        
        Args:
            installation_id: GitHub App installation ID
        
        Returns:
            Installation access token
        """
        now = time.time()
        
        # Check if we have a cached token that's still valid
        if installation_id in self._installation_tokens:
            token_info = self._installation_tokens[installation_id]
            if now < token_info['expires_at'] - 300:  # Refresh 5 minutes early
                return token_info['token']
        
        # Get a new installation token
        jwt_token = self.get_jwt_token()
        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.post(
            f'{GITHUB_API_BASE_URL}/app/installations/{installation_id}/access_tokens',
            headers=headers
        )
        response.raise_for_status()
        
        token_data = response.json()
        expires_at = datetime.fromisoformat(
            token_data['expires_at'].replace('Z', '+00:00')
        ).timestamp()
        
        # Cache the token
        self._installation_tokens[installation_id] = {
            'token': token_data['token'],
            'expires_at': expires_at
        }
        
        return token_data['token']


# =============================================================================
# AUTHENTICATION FUNCTIONS
# =============================================================================

def load_github_app_creds() -> Tuple[Optional[int], Optional[str]]:
    """
    Load GitHub App credentials from environment variables or CLI arguments.
    
    Returns:
        Tuple of (app_id, private_key_content) or (None, None) if not available
    """
    app_id = os.getenv('GITHUB_APP_ID')
    private_key_path = os.getenv('GITHUB_PRIVATE_KEY_PATH')
    
    if app_id and private_key_path:
        try:
            with open(private_key_path, 'r') as f:
                private_key = f.read()
            return int(app_id), private_key
        except (FileNotFoundError, ValueError) as e:
            logging.getLogger('github_org_stats').warning(
                f"Failed to load GitHub App credentials from environment: {e}"
            )
    
    return None, None


def parse_installation_ids(installation_str: str) -> Dict[str, int]:
    """
    Parse installation IDs from string format.
    
    Supports formats:
    - Single ID: "12345"
    - Multiple IDs: "org1:12345,org2:67890"
    
    Args:
        installation_str: Installation ID string
    
    Returns:
        Dictionary mapping organization names to installation IDs
    """
    installations = {}
    
    if ',' in installation_str:
        # Multiple installations format: "org1:id1,org2:id2"
        for pair in installation_str.split(','):
            if ':' in pair:
                org, install_id = pair.strip().split(':', 1)
                installations[org.strip()] = int(install_id.strip())
            else:
                # Fallback: treat as single ID for default org
                installations['default'] = int(pair.strip())
    else:
        # Single installation ID
        if ':' in installation_str:
            org, install_id = installation_str.split(':', 1)
            installations[org.strip()] = int(install_id.strip())
        else:
            installations['default'] = int(installation_str)
    
    return installations


def get_installation_id(org_name: str, token_manager: GitHubAppTokenManager,
                       specified_installations: Optional[Dict[str, int]] = None) -> int:
    """
    Get the installation ID for a specific organization.
    
    Args:
        org_name: Organization name
        token_manager: GitHub App token manager
        specified_installations: Pre-specified installation mappings
    
    Returns:
        Installation ID for the organization
    
    Raises:
        ValueError: If installation ID cannot be determined
    """
    # Check if installation ID was explicitly specified
    if specified_installations:
        if org_name in specified_installations:
            return specified_installations[org_name]
        elif 'default' in specified_installations:
            return specified_installations['default']
    
    # Query GitHub API to find installation for organization
    jwt_token = token_manager.get_jwt_token()
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    response = requests.get(f'{GITHUB_API_BASE_URL}/app/installations', headers=headers)
    response.raise_for_status()
    
    installations = response.json()
    for installation in installations:
        if installation['account']['login'].lower() == org_name.lower():
            return installation['id']
    
    raise ValueError(f"No GitHub App installation found for organization: {org_name}")


def get_installation_token(app_id: int, private_key: str, installation_id: int) -> str:
    """
    Get an installation access token for GitHub App authentication.
    
    Args:
        app_id: GitHub App ID
        private_key: Private key content (PEM format)
        installation_id: Installation ID
    
    Returns:
        Installation access token
    """
    token_manager = GitHubAppTokenManager(app_id, private_key)
    return token_manager.get_installation_token(installation_id)


def load_private_key(private_key_path: str) -> str:
    """
    Load and cache private key from file.
    
    Args:
        private_key_path: Path to private key file
    
    Returns:
        Private key content
    
    Raises:
        FileNotFoundError: If private key file doesn't exist
        ValueError: If private key format is invalid
    """
    if not os.path.exists(private_key_path):
        raise FileNotFoundError(f"Private key file not found: {private_key_path}")
    
    try:
        with open(private_key_path, 'r') as f:
            private_key = f.read()
        
        # Basic validation - check if it looks like a PEM key
        if not private_key.strip().startswith('-----BEGIN'):
            raise ValueError("Private key file does not appear to be in PEM format")
        
        return private_key
    except Exception as e:
        raise ValueError(f"Failed to load private key: {e}")


# =============================================================================
# RATE LIMITING & ERROR HANDLING
# =============================================================================

def print_rate_limit(github_client: Github) -> None:
    """
    Print current rate limit status.
    
    Args:
        github_client: GitHub client instance
    """
    try:
        rate_limit = github_client.get_rate_limit()
        core = rate_limit.core
        search = rate_limit.search
        
        logger = logging.getLogger('github_org_stats')
        logger.info(f"Rate Limit Status:")
        logger.info(f"  Core API: {core.remaining}/{core.limit} (resets at {core.reset})")
        logger.info(f"  Search API: {search.remaining}/{search.limit} (resets at {search.reset})")
        
    except Exception as e:
        logging.getLogger('github_org_stats').warning(f"Could not fetch rate limit: {e}")


def robust_github_call(func, *args, max_retries: int = MAX_RETRIES, **kwargs):
    """
    Execute a GitHub API call with robust error handling and retry logic.
    
    Args:
        func: Function to call
        *args: Positional arguments for the function
        max_retries: Maximum number of retry attempts
        **kwargs: Keyword arguments for the function
    
    Returns:
        Function result or None if all retries failed
    """
    logger = logging.getLogger('github_org_stats')
    
    for attempt in range(max_retries + 1):
        try:
            return func(*args, **kwargs)
            
        except RateLimitExceededException as e:
            if attempt < max_retries:
                wait_time = e.retry_after if hasattr(e, 'retry_after') else 60
                logger.warning(f"Rate limit exceeded. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            else:
                logger.error("Rate limit exceeded and max retries reached")
                return None
                
        except UnknownObjectException as e:
            # Don't retry for 404 errors
            logger.debug(f"Resource not found: {e}")
            return None
            
        except GithubException as e:
            if e.status == 403:
                # Forbidden - cache this to avoid repeated attempts
                cache_key = f"{func.__name__}:{str(args)}"
                FORBIDDEN_CACHE.add(cache_key)
                logger.debug(f"Access forbidden (cached): {e}")
                return None
            elif e.status >= 500 and attempt < max_retries:
                # Server error - retry with backoff
                wait_time = (RETRY_BACKOFF_FACTOR ** attempt) * DEFAULT_RATE_LIMIT_DELAY
                logger.warning(f"Server error {e.status}. Retrying in {wait_time:.1f}s...")
                time.sleep(wait_time)
                continue
            else:
                logger.error(f"GitHub API error: {e}")
                return None
                
        except Exception as e:
            if attempt < max_retries:
                wait_time = (RETRY_BACKOFF_FACTOR ** attempt) * DEFAULT_RATE_LIMIT_DELAY
                logger.warning(f"Unexpected error: {e}. Retrying in {wait_time:.1f}s...")
                time.sleep(wait_time)
                continue
            else:
                logger.error(f"Unexpected error after {max_retries} retries: {e}")
                return None
    
    return None


def gh_safe(github_client: Github, func, *args, **kwargs):
    """
    Wrapper for GitHub API calls with token refresh handling.
    
    Args:
        github_client: GitHub client instance
        func: Function to call
        *args: Positional arguments
        **kwargs: Keyword arguments
    
    Returns:
        Function result or None if failed
    """
    # Check if this operation is cached as forbidden
    cache_key = f"{func.__name__ if hasattr(func, '__name__') else str(func)}:{str(args)}"
    if cache_key in FORBIDDEN_CACHE:
        return None
    
    # Check rate limit before making call
    try:
        rate_limit = github_client.get_rate_limit()
        if rate_limit.core.remaining < RATE_LIMIT_BUFFER:
            logger = logging.getLogger('github_org_stats')
            reset_time = rate_limit.core.reset
            wait_time = (reset_time - datetime.now()).total_seconds() + 10
            if wait_time > 0:
                logger.warning(f"Rate limit low ({rate_limit.core.remaining}). Waiting {wait_time:.0f}s...")
                time.sleep(wait_time)
    except:
        pass  # Continue if rate limit check fails
    
    return robust_github_call(func, *args, **kwargs)


# =============================================================================
# BOT DETECTION AND FILTERING
# =============================================================================

def is_bot_account(username: str) -> bool:
    """
    Check if a username appears to be a bot account.
    
    Args:
        username: GitHub username to check
        
    Returns:
        True if username matches bot patterns
    """
    if not username:
        return False
    
    for pattern in COMPILED_BOT_PATTERNS:
        if pattern.match(username):
            return True
    
    return False


def filter_bot_contributors(contributors: List[Dict[str, Any]], exclude_bots: bool = True) -> List[Dict[str, Any]]:
    """
    Filter bot accounts from contributors list.
    
    Args:
        contributors: List of contributor dictionaries
        exclude_bots: Whether to exclude bot accounts
        
    Returns:
        Filtered contributors list
    """
    if not exclude_bots:
        return contributors
    
    return [
        contrib for contrib in contributors
        if not is_bot_account(contrib.get('login', ''))
    ]


# =============================================================================
# GITHUB API HELPER FUNCTIONS
# =============================================================================

def safe_get_commits(repo, since_date: datetime = None) -> List[Any]:
    """
    Safely get commits from a repository, handling empty repositories.
    
    Args:
        repo: GitHub repository object
        since_date: Optional date to filter commits from
    
    Returns:
        List of commit objects or empty list if failed
    """
    try:
        commits_kwargs = {}
        if since_date:
            commits_kwargs['since'] = since_date
            
        commits = list(repo.get_commits(**commits_kwargs))
        return commits
    except (GithubException, Exception):
        return []


def get_commit_stats(repo, days_back: int = 30) -> Dict[str, Any]:
    """
    Get commit statistics with author breakdown.
    
    Args:
        repo: GitHub repository object
        days_back: Number of days to look back
    
    Returns:
        Dictionary with commit statistics
    """
    since_date = datetime.now() - timedelta(days=days_back)
    commits = safe_get_commits(repo, since_date)
    
    stats = {
        'total_commits': len(commits),
        'unique_authors': set(),
        'commit_authors': defaultdict(int),
        'commits_by_day': defaultdict(int)
    }
    
    for commit in commits:
        if commit.author:
            author = commit.author.login
            stats['unique_authors'].add(author)
            stats['commit_authors'][author] += 1
        
        commit_date = commit.commit.author.date.strftime('%Y-%m-%d')
        stats['commits_by_day'][commit_date] += 1
    
    stats['unique_authors'] = len(stats['unique_authors'])
    stats['commit_authors'] = dict(stats['commit_authors'])
    stats['commits_by_day'] = dict(stats['commits_by_day'])
    
    return stats


def get_code_bytes(repo) -> Dict[str, int]:
    """
    Get language statistics for a repository.
    
    Args:
        repo: GitHub repository object
    
    Returns:
        Dictionary mapping language names to byte counts
    """
    try:
        languages = repo.get_languages()
        return dict(languages) if languages else {}
    except (GithubException, Exception):
        return {}


def get_repo_topics(repo) -> List[str]:
    """
    Get repository topics.
    
    Args:
        repo: GitHub repository object
    
    Returns:
        List of topic strings
    """
    try:
        return list(repo.get_topics()) if hasattr(repo, 'get_topics') else []
    except (GithubException, Exception):
        return []


def get_submodules_info(repo) -> List[Dict[str, str]]:
    """
    Parse .gitmodules file to get submodule information.
    
    Args:
        repo: GitHub repository object
    
    Returns:
        List of dictionaries with submodule info
    """
    try:
        gitmodules = repo.get_contents('.gitmodules')
        content = base64.b64decode(gitmodules.content).decode('utf-8')
        
        submodules = []
        current_submodule = {}
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('[submodule'):
                if current_submodule:
                    submodules.append(current_submodule)
                current_submodule = {'name': line.split('"')[1] if '"' in line else ''}
            elif '=' in line and current_submodule:
                key, value = line.split('=', 1)
                current_submodule[key.strip()] = value.strip()
        
        if current_submodule:
            submodules.append(current_submodule)
            
        return submodules
    except (GithubException, Exception):
        return []


def get_sbom_deps(repo) -> Dict[str, List[str]]:
    """
    Get dependency information from common dependency files.
    
    Args:
        repo: GitHub repository object
    
    Returns:
        Dictionary mapping dependency file types to lists of dependencies
    """
    deps = {}
    
    # Common dependency files to check
    dep_files = {
        'package.json': 'npm',
        'requirements.txt': 'pip',
        'Gemfile': 'gem',
        'pom.xml': 'maven',
        'build.gradle': 'gradle',
        'Cargo.toml': 'cargo',
        'go.mod': 'go'
    }
    
    for filename, dep_type in dep_files.items():
        try:
            file_content = repo.get_contents(filename)
            content = base64.b64decode(file_content.content).decode('utf-8')
            
            if dep_type == 'npm':
                # Parse package.json
                try:
                    import json
                    pkg_data = json.loads(content)
                    deps[dep_type] = list(pkg_data.get('dependencies', {}).keys())
                except:
                    deps[dep_type] = []
            elif dep_type == 'pip':
                # Parse requirements.txt
                deps[dep_type] = [line.split('==')[0].split('>=')[0].split('<=')[0].strip()
                                 for line in content.split('\n')
                                 if line.strip() and not line.startswith('#')]
            else:
                # For other types, just note that the file exists
                deps[dep_type] = ['present']
                
        except (GithubException, Exception):
            continue
    
    return deps


def get_primary_contributors(repo, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get top contributors to a repository.
    
    Args:
        repo: GitHub repository object
        limit: Maximum number of contributors to return
    
    Returns:
        List of contributor dictionaries
    """
    try:
        contributors = list(repo.get_contributors())[:limit]
        return [
            {
                'login': contrib.login,
                'contributions': contrib.contributions,
                'avatar_url': contrib.avatar_url,
                'html_url': contrib.html_url
            }
            for contrib in contributors
        ]
    except (GithubException, Exception):
        return []


def get_repo_teams(repo) -> List[Dict[str, str]]:
    """
    Get teams with access to a repository.
    
    Args:
        repo: GitHub repository object
    
    Returns:
        List of team dictionaries
    """
    try:
        teams = list(repo.get_teams())
        return [
            {
                'name': team.name,
                'slug': team.slug,
                'permission': getattr(team, 'permission', 'unknown')
            }
            for team in teams
        ]
    except (GithubException, Exception):
        return []


def get_repo_collaborators(repo) -> List[Dict[str, str]]:
    """
    Get collaborators for a repository.
    
    Args:
        repo: GitHub repository object
    
    Returns:
        List of collaborator dictionaries
    """
    try:
        collaborators = list(repo.get_collaborators())
        return [
            {
                'login': collab.login,
                'permissions': getattr(collab, 'permissions', {}),
                'role': getattr(collab, 'role_name', 'unknown')
            }
            for collab in collaborators
        ]
    except (GithubException, Exception):
        return []


def get_repo_admins(repo) -> List[str]:
    """
    Get admin users for a repository.
    
    Args:
        repo: GitHub repository object
    
    Returns:
        List of admin usernames
    """
    try:
        collaborators = get_repo_collaborators(repo)
        return [
            collab['login']
            for collab in collaborators
            if collab.get('permissions', {}).get('admin', False)
        ]
    except (GithubException, Exception):
        return []


def get_branches_tags_counts(repo) -> Dict[str, int]:
    """
    Count branches and tags in a repository.
    
    Args:
        repo: GitHub repository object
    
    Returns:
        Dictionary with branch and tag counts
    """
    try:
        branches = list(repo.get_branches())
        tags = list(repo.get_tags())
        
        return {
            'branches_count': len(branches),
            'tags_count': len(tags)
        }
    except (GithubException, Exception):
        return {'branches_count': 0, 'tags_count': 0}


def get_release_info(repo) -> Dict[str, Any]:
    """
    Get latest release information.
    
    Args:
        repo: GitHub repository object
    
    Returns:
        Dictionary with release information
    """
    try:
        releases = list(repo.get_releases())
        if releases:
            latest = releases[0]
            return {
                'latest_release': latest.tag_name,
                'release_date': latest.published_at.isoformat() if latest.published_at else None,
                'release_url': latest.html_url,
                'total_releases': len(releases)
            }
        else:
            return {'latest_release': None, 'total_releases': 0}
    except (GithubException, Exception):
        return {'latest_release': None, 'total_releases': 0}


def get_actions_info(repo) -> Dict[str, Any]:
    """
    Get GitHub Actions workflow information.
    
    Args:
        repo: GitHub repository object
    
    Returns:
        Dictionary with Actions information
    """
    try:
        workflows = list(repo.get_workflows())
        workflow_runs = list(repo.get_workflow_runs())[:10]  # Get last 10 runs
        
        return {
            'workflows_count': len(workflows),
            'recent_runs': len(workflow_runs),
            'workflows': [
                {
                    'name': wf.name,
                    'state': wf.state,
                    'path': wf.path
                }
                for wf in workflows
            ]
        }
    except (GithubException, Exception):
        return {'workflows_count': 0, 'recent_runs': 0, 'workflows': []}


def get_default_branch_protection(repo) -> Dict[str, Any]:
    """
    Check default branch protection settings.
    
    Args:
        repo: GitHub repository object
    
    Returns:
        Dictionary with branch protection information
    """
    try:
        default_branch = repo.default_branch
        branch = repo.get_branch(default_branch)
        protection = branch.get_protection()
        
        return {
            'protected': True,
            'required_status_checks': bool(protection.required_status_checks),
            'enforce_admins': protection.enforce_admins,
            'required_pull_request_reviews': bool(protection.required_pull_request_reviews),
            'restrictions': bool(protection.restrictions)
        }
    except (GithubException, Exception):
        return {'protected': False}


def get_latest_commit_info(repo) -> Dict[str, Any]:
    """
    Get latest commit information.
    
    Args:
        repo: GitHub repository object
    
    Returns:
        Dictionary with latest commit information
    """
    try:
        commits = list(repo.get_commits())
        if commits:
            latest = commits[0]
            return {
                'sha': latest.sha,
                'author': latest.author.login if latest.author else 'unknown',
                'date': latest.commit.author.date.isoformat(),
                'message': latest.commit.message[:100] + '...' if len(latest.commit.message) > 100 else latest.commit.message
            }
        else:
            return {}
    except (GithubException, Exception):
        return {}

# =============================================================================
# LANGUAGE NAME SANITIZATION SYSTEM
# =============================================================================

def sanitize_language_names(repo_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sanitize problematic language names to prevent Excel column name conflicts.
    
    This function addresses the issue where Excel sanitizes the "#" character in column names,
    causing "languages.C#" to become "languages.C" and creating conflicts with actual C language data.
    
    Args:
        repo_data: List of repository dictionaries containing language data
        
    Returns:
        List of repository dictionaries with sanitized language names
    """
    import copy
    
    logger = logging.getLogger('github_org_stats')
    
    # Define language name mappings for problematic characters
    language_mappings = {
        'C#': 'CSharp',
        'C++': 'CPlusPlus',
        'F#': 'FSharp'
    }
    
    sanitized_languages = []
    transformation_count = 0
    
    for repo in repo_data:
        # Create a deep copy to avoid modifying the original data
        sanitized_repo = copy.deepcopy(repo)
        
        # Check if repository has language data
        if 'languages' in sanitized_repo and isinstance(sanitized_repo['languages'], dict):
            original_languages = sanitized_repo['languages']
            sanitized_repo_languages = {}
            
            for lang_name, byte_count in original_languages.items():
                if lang_name in language_mappings:
                    new_name = language_mappings[lang_name]
                    sanitized_repo_languages[new_name] = byte_count
                    transformation_count += 1
                    logger.debug(f"Sanitized language name in {sanitized_repo.get('name', 'unknown')}: {lang_name} → {new_name}")
                else:
                    sanitized_repo_languages[lang_name] = byte_count
            
            sanitized_repo['languages'] = sanitized_repo_languages
        
        # Update primary_language if it was one of the sanitized languages (handle independently of languages dict)
        if 'primary_language' in sanitized_repo and sanitized_repo['primary_language'] in language_mappings:
            old_primary = sanitized_repo['primary_language']
            sanitized_repo['primary_language'] = language_mappings[old_primary]
            transformation_count += 1
            logger.debug(f"Sanitized primary language in {sanitized_repo.get('name', 'unknown')}: {old_primary} → {sanitized_repo['primary_language']}")
        
        sanitized_languages.append(sanitized_repo)
    
    if transformation_count > 0:
        transformed_mappings = [f"{old} → {new}" for old, new in language_mappings.items()]
        logger.info(f"Sanitized language names: {', '.join(transformed_mappings)} ({transformation_count} transformations)")
    else:
        logger.debug("No language name sanitization needed")
    
    return sanitized_languages


# =============================================================================
# EXCEL OUTPUT & OPTIMIZATION SYSTEM
# =============================================================================

class ColumnNameManager:
    """
    Manages Excel column name sanitization and mapping.
    """
    
    def __init__(self):
        self.column_mapping = {}
        self.used_names = set()
    
    def sanitize_column_name(self, name: str) -> str:
        """
        Sanitize column name for Excel compatibility.
        
        Args:
            name: Original column name
            
        Returns:
            Sanitized column name
        """
        # Remove or replace invalid characters
        sanitized = re.sub(r'[^\w\s-]', '_', str(name))
        sanitized = re.sub(r'\s+', '_', sanitized)
        sanitized = sanitized.strip('_')
        
        # Ensure it doesn't start with a number
        if sanitized and sanitized[0].isdigit():
            sanitized = f"col_{sanitized}"
        
        # Limit length
        if len(sanitized) > 31:  # Excel column name limit
            sanitized = sanitized[:28] + "..."
        
        # Handle duplicates
        original_sanitized = sanitized
        counter = 1
        while sanitized in self.used_names:
            sanitized = f"{original_sanitized}_{counter}"
            counter += 1
        
        self.used_names.add(sanitized)
        self.column_mapping[name] = sanitized
        return sanitized
    
    def get_mapping(self) -> Dict[str, str]:
        """Get the complete column mapping."""
        return self.column_mapping.copy()


class DataSanitizer:
    """
    Handles data sanitization and type conversion for Excel output.
    """
    
    @staticmethod
    def sanitize_value(value: Any, timezone_name: str = DEFAULT_TIMEZONE) -> Any:
        """
        Sanitize a value for Excel output.
        
        Args:
            value: Value to sanitize
            timezone_name: Timezone for datetime conversion
            
        Returns:
            Sanitized value
        """
        if value is None:
            return ""
        
        # Handle datetime objects
        if isinstance(value, datetime):
            try:
                # Ensure timezone awareness
                if value.tzinfo is None:
                    tz = pytz.timezone(timezone_name)
                    value = tz.localize(value)
                return value.isoformat()
            except Exception:
                return str(value)
        
        # Handle complex data structures
        if isinstance(value, (dict, list)):
            try:
                json_str = json.dumps(value, default=str)
                # Truncate if too long for Excel
                if len(json_str) > EXCEL_MAX_CELL_LENGTH:
                    json_str = json_str[:EXCEL_MAX_CELL_LENGTH-3] + "..."
                return json_str
            except Exception:
                return str(value)[:EXCEL_MAX_CELL_LENGTH]
        
        # Handle strings
        if isinstance(value, str):
            # Truncate long strings
            if len(value) > EXCEL_MAX_CELL_LENGTH:
                return value[:EXCEL_MAX_CELL_LENGTH-3] + "..."
            return value
        
        # Handle numeric types
        if isinstance(value, (int, float)):
            # Check for NaN or infinity
            if isinstance(value, float) and (pd.isna(value) or not np.isfinite(value)):
                return ""
            return value
        
        # Handle boolean
        if isinstance(value, bool):
            return value
        
        # Default: convert to string
        try:
            str_value = str(value)
            if len(str_value) > EXCEL_MAX_CELL_LENGTH:
                str_value = str_value[:EXCEL_MAX_CELL_LENGTH-3] + "..."
            return str_value
        except Exception:
            return ""


class ErrorTracker:
    """
    Tracks and categorizes errors during processing.
    """
    
    def __init__(self):
        self.errors = []
        self.error_counts = defaultdict(int)
        self.repo_errors = defaultdict(list)
    
    def add_error(self, repo_name: str, error_type: str, error_message: str, context: str = ""):
        """
        Add an error to the tracker.
        
        Args:
            repo_name: Name of the repository where error occurred
            error_type: Type/category of error
            error_message: Error message
            context: Additional context information
        """
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'repo_name': repo_name,
            'error_type': error_type,
            'error_message': str(error_message),
            'context': context
        }
        
        self.errors.append(error_entry)
        self.error_counts[error_type] += 1
        self.repo_errors[repo_name].append(error_entry)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of all errors."""
        return {
            'total_errors': len(self.errors),
            'errors_by_category': dict(self.error_counts),
            'repos_with_errors': len(self.repo_errors),
            'error_rate': len(self.errors) / max(len(self.repo_errors), 1)
        }
    
    def get_errors_for_repo(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all errors for a specific repository."""
        return self.repo_errors.get(repo_name, [])


def calculate_adaptive_batch_size(total_repos: int, available_memory_gb: float = 4.0) -> int:
    """
    Calculate optimal batch size based on repository count and available memory.
    
    Args:
        total_repos: Total number of repositories to process
        available_memory_gb: Available memory in GB
        
    Returns:
        Optimal batch size
    """
    # Base batch size
    base_batch_size = EXCEL_BATCH_SIZE
    
    # Adjust based on repository count
    if total_repos < 50:
        return min(total_repos, 25)
    elif total_repos < 200:
        return min(total_repos // 2, 50)
    elif total_repos < 1000:
        return min(100, base_batch_size)
    else:
        # For large datasets, use memory-based calculation
        estimated_memory_per_repo = 0.1  # MB per repository (rough estimate)
        max_repos_in_memory = int((available_memory_gb * 1024) / estimated_memory_per_repo)
        calculated_batch = max_repos_in_memory // 4  # Use 1/4 of available memory
        
        # Ensure minimum batch size for memory-constrained environments
        if available_memory_gb < 2.0:
            calculated_batch = min(calculated_batch, 50)
        
        return min(calculated_batch, 200)


def log_processing_stats(logger, processed: int, total: int, skipped: int, errors: int):
    """
    Log processing statistics.
    
    Args:
        logger: Logger instance
        processed: Number of repositories processed
        total: Total number of repositories
        skipped: Number of repositories skipped
        errors: Number of errors encountered
    """
    logger.info("=== Processing Statistics ===")
    logger.info(f"Total repositories found: {total}")
    logger.info(f"Repositories processed: {processed}")
    logger.info(f"Repositories skipped: {skipped}")
    logger.info(f"Errors encountered: {errors}")
    
    if total > 0:
        success_rate = (processed / total) * 100
        logger.info(f"Success rate: {success_rate:.1f}%")

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

def setup_logging(log_level: str = DEFAULT_LOG_LEVEL, log_file: Optional[str] = None) -> logging.Logger:
    """
    Configure logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
    
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger('github_org_stats')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# =============================================================================
# COMMAND LINE ARGUMENT PARSING
# =============================================================================

def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="GitHub Organization Statistics Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --org myorg --token ghp_xxx
  %(prog)s --org myorg --app-id 12345 --private-key key.pem --installation-id 67890
  %(prog)s --org myorg --app-id 12345 --private-key key.pem --installation-id "myorg:67890"
  %(prog)s --org-ids "org1:111,org2:222" --app-id 12345 --private-key key.pem
  %(prog)s --org-ids "kaltura:68242466,kaltura-ps:68357040" --format all
  %(prog)s --config config.json --output-dir ./reports
        """
    )
    
    # Authentication options
    auth_group = parser.add_argument_group('Authentication')
    auth_group.add_argument(
        '--token',
        help='GitHub personal access token'
    )
    auth_group.add_argument(
        '--app-id',
        type=int,
        help='GitHub App ID for authentication'
    )
    auth_group.add_argument(
        '--private-key',
        help='Path to GitHub App private key file'
    )
    auth_group.add_argument(
        '--installation-id',
        help='GitHub App installation ID (supports multiple: "org1:id1,org2:id2" or single: "12345")'
    )
    auth_group.add_argument(
        '--installation-ids',
        help='Multiple installation IDs in format "org1:id1,org2:id2" (alias for --installation-id)'
    )
    
    # Organization and scope
    scope_group = parser.add_argument_group('Scope')
    scope_group.add_argument(
        '--org',
        help='GitHub organization name to analyze (single organization mode)'
    )
    scope_group.add_argument(
        '--org-ids',
        help='Multiple organizations with installation IDs in format "org1:id1,org2:id2" (multi-organization mode)'
    )
    scope_group.add_argument(
        '--repos',
        nargs='+',
        help='Specific repositories to analyze (default: all)'
    )
    scope_group.add_argument(
        '--days-back',
        type=int,
        default=DEFAULT_DAYS_BACK,
        help=f'Number of days to look back for activity (default: {DEFAULT_DAYS_BACK})'
    )
    
    # Output options
    output_group = parser.add_argument_group('Output')
    output_group.add_argument(
        '--output-dir',
        default=DEFAULT_OUTPUT_DIR,
        help=f'Output directory for reports (default: {DEFAULT_OUTPUT_DIR})'
    )
    output_group.add_argument(
        '--format',
        choices=['json', 'csv', 'excel', 'all'],
        default='excel',
        help='Output format (default: excel)'
    )
    output_group.add_argument(
        '--config',
        help='Configuration file path (JSON format)'
    )
    
    # Logging options
    logging_group = parser.add_argument_group('Logging')
    logging_group.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default=DEFAULT_LOG_LEVEL,
        help=f'Logging level (default: {DEFAULT_LOG_LEVEL})'
    )
    logging_group.add_argument(
        '--log-file',
        help='Log file path (default: console only)'
    )
    
    # Analysis options
    analysis_group = parser.add_argument_group('Analysis')
    analysis_group.add_argument(
        '--include-forks',
        action='store_true',
        help='Include forked repositories in analysis'
    )
    analysis_group.add_argument(
        '--include-archived',
        action='store_true',
        help='Include archived repositories in analysis'
    )
    analysis_group.add_argument(
        '--max-repos',
        type=int,
        default=DEFAULT_MAX_REPOS,
        help=f'Maximum number of repositories to analyze (default: {DEFAULT_MAX_REPOS})'
    )
    analysis_group.add_argument(
        '--exclude-bots',
        action='store_true',
        help='Exclude bot accounts from contributor analysis and commit statistics'
    )
    analysis_group.add_argument(
        '--include-empty',
        action='store_true',
        help='Include repositories with no commits in the specified timeframe (default: exclude empty repos)'
    )
    
    return parser.parse_args()


# =============================================================================
# CONFIGURATION MANAGEMENT
# =============================================================================

def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from JSON file.
    
    Args:
        config_path: Path to configuration file
    
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in configuration file: {e}")


def validate_arguments(args: argparse.Namespace) -> None:
    """
    Validate command line arguments and configuration.
    
    Args:
        args: Parsed command line arguments
    
    Raises:
        ValueError: If arguments are invalid or incomplete
    """
    # Validate organization parameters
    if not args.org and not args.org_ids:
        raise ValueError("Either --org or --org-ids must be specified")
    
    if args.org and args.org_ids:
        raise ValueError("Cannot specify both --org and --org-ids. Use --org for single organization or --org-ids for multiple organizations")
    
    # Validate authentication - check CLI args first, then environment variables
    has_token = args.token is not None
    has_app_creds = args.app_id is not None and args.private_key is not None
    has_env_creds = os.getenv('GITHUB_APP_ID') is not None and os.getenv('GITHUB_PRIVATE_KEY_PATH') is not None
    
    if not has_token and not has_app_creds and not has_env_creds:
        raise ValueError(
            "Authentication required: provide either --token, both --app-id and --private-key, or set GITHUB_APP_ID and GITHUB_PRIVATE_KEY_PATH environment variables"
        )
    
    # Validate GitHub App authentication
    if args.app_id and not args.private_key:
        raise ValueError("GitHub App authentication requires both --app-id and --private-key")
    
    if args.private_key and not os.path.exists(args.private_key):
        raise ValueError(f"Private key file not found: {args.private_key}")
    
    # Handle installation-ids alias
    if args.installation_ids and not args.installation_id:
        args.installation_id = args.installation_ids
    
    # Validate installation ID format if using GitHub App
    if args.app_id and args.installation_id:
        try:
            parse_installation_ids(args.installation_id)
        except ValueError as e:
            raise ValueError(f"Invalid installation ID format: {e}")
    
    # Validate org-ids format if using multi-organization mode
    if args.org_ids:
        try:
            parse_installation_ids(args.org_ids)
        except ValueError as e:
            raise ValueError(f"Invalid --org-ids format: {e}")
    
    # Validate output directory
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir, exist_ok=True)


# =============================================================================
# MAIN APPLICATION LOGIC
# =============================================================================

def main() -> int:
    """
    Main application entry point.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Load configuration file if provided
        config = {}
        if args.config:
            config = load_config(args.config)
        
        # Setup logging
        logger = setup_logging(args.log_level, args.log_file)
        logger.info("GitHub Organization Statistics Tool - Starting")
        
        # Determine organizations to analyze
        organizations_to_analyze = {}
        if args.org:
            # Single organization mode
            logger.info(f"Single organization mode: {args.org}")
            organizations_to_analyze[args.org] = None  # Will determine installation ID later
        elif args.org_ids:
            # Multi-organization mode
            organizations_to_analyze = parse_installation_ids(args.org_ids)
            logger.info(f"Multi-organization mode: {list(organizations_to_analyze.keys())}")
        
        logger.info(f"Output directory: {args.output_dir}")
        
        # Validate arguments
        validate_arguments(args)
        logger.info("Arguments validated successfully")
        
        # Initialize authentication
        token_manager = None
        installation_mappings = None
        
        if args.token:
            # Personal Access Token authentication
            logger.info("Using Personal Access Token authentication")
            # For PAT, we'll create a single client and use it for all organizations
            
        elif args.app_id and args.private_key:
            # GitHub App authentication from CLI args
            logger.info("Using GitHub App authentication from CLI arguments")
            
            try:
                # Load private key
                private_key = load_private_key(args.private_key)
                logger.info(f"Loaded private key from: {args.private_key}")
                
                # Initialize token manager
                token_manager = GitHubAppTokenManager(args.app_id, private_key)
                logger.info(f"Initialized token manager for App ID: {args.app_id}")
                
                # Parse installation IDs if provided for single org mode
                if args.installation_id:
                    installation_mappings = parse_installation_ids(args.installation_id)
                    logger.info(f"Parsed installation mappings: {installation_mappings}")
                
                # For multi-org mode, organizations_to_analyze already contains the mappings
                if args.org_ids:
                    installation_mappings = organizations_to_analyze
                    logger.info(f"Using org-ids installation mappings: {installation_mappings}")
                
            except Exception as e:
                logger.error(f"GitHub App authentication failed: {e}")
                raise ValueError(f"GitHub App authentication failed: {e}")
        
        else:
            # Try loading from environment variables
            logger.info("Using GitHub App authentication from environment variables")
            env_app_id, env_private_key = load_github_app_creds()
            
            if env_app_id and env_private_key:
                token_manager = GitHubAppTokenManager(env_app_id, env_private_key)
                logger.info(f"Successfully loaded GitHub App credentials from environment (App ID: {env_app_id})")
                
                # For multi-org mode, organizations_to_analyze already contains the mappings
                if args.org_ids:
                    installation_mappings = organizations_to_analyze
                    logger.info(f"Using org-ids installation mappings: {installation_mappings}")
                
            else:
                raise ValueError("No valid authentication method found")
        
        # Collect data from all organizations
        logger.info("Starting multi-organization data collection...")
        
        all_repo_data = []
        all_error_tracker = ErrorTracker()
        all_skipped_repos = []
        total_repos_found = 0
        
        # Process each organization
        for org_name, installation_id in organizations_to_analyze.items():
            logger.info(f"Processing organization: {org_name}")
            
            try:
                # Get GitHub client for this organization
                github_client = None
                
                if args.token:
                    # Personal Access Token - same client for all orgs
                    github_client = Github(args.token)
                elif token_manager:
                    # GitHub App authentication - get installation token for this org
                    if installation_id is None:
                        # Single org mode - determine installation ID
                        installation_id = get_installation_id(org_name, token_manager, installation_mappings)
                    
                    installation_token = token_manager.get_installation_token(installation_id)
                    github_client = Github(installation_token)
                    logger.info(f"Using installation ID {installation_id} for organization: {org_name}")
                
                # Verify organization access (skip user verification for GitHub Apps)
                org = github_client.get_organization(org_name)
                logger.info(f"Successfully accessed organization: {org.name} ({org.login})")
                
                # Get organization repositories
                repos = list(org.get_repos())
                logger.info(f"Found {len(repos)} repositories in organization {org_name}")
                total_repos_found += len(repos)
                
                # Filter repositories based on arguments
                filtered_repos = []
                for repo in repos:
                    # Skip forks if not included
                    if repo.fork and not args.include_forks:
                        continue
                    
                    # Skip archived if not included
                    if repo.archived and not args.include_archived:
                        continue
                    
                    # Filter by specific repositories if specified
                    if args.repos and repo.name not in args.repos:
                        continue
                    
                    filtered_repos.append(repo)
                
                # Limit number of repositories per organization
                org_max_repos = args.max_repos // len(organizations_to_analyze) if len(organizations_to_analyze) > 1 else args.max_repos
                if len(filtered_repos) > org_max_repos:
                    logger.warning(f"Limiting analysis to {org_max_repos} repositories for {org_name} (found {len(filtered_repos)})")
                    filtered_repos = filtered_repos[:org_max_repos]
                
                logger.info(f"Analyzing {len(filtered_repos)} repositories from {org_name}")
                
                # Process repositories with progress bar
                with tqdm(total=len(filtered_repos), desc=f"Processing {org_name} repositories") as pbar:
                    for repo in filtered_repos:
                        try:
                            logger.debug(f"Processing repository: {repo.name} from {org_name}")
                            
                            # Basic repository information
                            repo_info = {
                                'organization': org_name,  # Add organization field
                                'name': repo.name,
                                'full_name': repo.full_name,
                                'description': repo.description or '',
                                'private': repo.private,
                                'fork': repo.fork,
                                'archived': repo.archived,
                                'disabled': repo.disabled,
                                'created_at': repo.created_at.isoformat() if repo.created_at else None,
                                'updated_at': repo.updated_at.isoformat() if repo.updated_at else None,
                                'pushed_at': repo.pushed_at.isoformat() if repo.pushed_at else None,
                                'size': repo.size,
                                'stargazers_count': repo.stargazers_count,
                                'watchers_count': repo.watchers_count,
                                'forks_count': repo.forks_count,
                                'open_issues_count': repo.open_issues_count,
                                'default_branch': repo.default_branch,
                                'language': repo.language,
                                'has_issues': repo.has_issues,
                                'has_projects': repo.has_projects,
                                'has_wiki': repo.has_wiki,
                                'has_pages': repo.has_pages,
                                'has_downloads': repo.has_downloads,
                                'license': repo.license.name if repo.license else None,
                                'clone_url': repo.clone_url,
                                'html_url': repo.html_url
                            }
                            
                            # Enhanced data collection using helper functions
                            logger.debug(f"Collecting commit statistics for {repo.name}")
                            commit_stats = gh_safe(github_client, get_commit_stats, repo, args.days_back)
                            if commit_stats:
                                repo_info.update(commit_stats)
                            
                            logger.debug(f"Collecting language statistics for {repo.name}")
                            languages = gh_safe(github_client, get_code_bytes, repo)
                            if languages:
                                repo_info['languages'] = languages
                                repo_info['total_code_bytes'] = sum(languages.values())
                                repo_info['primary_language'] = max(languages.items(), key=lambda x: x[1])[0] if languages else None
                            
                            logger.debug(f"Collecting topics for {repo.name}")
                            topics = gh_safe(github_client, get_repo_topics, repo)
                            repo_info['topics'] = topics
                            
                            logger.debug(f"Collecting contributors for {repo.name}")
                            contributors = gh_safe(github_client, get_primary_contributors, repo)
                            repo_info['contributors'] = contributors
                            repo_info['contributors_count'] = len(contributors) if contributors else 0
                            
                            logger.debug(f"Collecting branch/tag counts for {repo.name}")
                            branch_tag_info = gh_safe(github_client, get_branches_tags_counts, repo)
                            if branch_tag_info:
                                repo_info.update(branch_tag_info)
                            
                            logger.debug(f"Collecting release information for {repo.name}")
                            release_info = gh_safe(github_client, get_release_info, repo)
                            if release_info:
                                repo_info.update(release_info)
                            
                            logger.debug(f"Collecting Actions information for {repo.name}")
                            actions_info = gh_safe(github_client, get_actions_info, repo)
                            if actions_info:
                                repo_info['github_actions'] = actions_info
                            
                            logger.debug(f"Collecting branch protection for {repo.name}")
                            protection_info = gh_safe(github_client, get_default_branch_protection, repo)
                            if protection_info:
                                repo_info['branch_protection'] = protection_info
                            
                            logger.debug(f"Collecting latest commit info for {repo.name}")
                            latest_commit = gh_safe(github_client, get_latest_commit_info, repo)
                            if latest_commit:
                                repo_info['latest_commit'] = latest_commit
                            
                            logger.debug(f"Collecting dependency information for {repo.name}")
                            deps = gh_safe(github_client, get_sbom_deps, repo)
                            if deps:
                                repo_info['dependencies'] = deps
                            
                            logger.debug(f"Collecting submodules for {repo.name}")
                            submodules = gh_safe(github_client, get_submodules_info, repo)
                            repo_info['submodules'] = submodules
                            repo_info['submodules_count'] = len(submodules) if submodules else 0
                            
                            # Add timestamp
                            repo_info['analyzed_at'] = datetime.now().isoformat()
                            
                            all_repo_data.append(repo_info)
                            
                        except Exception as e:
                            logger.error(f"Error processing repository {repo.name} from {org_name}: {e}")
                            all_error_tracker.add_error(repo.name, "processing_error", str(e), f"Organization: {org_name}")
                            continue
                        finally:
                            pbar.update(1)
                            
                            # Print rate limit status periodically
                            if len(all_repo_data) % 10 == 0:
                                print_rate_limit(github_client)
                
                logger.info(f"Successfully collected data for {len([r for r in all_repo_data if r['organization'] == org_name])} repositories from {org_name}")
                
            except Exception as e:
                logger.error(f"Error processing organization {org_name}: {e}")
                all_error_tracker.add_error(org_name, "organization_error", str(e), "Failed to process entire organization")
                continue
        
        # Use collected data for output
        repo_data = all_repo_data
        error_tracker = all_error_tracker
        skipped_repos = all_skipped_repos
        
        logger.info(f"Successfully collected data for {len(repo_data)} repositories across {len(organizations_to_analyze)} organizations")
        
        # Create output directory
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Generate timestamp for output files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Determine filename suffix based on mode
        if args.org:
            filename_suffix = args.org
        else:
            filename_suffix = "_".join(organizations_to_analyze.keys())
            if len(filename_suffix) > 50:  # Limit filename length
                filename_suffix = f"multi_org_{len(organizations_to_analyze)}_orgs"
        
        # Save data in requested format(s)
        if args.format in ['json', 'all']:
            json_file = os.path.join(args.output_dir, f"github_org_stats_{filename_suffix}_{timestamp}.json")
            with open(json_file, 'w') as f:
                json.dump({
                    'organizations': list(organizations_to_analyze.keys()) if args.org_ids else [args.org],
                    'analyzed_at': datetime.now().isoformat(),
                    'total_repositories': len(repo_data),
                    'repositories': repo_data,
                    'analysis_mode': 'multi-organization' if args.org_ids else 'single-organization'
                }, f, indent=2, default=str)
            logger.info(f"JSON report saved to: {json_file}")
        
        if args.format in ['csv', 'all']:
            csv_file = os.path.join(args.output_dir, f"github_org_stats_{filename_suffix}_{timestamp}.csv")
            # Apply language name sanitization before pandas normalization
            sanitized_repo_data = sanitize_language_names(repo_data)
            df = pd.json_normalize(sanitized_repo_data)
            df.to_csv(csv_file, index=False)
            logger.info(f"CSV report saved to: {csv_file}")
        
        if args.format in ['excel', 'all']:
            excel_file = os.path.join(args.output_dir, f"github_org_stats_{filename_suffix}_{timestamp}.xlsx")
            # Apply language name sanitization before pandas normalization
            sanitized_repo_data = sanitize_language_names(repo_data)
            df = pd.json_normalize(sanitized_repo_data)
            
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                # Main data sheet
                df.to_excel(writer, sheet_name='Repository_Data', index=False)
                
                # Summary sheet - overall summary
                summary_data = {
                    'Metric': [
                        'Total Organizations',
                        'Total Repositories',
                        'Private Repositories',
                        'Forked Repositories',
                        'Archived Repositories',
                        'Total Stars',
                        'Total Forks',
                        'Total Open Issues',
                        'Repositories with Actions',
                        'Protected Repositories'
                    ],
                    'Value': [
                        len(organizations_to_analyze),
                        len(sanitized_repo_data),
                        sum(1 for r in sanitized_repo_data if r.get('private', False)),
                        sum(1 for r in sanitized_repo_data if r.get('fork', False)),
                        sum(1 for r in sanitized_repo_data if r.get('archived', False)),
                        sum(r.get('stargazers_count', 0) for r in sanitized_repo_data),
                        sum(r.get('forks_count', 0) for r in sanitized_repo_data),
                        sum(r.get('open_issues_count', 0) for r in sanitized_repo_data),
                        sum(1 for r in sanitized_repo_data if r.get('github_actions', {}).get('workflows_count', 0) > 0),
                        sum(1 for r in sanitized_repo_data if r.get('branch_protection', {}).get('protected', False))
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Organization breakdown sheet (if multi-org mode)
                if args.org_ids and len(organizations_to_analyze) > 1:
                    org_breakdown = []
                    for org_name in organizations_to_analyze.keys():
                        org_repos = [r for r in sanitized_repo_data if r.get('organization') == org_name]
                        org_breakdown.append({
                            'Organization': org_name,
                            'Repositories': len(org_repos),
                            'Private Repos': sum(1 for r in org_repos if r.get('private', False)),
                            'Forked Repos': sum(1 for r in org_repos if r.get('fork', False)),
                            'Archived Repos': sum(1 for r in org_repos if r.get('archived', False)),
                            'Total Stars': sum(r.get('stargazers_count', 0) for r in org_repos),
                            'Total Forks': sum(r.get('forks_count', 0) for r in org_repos),
                            'Open Issues': sum(r.get('open_issues_count', 0) for r in org_repos)
                        })
                    
                    org_breakdown_df = pd.DataFrame(org_breakdown)
                    org_breakdown_df.to_excel(writer, sheet_name='Organization_Breakdown', index=False)
            
            logger.info(f"Excel report saved to: {excel_file}")
        
        # Log final statistics
        error_summary = error_tracker.get_error_summary()
        log_processing_stats(
            logger,
            processed=len(repo_data),
            total=total_repos_found,
            skipped=len(skipped_repos),
            errors=error_summary['total_errors']
        )
        
        logger.info("=== Analysis Summary ===")
        logger.info(f"Organizations analyzed: {len(organizations_to_analyze)}")
        logger.info(f"Organization names: {', '.join(organizations_to_analyze.keys())}")
        logger.info(f"Repositories processed: {len(repo_data)}")
        logger.info(f"Repositories skipped: {len(skipped_repos)}")
        logger.info(f"Total errors encountered: {error_summary['total_errors']}")
        logger.info(f"Bot filtering: {'enabled' if args.exclude_bots else 'disabled'}")
        logger.info(f"Empty repo filtering: {'enabled' if not args.include_empty else 'disabled'}")
        
        # Per-organization breakdown
        if args.org_ids and len(organizations_to_analyze) > 1:
            logger.info("=== Per-Organization Breakdown ===")
            for org_name in organizations_to_analyze.keys():
                org_repos = [r for r in repo_data if r.get('organization') == org_name]
                logger.info(f"{org_name}: {len(org_repos)} repositories processed")
        
        if error_summary['total_errors'] > 0:
            logger.warning(f"Errors by category: {error_summary['errors_by_category']}")
        
        logger.info("Multi-organization analysis completed successfully")
        return 0
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        if 'logger' in locals():
            logger.error(f"Fatal error: {e}")
        else:
            print(f"Fatal error: {e}")
        return 1


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    sys.exit(main())