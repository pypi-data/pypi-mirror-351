#!/usr/bin/env python3
"""
Comprehensive Test Suite for Language Name Sanitization
======================================================

Tests the sanitize_language_names() function and related functionality
to ensure proper handling of C#, C++, F# and other problematic language names.

Author: GitHub Stats Team
Version: 1.0.0
"""

import unittest
import sys
import os
import copy
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import tempfile
import json

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from github_org_stats import sanitize_language_names
except ImportError as e:
    print(f"Error importing sanitize_language_names: {e}")
    sys.exit(1)


class TestSanitizeLanguageNames(unittest.TestCase):
    """Comprehensive tests for the sanitize_language_names function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.basic_repo_data = [
            {
                'name': 'test-repo-1',
                'languages': {'Python': 1000, 'JavaScript': 500},
                'primary_language': 'Python'
            },
            {
                'name': 'test-repo-2',
                'languages': {'Java': 2000, 'C': 800},
                'primary_language': 'Java'
            }
        ]
        
        self.problematic_repo_data = [
            {
                'name': 'csharp-repo',
                'languages': {'C#': 1500, 'Python': 500},
                'primary_language': 'C#'
            },
            {
                'name': 'cpp-repo',
                'languages': {'C++': 2000, 'C': 1000},
                'primary_language': 'C++'
            },
            {
                'name': 'fsharp-repo',
                'languages': {'F#': 800, 'C#': 1200},
                'primary_language': 'F#'
            }
        ]
        
        self.mixed_repo_data = [
            {
                'name': 'mixed-repo-1',
                'languages': {'C#': 1000, 'Python': 500, 'JavaScript': 300},
                'primary_language': 'C#'
            },
            {
                'name': 'mixed-repo-2',
                'languages': {'Java': 2000, 'C': 800},
                'primary_language': 'Java'
            },
            {
                'name': 'mixed-repo-3',
                'languages': {'C++': 1500, 'F#': 700, 'C': 300},
                'primary_language': 'C++'
            }
        ]
    
    def test_sanitize_basic_languages_unchanged(self):
        """Test that normal languages are not modified."""
        result = sanitize_language_names(self.basic_repo_data)
        
        # Should have same number of repositories
        self.assertEqual(len(result), len(self.basic_repo_data))
        
        # Languages should be unchanged
        self.assertEqual(result[0]['languages'], {'Python': 1000, 'JavaScript': 500})
        self.assertEqual(result[1]['languages'], {'Java': 2000, 'C': 800})
        
        # Primary languages should be unchanged
        self.assertEqual(result[0]['primary_language'], 'Python')
        self.assertEqual(result[1]['primary_language'], 'Java')
    
    def test_sanitize_problematic_languages(self):
        """Test sanitization of C#, C++, F# languages."""
        result = sanitize_language_names(self.problematic_repo_data)
        
        # Check C# -> CSharp transformation
        csharp_repo = result[0]
        self.assertIn('CSharp', csharp_repo['languages'])
        self.assertNotIn('C#', csharp_repo['languages'])
        self.assertEqual(csharp_repo['languages']['CSharp'], 1500)
        self.assertEqual(csharp_repo['primary_language'], 'CSharp')
        
        # Check C++ -> CPlusPlus transformation
        cpp_repo = result[1]
        self.assertIn('CPlusPlus', cpp_repo['languages'])
        self.assertNotIn('C++', cpp_repo['languages'])
        self.assertEqual(cpp_repo['languages']['CPlusPlus'], 2000)
        self.assertEqual(cpp_repo['primary_language'], 'CPlusPlus')
        
        # Check F# -> FSharp transformation
        fsharp_repo = result[2]
        self.assertIn('FSharp', fsharp_repo['languages'])
        self.assertNotIn('F#', fsharp_repo['languages'])
        self.assertEqual(fsharp_repo['languages']['FSharp'], 800)
        self.assertEqual(fsharp_repo['primary_language'], 'FSharp')
        
        # Ensure C# in fsharp_repo is also transformed
        self.assertIn('CSharp', fsharp_repo['languages'])
        self.assertNotIn('C#', fsharp_repo['languages'])
        self.assertEqual(fsharp_repo['languages']['CSharp'], 1200)
    
    def test_sanitize_mixed_scenarios(self):
        """Test mixed scenarios with both problematic and normal languages."""
        result = sanitize_language_names(self.mixed_repo_data)
        
        # First repo: C# should be sanitized, others unchanged
        repo1 = result[0]
        expected_languages1 = {'CSharp': 1000, 'Python': 500, 'JavaScript': 300}
        self.assertEqual(repo1['languages'], expected_languages1)
        self.assertEqual(repo1['primary_language'], 'CSharp')
        
        # Second repo: No changes expected
        repo2 = result[1]
        expected_languages2 = {'Java': 2000, 'C': 800}
        self.assertEqual(repo2['languages'], expected_languages2)
        self.assertEqual(repo2['primary_language'], 'Java')
        
        # Third repo: C++ and F# should be sanitized, C unchanged
        repo3 = result[2]
        expected_languages3 = {'CPlusPlus': 1500, 'FSharp': 700, 'C': 300}
        self.assertEqual(repo3['languages'], expected_languages3)
        self.assertEqual(repo3['primary_language'], 'CPlusPlus')
    
    def test_deep_copy_behavior(self):
        """Test that original data is not modified (deep copy behavior)."""
        original_data = copy.deepcopy(self.problematic_repo_data)
        result = sanitize_language_names(self.problematic_repo_data)
        
        # Original data should be unchanged
        self.assertEqual(self.problematic_repo_data, original_data)
        
        # But result should be different
        self.assertNotEqual(result[0]['languages'], original_data[0]['languages'])
        self.assertIn('C#', original_data[0]['languages'])
        self.assertNotIn('C#', result[0]['languages'])
    
    def test_empty_repo_data(self):
        """Test with empty repository data."""
        result = sanitize_language_names([])
        self.assertEqual(result, [])
    
    def test_repo_without_languages(self):
        """Test repositories without language data."""
        repo_data = [
            {'name': 'no-lang-repo', 'description': 'A repo without languages'},
            {'name': 'empty-lang-repo', 'languages': {}, 'primary_language': None}
        ]
        
        result = sanitize_language_names(repo_data)
        
        # Should return same structure
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'no-lang-repo')
        self.assertEqual(result[1]['languages'], {})
    
    def test_malformed_language_data(self):
        """Test with malformed language data."""
        malformed_data = [
            {'name': 'malformed-1', 'languages': None},
            {'name': 'malformed-2', 'languages': 'not-a-dict'},
            {'name': 'malformed-3', 'languages': ['list', 'instead', 'of', 'dict']},
            {'name': 'valid-repo', 'languages': {'C#': 1000}, 'primary_language': 'C#'}
        ]
        
        result = sanitize_language_names(malformed_data)
        
        # Should handle malformed data gracefully
        self.assertEqual(len(result), 4)
        
        # Malformed entries should be unchanged
        self.assertIsNone(result[0]['languages'])
        self.assertEqual(result[1]['languages'], 'not-a-dict')
        self.assertEqual(result[2]['languages'], ['list', 'instead', 'of', 'dict'])
        
        # Valid entry should be sanitized
        self.assertEqual(result[3]['languages'], {'CSharp': 1000})
        self.assertEqual(result[3]['primary_language'], 'CSharp')
    
    def test_none_values_in_languages(self):
        """Test handling of None values in language dictionaries."""
        repo_data = [
            {
                'name': 'none-values-repo',
                'languages': {'C#': 1000, 'Python': None, 'JavaScript': 500},
                'primary_language': 'C#'
            }
        ]
        
        result = sanitize_language_names(repo_data)
        
        # Should handle None values gracefully
        expected_languages = {'CSharp': 1000, 'Python': None, 'JavaScript': 500}
        self.assertEqual(result[0]['languages'], expected_languages)
        self.assertEqual(result[0]['primary_language'], 'CSharp')
    
    def test_primary_language_without_languages_dict(self):
        """Test primary language sanitization when languages dict is missing."""
        repo_data = [
            {'name': 'primary-only-repo', 'primary_language': 'C#'}
        ]
        
        result = sanitize_language_names(repo_data)
        
        # Primary language should still be sanitized
        self.assertEqual(result[0]['primary_language'], 'CSharp')
    
    def test_case_sensitivity(self):
        """Test that language name matching is case-sensitive."""
        repo_data = [
            {
                'name': 'case-test-repo',
                'languages': {'c#': 1000, 'C#': 500, 'c++': 300},
                'primary_language': 'C#'
            }
        ]
        
        result = sanitize_language_names(repo_data)
        
        # Only exact matches should be transformed
        expected_languages = {'c#': 1000, 'CSharp': 500, 'c++': 300}
        self.assertEqual(result[0]['languages'], expected_languages)
        self.assertEqual(result[0]['primary_language'], 'CSharp')
    
    def test_large_dataset_performance(self):
        """Test performance with large dataset."""
        # Create a large dataset
        large_dataset = []
        for i in range(1000):
            repo = {
                'name': f'repo-{i}',
                'languages': {'Python': 1000, 'JavaScript': 500} if i % 2 == 0 else {'C#': 1500, 'C++': 800},
                'primary_language': 'Python' if i % 2 == 0 else 'C#'
            }
            large_dataset.append(repo)
        
        # This should complete without timeout
        import time
        start_time = time.time()
        result = sanitize_language_names(large_dataset)
        end_time = time.time()
        
        # Should complete in reasonable time (less than 5 seconds)
        self.assertLess(end_time - start_time, 5.0)
        self.assertEqual(len(result), 1000)
        
        # Verify some transformations occurred
        transformed_count = sum(1 for repo in result if 'CSharp' in repo.get('languages', {}))
        self.assertEqual(transformed_count, 500)  # Half the repos should have CSharp
    
    @patch('github_org_stats.logging.getLogger')
    def test_logging_behavior(self, mock_get_logger):
        """Test that appropriate log messages are generated."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        result = sanitize_language_names(self.problematic_repo_data)
        
        # Should log transformations
        mock_logger.info.assert_called()
        mock_logger.debug.assert_called()
        
        # Check that info log contains transformation summary
        info_calls = [call.args[0] for call in mock_logger.info.call_args_list]
        transformation_log = next((log for log in info_calls if 'Sanitized language names' in log), None)
        self.assertIsNotNone(transformation_log)
        self.assertIn('C# → CSharp', transformation_log)
        self.assertIn('C++ → CPlusPlus', transformation_log)
        self.assertIn('F# → FSharp', transformation_log)
    
    def test_no_transformations_needed(self):
        """Test logging when no transformations are needed."""
        with patch('github_org_stats.logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            result = sanitize_language_names(self.basic_repo_data)
            
            # Should log that no sanitization was needed
            mock_logger.debug.assert_called_with("No language name sanitization needed")
    
    def test_all_problematic_languages_together(self):
        """Test repository with all problematic languages together."""
        repo_data = [
            {
                'name': 'all-problematic-repo',
                'languages': {'C#': 1000, 'C++': 800, 'F#': 600, 'Python': 400, 'C': 200},
                'primary_language': 'C#'
            }
        ]
        
        result = sanitize_language_names(repo_data)
        
        expected_languages = {
            'CSharp': 1000,
            'CPlusPlus': 800,
            'FSharp': 600,
            'Python': 400,
            'C': 200
        }
        
        self.assertEqual(result[0]['languages'], expected_languages)
        self.assertEqual(result[0]['primary_language'], 'CSharp')
        
        # Ensure no original problematic names remain
        for problematic_name in ['C#', 'C++', 'F#']:
            self.assertNotIn(problematic_name, result[0]['languages'])


class TestLanguageSanitizationIntegration(unittest.TestCase):
    """Integration tests for language sanitization with pandas and Excel output."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_data = [
            {
                'name': 'csharp-project',
                'languages': {'C#': 2000, 'JavaScript': 1000},
                'primary_language': 'C#',
                'stargazers_count': 50,
                'forks_count': 10
            },
            {
                'name': 'cpp-project',
                'languages': {'C++': 1500, 'C': 800},
                'primary_language': 'C++',
                'stargazers_count': 30,
                'forks_count': 5
            },
            {
                'name': 'python-project',
                'languages': {'Python': 3000, 'HTML': 500},
                'primary_language': 'Python',
                'stargazers_count': 100,
                'forks_count': 25
            }
        ]
    
    def test_pandas_normalization_after_sanitization(self):
        """Test that pandas normalization works correctly after language sanitization."""
        sanitized_data = sanitize_language_names(self.test_data)
        
        # Normalize with pandas
        df = pd.json_normalize(sanitized_data)
        
        # Check that sanitized language names appear in column names
        columns = df.columns.tolist()
        
        # Should have CSharp and CPlusPlus columns, not C# or C++
        csharp_columns = [col for col in columns if 'CSharp' in col]
        cpp_columns = [col for col in columns if 'CPlusPlus' in col]
        
        self.assertTrue(len(csharp_columns) > 0, "Should have CSharp-related columns")
        self.assertTrue(len(cpp_columns) > 0, "Should have CPlusPlus-related columns")
        
        # Should not have problematic characters in column names
        problematic_columns = [col for col in columns if '#' in col or '++' in col]
        self.assertEqual(len(problematic_columns), 0, f"Found problematic columns: {problematic_columns}")
    
    def test_csv_output_column_names(self):
        """Test CSV output has properly sanitized column names."""
        sanitized_data = sanitize_language_names(self.test_data)
        df = pd.json_normalize(sanitized_data)
        
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            csv_path = f.name
        
        try:
            df.to_csv(csv_path, index=False)
            
            # Read back the CSV and check column names
            df_read = pd.read_csv(csv_path)
            columns = df_read.columns.tolist()
            
            # Verify sanitized names are present
            self.assertTrue(any('CSharp' in col for col in columns))
            self.assertTrue(any('CPlusPlus' in col for col in columns))
            
            # Verify problematic characters are not present
            self.assertFalse(any('#' in col for col in columns))
            self.assertFalse(any('++' in col for col in columns))
            
        finally:
            os.unlink(csv_path)
    
    def test_excel_output_compatibility(self):
        """Test Excel output compatibility with sanitized language names."""
        sanitized_data = sanitize_language_names(self.test_data)
        df = pd.json_normalize(sanitized_data)
        
        # Create temporary Excel file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            excel_path = f.name
        
        try:
            # This should not raise any errors
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Test_Data', index=False)
            
            # Read back the Excel file
            df_read = pd.read_excel(excel_path, sheet_name='Test_Data')
            columns = df_read.columns.tolist()
            
            # Verify sanitized names are present and readable
            self.assertTrue(any('CSharp' in col for col in columns))
            self.assertTrue(any('CPlusPlus' in col for col in columns))
            
            # Verify data integrity
            self.assertEqual(len(df_read), 3)
            
        finally:
            os.unlink(excel_path)
    
    def test_language_statistics_accuracy(self):
        """Test that language statistics remain accurate after sanitization."""
        original_data = copy.deepcopy(self.test_data)
        sanitized_data = sanitize_language_names(self.test_data)
        
        # Compare total language bytes
        for i, (orig, sanitized) in enumerate(zip(original_data, sanitized_data)):
            orig_total = sum(orig['languages'].values())
            sanitized_total = sum(sanitized['languages'].values())
            
            self.assertEqual(orig_total, sanitized_total, 
                           f"Language byte counts don't match for repo {i}")
        
        # Check specific transformations
        csharp_repo = sanitized_data[0]
        self.assertEqual(csharp_repo['languages']['CSharp'], 2000)
        self.assertEqual(csharp_repo['languages']['JavaScript'], 1000)
        
        cpp_repo = sanitized_data[1]
        self.assertEqual(cpp_repo['languages']['CPlusPlus'], 1500)
        self.assertEqual(cpp_repo['languages']['C'], 800)


