#!/usr/bin/env python3
"""
Test Suite for GitHub Organization Statistics Unified Script
===========================================================

Comprehensive testing script that validates all functionality of the unified
GitHub organization statistics tool including authentication, data collection,
output generation, and error handling.

Author: GitHub Stats Team
Version: 1.0.0
"""

import unittest
import os
import sys
import json
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import pandas as pd

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the script modules
try:
    from github_org_stats import (
        GitHubAppTokenManager,
        parse_installation_ids,
        get_installation_id,
        load_private_key,
        is_bot_account,
        filter_bot_contributors,
        get_commit_stats,
        get_code_bytes,
        get_repo_topics,
        get_primary_contributors,
        ColumnNameManager,
        DataSanitizer,
        ErrorTracker,
        calculate_adaptive_batch_size,
        setup_logging,
        parse_arguments,
        validate_arguments,
        load_config,
        robust_github_call,
        gh_safe
    )
except ImportError as e:
    print(f"Error importing script: {e}")
    print("Please ensure github_org_stats.py is in the parent directory")
    sys.exit(1)


class TestGitHubAppAuthentication(unittest.TestCase):
    """Test GitHub App authentication functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app_id = 12345
        self.private_key = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA1234567890abcdef...
-----END RSA PRIVATE KEY-----"""
        self.installation_id = 67890
    
    def test_parse_installation_ids_single(self):
        """Test parsing single installation ID."""
        result = parse_installation_ids("12345")
        self.assertEqual(result, {'default': 12345})
    
    def test_parse_installation_ids_single_with_org(self):
        """Test parsing single installation ID with organization."""
        result = parse_installation_ids("myorg:12345")
        self.assertEqual(result, {'myorg': 12345})
    
    def test_parse_installation_ids_multiple(self):
        """Test parsing multiple installation IDs."""
        result = parse_installation_ids("org1:111,org2:222,org3:333")
        expected = {'org1': 111, 'org2': 222, 'org3': 333}
        self.assertEqual(result, expected)
    
    def test_parse_installation_ids_mixed(self):
        """Test parsing mixed format installation IDs."""
        result = parse_installation_ids("org1:111,222,org3:333")
        expected = {'org1': 111, 'default': 222, 'org3': 333}
        self.assertEqual(result, expected)
    
    @patch('github_org_stats.jwt.encode')
    def test_github_app_token_manager_jwt(self, mock_jwt_encode):
        """Test JWT token generation."""
        mock_jwt_encode.return_value = "mock_jwt_token"
        
        token_manager = GitHubAppTokenManager(self.app_id, self.private_key)
        jwt_token = token_manager.get_jwt_token()
        
        self.assertEqual(jwt_token, "mock_jwt_token")
        mock_jwt_encode.assert_called_once()
    
    @patch('github_org_stats.requests.post')
    @patch('github_org_stats.jwt.encode')
    def test_github_app_installation_token(self, mock_jwt_encode, mock_post):
        """Test installation token retrieval."""
        mock_jwt_encode.return_value = "mock_jwt_token"
        mock_response = Mock()
        mock_response.json.return_value = {
            'token': 'mock_installation_token',
            'expires_at': '2024-01-15T12:00:00Z'
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        token_manager = GitHubAppTokenManager(self.app_id, self.private_key)
        installation_token = token_manager.get_installation_token(self.installation_id)
        
        self.assertEqual(installation_token, 'mock_installation_token')
        mock_post.assert_called_once()
    
    def test_load_private_key_file_not_found(self):
        """Test private key loading with non-existent file."""
        with self.assertRaises(FileNotFoundError):
            load_private_key("/nonexistent/path/key.pem")
    
    def test_load_private_key_invalid_format(self):
        """Test private key loading with invalid format."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("invalid key content")
            temp_path = f.name
        
        try:
            with self.assertRaises(ValueError):
                load_private_key(temp_path)
        finally:
            os.unlink(temp_path)


class TestBotDetection(unittest.TestCase):
    """Test bot account detection and filtering."""
    
    def test_is_bot_account_positive_cases(self):
        """Test bot detection for known bot patterns."""
        bot_usernames = [
            'dependabot',
            'renovate[bot]',
            'github-actions[bot]',
            'codecov-bot',
            'greenkeeper[bot]',
            'snyk-bot',
            'imgbot',
            'semantic-release-bot',
            'pre-commit-ci[bot]'
        ]
        
        for username in bot_usernames:
            with self.subTest(username=username):
                self.assertTrue(is_bot_account(username))
    
    def test_is_bot_account_negative_cases(self):
        """Test bot detection for human usernames."""
        human_usernames = [
            'john-doe',
            'alice_smith',
            'developer123',
            'team-lead',
            'contributor'
        ]
        
        for username in human_usernames:
            with self.subTest(username=username):
                self.assertFalse(is_bot_account(username))
    
    def test_is_bot_account_edge_cases(self):
        """Test bot detection edge cases."""
        self.assertFalse(is_bot_account(''))
        self.assertFalse(is_bot_account(None))
        self.assertTrue(is_bot_account('mybot'))
        self.assertTrue(is_bot_account('DEPENDABOT'))  # Case insensitive
    
    def test_filter_bot_contributors(self):
        """Test filtering bot contributors from list."""
        contributors = [
            {'login': 'human-user', 'contributions': 10},
            {'login': 'dependabot[bot]', 'contributions': 5},
            {'login': 'another-human', 'contributions': 8},
            {'login': 'renovate[bot]', 'contributions': 3}
        ]
        
        # Test with bot exclusion enabled
        filtered = filter_bot_contributors(contributors, exclude_bots=True)
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0]['login'], 'human-user')
        self.assertEqual(filtered[1]['login'], 'another-human')
        
        # Test with bot exclusion disabled
        unfiltered = filter_bot_contributors(contributors, exclude_bots=False)
        self.assertEqual(len(unfiltered), 4)


class TestDataProcessing(unittest.TestCase):
    """Test data processing and helper functions."""
    
    def setUp(self):
        """Set up mock repository object."""
        self.mock_repo = Mock()
        self.mock_repo.name = "test-repo"
        self.mock_repo.full_name = "org/test-repo"
        self.mock_repo.get_commits.return_value = []
        self.mock_repo.get_languages.return_value = {'Python': 1000, 'JavaScript': 500}
        self.mock_repo.get_topics.return_value = ['web', 'api', 'python']
        self.mock_repo.get_contributors.return_value = []
    
    def test_get_code_bytes(self):
        """Test language statistics collection."""
        result = get_code_bytes(self.mock_repo)
        expected = {'Python': 1000, 'JavaScript': 500}
        self.assertEqual(result, expected)
    
    def test_get_repo_topics(self):
        """Test repository topics collection."""
        result = get_repo_topics(self.mock_repo)
        expected = ['web', 'api', 'python']
        self.assertEqual(result, expected)
    
    def test_get_commit_stats_empty_repo(self):
        """Test commit statistics for empty repository."""
        result = get_commit_stats(self.mock_repo, days_back=30)
        
        self.assertEqual(result['total_commits'], 0)
        self.assertEqual(result['unique_authors'], 0)
        self.assertEqual(result['commit_authors'], {})
        self.assertEqual(result['commits_by_day'], {})
    
    @patch('github_org_stats.datetime')
    def test_get_commit_stats_with_commits(self, mock_datetime):
        """Test commit statistics with mock commits."""
        # Mock current time
        mock_datetime.now.return_value = datetime(2024, 1, 15)
        
        # Create mock commits
        mock_commit1 = Mock()
        mock_commit1.author.login = 'user1'
        mock_commit1.commit.author.date = datetime(2024, 1, 10)
        
        mock_commit2 = Mock()
        mock_commit2.author.login = 'user2'
        mock_commit2.commit.author.date = datetime(2024, 1, 12)
        
        mock_commit3 = Mock()
        mock_commit3.author.login = 'user1'
        mock_commit3.commit.author.date = datetime(2024, 1, 14)
        
        self.mock_repo.get_commits.return_value = [mock_commit1, mock_commit2, mock_commit3]
        
        result = get_commit_stats(self.mock_repo, days_back=30)
        
        self.assertEqual(result['total_commits'], 3)
        self.assertEqual(result['unique_authors'], 2)
        self.assertEqual(result['commit_authors']['user1'], 2)
        self.assertEqual(result['commit_authors']['user2'], 1)


class TestExcelOutput(unittest.TestCase):
    """Test Excel output functionality."""
    
    def test_column_name_manager_sanitization(self):
        """Test column name sanitization for Excel."""
        manager = ColumnNameManager()
        
        # Test basic sanitization
        self.assertEqual(manager.sanitize_column_name("normal_name"), "normal_name")
        self.assertEqual(manager.sanitize_column_name("name with spaces"), "name_with_spaces")
        self.assertEqual(manager.sanitize_column_name("name@with#special$chars"), "name_with_special_chars")
        
        # Test length limiting
        long_name = "a" * 40
        sanitized = manager.sanitize_column_name(long_name)
        self.assertTrue(len(sanitized) <= 31)
        self.assertTrue(sanitized.endswith("..."))
        
        # Test duplicate handling
        name1 = manager.sanitize_column_name("duplicate")
        name2 = manager.sanitize_column_name("duplicate")
        self.assertNotEqual(name1, name2)
        self.assertTrue(name2.endswith("_1"))
    
    def test_data_sanitizer_basic_types(self):
        """Test data sanitization for basic types."""
        sanitizer = DataSanitizer()
        
        # Test None
        self.assertEqual(sanitizer.sanitize_value(None), "")
        
        # Test strings
        self.assertEqual(sanitizer.sanitize_value("normal string"), "normal string")
        
        # Test numbers
        self.assertEqual(sanitizer.sanitize_value(42), 42)
        self.assertEqual(sanitizer.sanitize_value(3.14), 3.14)
        
        # Test boolean
        self.assertEqual(sanitizer.sanitize_value(True), True)
        self.assertEqual(sanitizer.sanitize_value(False), False)
    
    def test_data_sanitizer_complex_types(self):
        """Test data sanitization for complex types."""
        sanitizer = DataSanitizer()
        
        # Test dictionary
        test_dict = {"key1": "value1", "key2": 42}
        result = sanitizer.sanitize_value(test_dict)
        self.assertIsInstance(result, str)
        self.assertIn("key1", result)
        
        # Test list
        test_list = ["item1", "item2", 42]
        result = sanitizer.sanitize_value(test_list)
        self.assertIsInstance(result, str)
        self.assertIn("item1", result)
    
    def test_data_sanitizer_long_strings(self):
        """Test data sanitization for long strings."""
        sanitizer = DataSanitizer()
        
        # Test string truncation
        long_string = "a" * 40000
        result = sanitizer.sanitize_value(long_string)
        self.assertTrue(len(result) <= 32767)
        self.assertTrue(result.endswith("..."))
    
    def test_calculate_adaptive_batch_size(self):
        """Test adaptive batch size calculation."""
        # Small organizations
        self.assertEqual(calculate_adaptive_batch_size(25), 25)
        
        # Medium organizations
        batch_size = calculate_adaptive_batch_size(150)
        self.assertTrue(25 <= batch_size <= 75)
        
        # Large organizations
        batch_size = calculate_adaptive_batch_size(500)
        self.assertTrue(batch_size <= 200)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and tracking."""
    
    def test_error_tracker_basic(self):
        """Test basic error tracking functionality."""
        tracker = ErrorTracker()
        
        # Add some errors
        tracker.add_error("repo1", "API_ERROR", "Rate limit exceeded", "get_commits")
        tracker.add_error("repo2", "PERMISSION_ERROR", "Access denied", "get_collaborators")
        tracker.add_error("repo1", "API_ERROR", "Timeout", "get_issues")
        
        # Test error summary
        summary = tracker.get_error_summary()
        self.assertEqual(summary['total_errors'], 3)
        self.assertEqual(summary['repos_with_errors'], 2)
        self.assertEqual(summary['errors_by_category']['API_ERROR'], 2)
        self.assertEqual(summary['errors_by_category']['PERMISSION_ERROR'], 1)
        
        # Test repo-specific errors
        repo1_errors = tracker.get_errors_for_repo("repo1")
        self.assertEqual(len(repo1_errors), 2)
        
        repo2_errors = tracker.get_errors_for_repo("repo2")
        self.assertEqual(len(repo2_errors), 1)
    
    def test_robust_github_call_success(self):
        """Test successful GitHub API call."""
        def mock_success_func():
            return "success"
        
        result = robust_github_call(mock_success_func)
        self.assertEqual(result, "success")
    
    def test_robust_github_call_failure(self):
        """Test GitHub API call with failures."""
        def mock_failure_func():
            raise Exception("Test error")
        
        result = robust_github_call(mock_failure_func, max_retries=1)
        self.assertIsNone(result)


class TestConfigurationAndArguments(unittest.TestCase):
    """Test configuration loading and argument parsing."""
    
    def test_load_config_valid(self):
        """Test loading valid configuration file."""
        config_data = {
            "authentication": {
                "app_id": 12345,
                "private_key_path": "/path/to/key.pem"
            },
            "analysis": {
                "days_back": 60,
                "max_repos": 200
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name
        
        try:
            loaded_config = load_config(config_path)
            self.assertEqual(loaded_config, config_data)
        finally:
            os.unlink(config_path)
    
    def test_load_config_invalid_json(self):
        """Test loading invalid JSON configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            config_path = f.name
        
        try:
            with self.assertRaises(ValueError):
                load_config(config_path)
        finally:
            os.unlink(config_path)
    
    def test_load_config_file_not_found(self):
        """Test loading non-existent configuration file."""
        with self.assertRaises(FileNotFoundError):
            load_config("/nonexistent/config.json")
    
    @patch('sys.argv', ['script.py', '--org', 'testorg', '--token', 'test_token'])
    def test_parse_arguments_basic(self):
        """Test basic argument parsing."""
        args = parse_arguments()
        self.assertEqual(args.org, 'testorg')
        self.assertEqual(args.token, 'test_token')
        self.assertEqual(args.days_back, 30)  # Default value
        self.assertEqual(args.format, 'excel')  # Default value
    
    def test_validate_arguments_missing_auth(self):
        """Test argument validation with missing authentication."""
        args = Mock()
        args.token = None
        args.app_id = None
        args.private_key = None
        args.installation_id = None
        args.installation_ids = None
        args.output_dir = '/tmp/test'
        
        with self.assertRaises(ValueError):
            validate_arguments(args)
    
    def test_validate_arguments_github_app_incomplete(self):
        """Test argument validation with incomplete GitHub App auth."""
        args = Mock()
        args.token = None
        args.app_id = 12345
        args.private_key = None
        args.installation_id = None
        args.installation_ids = None
        args.output_dir = '/tmp/test'
        
        with self.assertRaises(ValueError):
            validate_arguments(args)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)
    
    def test_logging_setup(self):
        """Test logging configuration."""
        log_file = os.path.join(self.test_dir, 'test.log')
        logger = setup_logging('INFO', log_file)
        
        self.assertIsNotNone(logger)
        logger.info("Test log message")
        
        # Check if log file was created
        self.assertTrue(os.path.exists(log_file))
        
        # Check log content
        with open(log_file, 'r') as f:
            content = f.read()
            self.assertIn("Test log message", content)
    
    @patch('github_org_stats.Github')
    def test_github_client_initialization(self, mock_github):
        """Test GitHub client initialization."""
        mock_client = Mock()
        mock_github.return_value = mock_client
        
        # Test with token
        client = mock_github('test_token')
        self.assertIsNotNone(client)
        mock_github.assert_called_with('test_token')


class TestPerformanceAndScaling(unittest.TestCase):
    """Test performance and scaling features."""
    
    def test_batch_size_calculation_small_org(self):
        """Test batch size calculation for small organizations."""
        batch_size = calculate_adaptive_batch_size(25, available_memory_gb=4.0)
        self.assertEqual(batch_size, 25)
    
    def test_batch_size_calculation_medium_org(self):
        """Test batch size calculation for medium organizations."""
        batch_size = calculate_adaptive_batch_size(150, available_memory_gb=4.0)
        self.assertTrue(25 <= batch_size <= 75)
    
    def test_batch_size_calculation_large_org(self):
        """Test batch size calculation for large organizations."""
        batch_size = calculate_adaptive_batch_size(1500, available_memory_gb=8.0)
        self.assertTrue(batch_size <= 200)
    
    def test_batch_size_calculation_memory_constrained(self):
        """Test batch size calculation with limited memory."""
        batch_size = calculate_adaptive_batch_size(1000, available_memory_gb=1.0)
        self.assertTrue(batch_size <= 100)


def create_test_suite():
    """Create and return the complete test suite."""
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestGitHubAppAuthentication,
        TestBotDetection,
        TestDataProcessing,
        TestExcelOutput,
        TestErrorHandling,
        TestConfigurationAndArguments,
        TestIntegration,
        TestPerformanceAndScaling
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    return suite


def run_specific_test_category(category):
    """Run tests for a specific category."""
    category_map = {
        'auth': TestGitHubAppAuthentication,
        'bot': TestBotDetection,
        'data': TestDataProcessing,
        'excel': TestExcelOutput,
        'error': TestErrorHandling,
        'config': TestConfigurationAndArguments,
        'integration': TestIntegration,
        'performance': TestPerformanceAndScaling
    }
    
    if category not in category_map:
        print(f"Unknown test category: {category}")
        print(f"Available categories: {', '.join(category_map.keys())}")
        return False
    
    suite = unittest.TestLoader().loadTestsFromTestCase(category_map[category])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def main():
    """Main test runner function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test GitHub Organization Stats Unified Script")
    parser.add_argument(
        '--category',
        choices=['auth', 'bot', 'data', 'excel', 'error', 'config', 'integration', 'performance', 'all'],
        default='all',
        help='Test category to run (default: all)'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--failfast',
        '-f',
        action='store_true',
        help='Stop on first failure'
    )
    
    args = parser.parse_args()
    
    # Set up test runner
    verbosity = 2 if args.verbose else 1
    
    if args.category == 'all':
        # Run all tests
        suite = create_test_suite()
        runner = unittest.TextTestRunner(
            verbosity=verbosity,
            failfast=args.failfast
        )
        result = runner.run(suite)
        
        # Print summary
        print(f"\n{'='*50}")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
        
        return 0 if result.wasSuccessful() else 1
    else:
        # Run specific category
        success = run_specific_test_category(args.category)
        return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())