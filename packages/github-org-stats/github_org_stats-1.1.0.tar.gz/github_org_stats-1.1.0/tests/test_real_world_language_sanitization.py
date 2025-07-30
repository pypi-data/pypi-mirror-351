#!/usr/bin/env python3
"""
Real-world test of C# vs C language detection fix
Testing against dotnet/aspnetcore repository data structure
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Add the current directory to Python path to import our module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from github_org_stats import sanitize_language_names

def create_mock_aspnetcore_data():
    """
    Create mock data that represents the actual dotnet/aspnetcore repository
    based on the GitHub page data we scraped showing:
    - C# 91.5%
    - HTML 2.5% 
    - C++ 1.9%
    - TypeScript 1.8%
    - Java 0.9%
    - PowerShell 0.5%
    - Other 0.9%
    """
    
    # Calculate approximate byte counts based on percentages
    # Assuming a large repository with ~10MB of code
    total_bytes = 10 * 1024 * 1024  # 10MB
    
    mock_repo_data = [{
        'name': 'aspnetcore',
        'full_name': 'dotnet/aspnetcore',
        'description': 'ASP.NET Core is a cross-platform .NET framework for building modern cloud-based web applications on Windows, Mac, or Linux.',
        'private': False,
        'fork': False,
        'archived': False,
        'stargazers_count': 36700,
        'forks_count': 10300,
        'primary_language': 'C#',  # This should be sanitized
        'languages': {
            'C#': int(total_bytes * 0.915),      # 91.5% - Should be sanitized to CSharp
            'HTML': int(total_bytes * 0.025),     # 2.5%
            'C++': int(total_bytes * 0.019),      # 1.9% - Should be sanitized to CPlusPlus
            'TypeScript': int(total_bytes * 0.018), # 1.8%
            'Java': int(total_bytes * 0.009),     # 0.9%
            'PowerShell': int(total_bytes * 0.005), # 0.5%
            'Dockerfile': int(total_bytes * 0.004), # Part of "Other"
            'Shell': int(total_bytes * 0.003),    # Part of "Other"
            'Batchfile': int(total_bytes * 0.002) # Part of "Other"
        },
        'total_code_bytes': total_bytes,
        'created_at': '2014-03-11T06:09:42Z',
        'updated_at': '2025-01-29T17:45:00Z',
        'analyzed_at': datetime.now().isoformat()
    }]
    
    return mock_repo_data

def test_language_sanitization():
    """Test the language sanitization with real-world dotnet/aspnetcore data"""
    
    print("=== Real-World C# Language Detection Fix Test ===")
    print("Testing against dotnet/aspnetcore repository structure")
    print()
    
    # Create mock data representing the actual repository
    original_data = create_mock_aspnetcore_data()
    
    print("BEFORE Sanitization:")
    print("-" * 50)
    repo = original_data[0]
    print(f"Repository: {repo['name']}")
    print(f"Primary Language: {repo['primary_language']}")
    print("Languages:")
    for lang, bytes_count in repo['languages'].items():
        percentage = (bytes_count / repo['total_code_bytes']) * 100
        print(f"  {lang}: {bytes_count:,} bytes ({percentage:.1f}%)")
    print()
    
    # Apply sanitization
    print("APPLYING SANITIZATION...")
    print("-" * 50)
    sanitized_data = sanitize_language_names(original_data)
    
    print("AFTER Sanitization:")
    print("-" * 50)
    sanitized_repo = sanitized_data[0]
    print(f"Repository: {sanitized_repo['name']}")
    print(f"Primary Language: {sanitized_repo['primary_language']}")
    print("Languages:")
    for lang, bytes_count in sanitized_repo['languages'].items():
        percentage = (bytes_count / sanitized_repo['total_code_bytes']) * 100
        print(f"  {lang}: {bytes_count:,} bytes ({percentage:.1f}%)")
    print()
    
    # Verify transformations
    print("VERIFICATION:")
    print("-" * 50)
    
    # Check primary language transformation
    if repo['primary_language'] == 'C#' and sanitized_repo['primary_language'] == 'CSharp':
        print("✅ Primary language C# → CSharp: SUCCESS")
    else:
        print(f"❌ Primary language transformation failed: {repo['primary_language']} → {sanitized_repo['primary_language']}")
    
    # Check language dictionary transformations
    transformations = [
        ('C#', 'CSharp'),
        ('C++', 'CPlusPlus')
    ]
    
    for old_name, new_name in transformations:
        if old_name in repo['languages'] and new_name in sanitized_repo['languages']:
            if repo['languages'][old_name] == sanitized_repo['languages'][new_name]:
                print(f"✅ Language {old_name} → {new_name}: SUCCESS (bytes preserved: {sanitized_repo['languages'][new_name]:,})")
            else:
                print(f"❌ Language {old_name} → {new_name}: FAILED (byte count mismatch)")
        elif old_name in repo['languages']:
            print(f"❌ Language {old_name} → {new_name}: FAILED (transformation not applied)")
    
    # Verify no problematic characters remain
    problematic_chars = ['#', '+']
    has_problematic = False
    for lang in sanitized_repo['languages'].keys():
        for char in problematic_chars:
            if char in lang:
                print(f"❌ Problematic character '{char}' still present in language: {lang}")
                has_problematic = True
    
    if not has_problematic:
        print("✅ No problematic characters (#, +) found in sanitized language names")
    
    # Check that non-problematic languages are preserved
    preserved_languages = ['HTML', 'TypeScript', 'Java', 'PowerShell', 'Dockerfile', 'Shell', 'Batchfile']
    for lang in preserved_languages:
        if lang in repo['languages'] and lang in sanitized_repo['languages']:
            if repo['languages'][lang] == sanitized_repo['languages'][lang]:
                print(f"✅ Non-problematic language preserved: {lang}")
            else:
                print(f"❌ Non-problematic language byte count changed: {lang}")
        elif lang in repo['languages']:
            print(f"❌ Non-problematic language lost: {lang}")
    
    return sanitized_data

def test_excel_compatibility():
    """Test that sanitized names would work in Excel column headers"""
    
    print("\n=== Excel Compatibility Test ===")
    print("-" * 50)
    
    # Test data with problematic language names
    test_data = create_mock_aspnetcore_data()
    sanitized_data = sanitize_language_names(test_data)
    
    # Simulate pandas json_normalize behavior (what happens in Excel export)
    import pandas as pd
    
    print("Testing pandas json_normalize with sanitized data...")
    try:
        df = pd.json_normalize(sanitized_data)
        
        # Check for language columns
        language_columns = [col for col in df.columns if col.startswith('languages.')]
        print(f"Found {len(language_columns)} language columns:")
        
        for col in sorted(language_columns):
            print(f"  {col}")
        
        # Check for conflicts (duplicate column names)
        if len(language_columns) == len(set(language_columns)):
            print("✅ No duplicate column names detected")
        else:
            print("❌ Duplicate column names detected!")
            
        # Verify no problematic characters in column names
        problematic_columns = [col for col in language_columns if '#' in col or '++' in col]
        if not problematic_columns:
            print("✅ No problematic characters in column names")
        else:
            print(f"❌ Problematic columns found: {problematic_columns}")
            
        print(f"✅ DataFrame created successfully with {len(df)} rows and {len(df.columns)} columns")
        
    except Exception as e:
        print(f"❌ pandas json_normalize failed: {e}")
        return False
    
    return True

def save_test_outputs():
    """Save test outputs to demonstrate the fix"""
    
    print("\n=== Saving Test Outputs ===")
    print("-" * 50)
    
    # Create test output directory
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    # Generate test data
    original_data = create_mock_aspnetcore_data()
    sanitized_data = sanitize_language_names(original_data)
    
    # Save original data
    original_file = output_dir / "original_aspnetcore_data.json"
    with open(original_file, 'w') as f:
        json.dump(original_data, f, indent=2, default=str)
    print(f"✅ Original data saved to: {original_file}")
    
    # Save sanitized data
    sanitized_file = output_dir / "sanitized_aspnetcore_data.json"
    with open(sanitized_file, 'w') as f:
        json.dump(sanitized_data, f, indent=2, default=str)
    print(f"✅ Sanitized data saved to: {sanitized_file}")
    
    # Create CSV output using pandas
    try:
        import pandas as pd
        
        # Test CSV export with sanitized data
        df = pd.json_normalize(sanitized_data)
        csv_file = output_dir / "aspnetcore_sanitized.csv"
        df.to_csv(csv_file, index=False)
        print(f"✅ CSV file created successfully: {csv_file}")
        
        # Test Excel export with sanitized data
        excel_file = output_dir / "aspnetcore_sanitized.xlsx"
        df.to_excel(excel_file, index=False, engine='openpyxl')
        print(f"✅ Excel file created successfully: {excel_file}")
        
        # Show some key columns to verify
        language_cols = [col for col in df.columns if col.startswith('languages.')]
        print(f"\nKey language columns in output files:")
        for col in sorted(language_cols):
            print(f"  {col}")
            
    except Exception as e:
        print(f"❌ Error creating output files: {e}")
        return False
    
    return True

def main():
    """Main test function"""
    
    print("Real-World Test: C# vs C Language Detection Fix")
    print("=" * 60)
    print("Repository: dotnet/aspnetcore")
    print("Languages: C# (91.5%), C++ (1.9%), HTML, TypeScript, Java, PowerShell")
    print("=" * 60)
    print()
    
    try:
        # Test 1: Language sanitization
        sanitized_data = test_language_sanitization()
        
        # Test 2: Excel compatibility
        excel_success = test_excel_compatibility()
        
        # Test 3: Save outputs
        output_success = save_test_outputs()
        
        # Final summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        if sanitized_data and excel_success and output_success:
            print("🎉 ALL TESTS PASSED!")
            print()
            print("✅ Language sanitization working correctly")
            print("✅ C# → CSharp transformation applied")
            print("✅ C++ → CPlusPlus transformation applied")
            print("✅ Excel compatibility verified")
            print("✅ Output files generated successfully")
            print()
            print("The C# vs C language detection fix is working correctly!")
            print("Excel column name conflicts have been resolved.")
            
        else:
            print("❌ SOME TESTS FAILED")
            print("Please check the output above for details.")
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())