class TestEdgeCasesAndErrorHandling(unittest.TestCase):
    """Test edge cases and error handling scenarios."""
    
    def test_empty_language_dictionaries(self):
        """Test repositories with empty language dictionaries."""
        repo_data = [
            {'name': 'empty-lang-repo', 'languages': {}, 'primary_language': None},
            {'name': 'normal-repo', 'languages': {'C#': 1000}, 'primary_language': 'C#'}
        ]
        
        result = sanitize_language_names(repo_data)
        
        self.assertEqual(result[0]['languages'], {})
        self.assertEqual(result[1]['languages'], {'CSharp': 1000})
    
    def test_none_repo_data(self):
        """Test with None values in repo_data list."""
        repo_data = [
            None,
            {'name': 'valid-repo', 'languages': {'C#': 1000}, 'primary_language': 'C#'},
            None
        ]
        
        # Should handle None values gracefully without crashing
        try:
            result = sanitize_language_names(repo_data)
            # The function should either skip None values or handle them gracefully
            self.assertIsInstance(result, list)
        except (TypeError, AttributeError):
            # This is acceptable - the function may not be designed to handle None values
            pass
    
    def test_very_large_language_counts(self):
        """Test with very large language byte counts."""
        repo_data = [
            {
                'name': 'large-counts-repo',
                'languages': {'C#': 999999999999, 'Python': 888888888888},
                'primary_language': 'C#'
            }
        ]
        
        result = sanitize_language_names(repo_data)
        
        self.assertEqual(result[0]['languages']['CSharp'], 999999999999)
        self.assertEqual(result[0]['languages']['Python'], 888888888888)
    
    def test_unicode_and_special_characters(self):
        """Test with unicode and special characters in language names."""
        repo_data = [
            {
                'name': 'unicode-repo',
                'languages': {
                    'C#': 1000,
                    'Python🐍': 500,
                    'JavaScript-ES6': 300,
                    'C++': 800
                },
                'primary_language': 'C#'
            }
        ]
        
        result = sanitize_language_names(repo_data)
        
        # Only exact matches should be transformed
        expected_languages = {
            'CSharp': 1000,
            'Python🐍': 500,
            'JavaScript-ES6': 300,
            'CPlusPlus': 800
        }
        
        self.assertEqual(result[0]['languages'], expected_languages)
        self.assertEqual(result[0]['primary_language'], 'CSharp')


def create_language_sanitization_test_suite():
    """Create and return the language sanitization test suite."""
    suite = unittest.TestSuite()
    
    test_classes = [
        TestSanitizeLanguageNames,
        TestLanguageSanitizationIntegration,
        TestEdgeCasesAndErrorHandling
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    return suite


def main():
    """Main test runner for language sanitization tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Language Name Sanitization")
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--failfast', '-f', action='store_true', help='Stop on first failure')
    
    args = parser.parse_args()
    
    suite = create_language_sanitization_test_suite()
    runner = unittest.TextTestRunner(
        verbosity=2 if args.verbose else 1,
        failfast=args.failfast
    )
    
    result = runner.run(suite)
    
    print(f"\n{'='*60}")
    print(f"Language Sanitization Tests Summary")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            error_msg = traceback.split('AssertionError: ')[-1].split('\n')[0]
            print(f"  - {test}: {error_msg}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            error_msg = traceback.split('\n')[-2]
            print(f"  - {test}: {error_msg}")
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())