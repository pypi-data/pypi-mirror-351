# GitHub Organization Statistics Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![GitHub Issues](https://img.shields.io/github/issues/zoharbabin/github-org-stats.svg)](https://github.com/zoharbabin/github-org-stats/issues)
[![GitHub Stars](https://img.shields.io/github/stars/zoharbabin/github-org-stats.svg)](https://github.com/zoharbabin/github-org-stats/stargazers)

A comprehensive, open-source tool for analyzing GitHub organization statistics including repository metrics, contributor activity, code quality insights, and **revolutionary multi-organization analysis** with GitHub Apps.

## 🚀 NEW in v1.1.0: Multi-Organization Analysis

**Analyze multiple organizations in a single command!** Use the new `--org-ids` parameter to process multiple GitHub organizations simultaneously, combining all data into unified output files while maintaining organization attribution.

```bash
# Analyze multiple organizations in one command
github-org-stats --org-ids "org1:install_id1,org2:install_id2,org3:install_id3" --format all
```

## 🚀 Features

### Revolutionary Multi-Organization Analysis
- **🆕 Single Command Multi-Org**: Analyze multiple organizations in one run with `--org-ids`
- **🔄 Unified Output**: All repository data combined into single files with organization attribution
- **📊 Enhanced Excel Reports**: Additional "Organization_Breakdown" sheet for multi-org analysis
- **🔐 Smart Authentication**: Automatic GitHub App token management across organizations
- **⚡ Efficient Processing**: Intelligent distribution of API limits across organizations

### Core Analysis Features
- **Repository Analysis**: Comprehensive metrics including stars, forks, issues, languages, and activity
- **Contributor Insights**: Detailed contributor analysis with bot filtering capabilities
- **Code Quality Metrics**: Language statistics, dependency analysis, and security insights
- **GitHub App Integration**: Enterprise-grade authentication for analyzing multiple organizations
- **Flexible Output**: JSON, CSV, and Excel formats with rich formatting
- **Advanced Filtering**: Include/exclude forks, archived repos, empty repos, and bot accounts
- **Rate Limit Management**: Intelligent rate limiting and retry mechanisms
- **Error Handling**: Robust error handling with detailed logging and recovery

### Advanced Features
- **Language Name Sanitization**: Intelligent handling of problematic language names (C#, C++, F#) to prevent Excel column conflicts
- **Dependency Analysis**: Detect and analyze dependencies from package.json, requirements.txt, Gemfile, pom.xml, build.gradle, Cargo.toml, and go.mod
- **Submodule Detection**: Identify and catalog Git submodules
- **GitHub Actions Integration**: Analyze workflow configurations and recent runs
- **Branch Protection Analysis**: Check default branch protection settings
- **Release Tracking**: Monitor latest releases and version information
- **Security Insights**: Collaborator analysis, team permissions, and admin detection
- **Bot Detection**: Advanced bot account filtering with configurable patterns
- **Performance Optimization**: Adaptive batch sizing and memory management

## 📦 Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Quick Install

```bash
git clone https://github.com/zoharbabin/github-org-stats.git
cd github-org-stats
pip install -e .
```

### Install from PyPI (when available)

```bash
pip install github-org-stats
```

## 🔧 Quick Start

### 🆕 Multi-Organization Analysis (Recommended)

Analyze multiple organizations in a single command:

```bash
# Set environment variables
export GITHUB_APP_ID=12345
export GITHUB_PRIVATE_KEY_PATH=/path/to/private-key.pem

# Analyze multiple organizations
github-org-stats \
  --org-ids "org1:install_id1,org2:install_id2,org3:install_id3" \
  --include-forks \
  --include-archived \
  --exclude-bots \
  --max-repos 6000 \
  --days-back 365 \
  --format all \
  --output-dir ./multi_org_reports
```

### Single Organization Analysis

Analyze a single GitHub organization:

```bash
# With personal access token
python github_org_stats.py --org your-org --token ghp_your_token_here

# With GitHub App
python github_org_stats.py \
  --org your-org \
  --app-id 12345 \
  --private-key /path/to/private-key.pem \
  --installation-id 67890
```

### Advanced Single Organization Usage

```bash
# Generate all output formats with comprehensive analysis
python github_org_stats.py \
  --org your-org \
  --token ghp_token \
  --format all \
  --exclude-bots \
  --include-forks \
  --include-archived \
  --max-repos 1000 \
  --days-back 365 \
  --output-dir ./reports
```

## 📋 Command Line Arguments

### Authentication Options
- `--token` - GitHub personal access token
- `--app-id` - GitHub App ID for authentication
- `--private-key` - Path to GitHub App private key file
- `--installation-id` - GitHub App installation ID (supports multiple: "org1:id1,org2:id2" or single: "12345")
- `--installation-ids` - Alias for --installation-id

### Scope Options
- `--org` - GitHub organization name to analyze (single organization mode)
- `--org-ids` - **NEW** Multiple organizations with installation IDs in format "org1:id1,org2:id2" (multi-organization mode)
- `--repos` - Specific repositories to analyze (space-separated list)
- `--days-back` - Number of days to look back for activity (default: 30)

### Multi-Organization Mode
The new `--org-ids` parameter enables analyzing multiple organizations in a single command run:
- Format: `"org1:installation_id1,org2:installation_id2,org3:installation_id3"`
- All data is combined into unified output files
- Excel output includes an additional "Organization_Breakdown" sheet
- Each repository record includes an "organization" field
- Cannot be used together with `--org` (choose single or multi-organization mode)

### Output Options
- `--output-dir` - Output directory for reports (default: output)
- `--format` - Output format: json, csv, excel, all (default: excel)
- `--config` - Configuration file path (JSON format)

### Logging Options
- `--log-level` - Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO)
- `--log-file` - Log file path (default: console only)

### Analysis Options
- `--include-forks` - Include forked repositories in analysis
- `--include-archived` - Include archived repositories in analysis
- `--max-repos` - Maximum number of repositories to analyze (default: 100)
- `--exclude-bots` - Exclude bot accounts from contributor analysis and commit statistics
- `--include-empty` - Include repositories with no commits in the specified timeframe

## 🔐 Authentication

### Personal Access Token

For individual use or small-scale analysis:

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with these permissions:
   - `repo` - Full control of private repositories
   - `read:org` - Read organization membership
   - `read:user` - Read user profile data

```bash
# Using token directly
python github_org_stats.py --org your-org --token ghp_your_token_here

# Using environment variable
export GITHUB_TOKEN=ghp_your_token_here
python github_org_stats.py --org your-org --token $GITHUB_TOKEN
```

### GitHub App Authentication

For enterprise use, multi-organization analysis, and higher rate limits:

#### Setup GitHub App

1. Go to GitHub Settings → Developer settings → GitHub Apps
2. Create a new GitHub App with these permissions:
   - **Repository permissions:**
     - Contents: Read
     - Issues: Read
     - Metadata: Read
     - Pull requests: Read
     - Actions: Read
   - **Organization permissions:**
     - Members: Read
     - Administration: Read

3. Generate and download a private key
4. Install the app on target organizations
5. Note the App ID and Installation IDs

#### Using GitHub App

```bash
# Single organization
python github_org_stats.py \
  --org your-org \
  --app-id 12345 \
  --private-key /path/to/private-key.pem \
  --installation-id 67890

# Multiple organizations
python github_org_stats.py \
  --org your-org \
  --app-id 12345 \
  --private-key /path/to/private-key.pem \
  --installation-id "org1:111,org2:222,org3:333"
```

#### Environment Variables

```bash
export GITHUB_APP_ID=12345
export GITHUB_PRIVATE_KEY_PATH=/path/to/private-key.pem
python github_org_stats.py --org your-org
```

## 📊 Output Formats

### Excel Output (Default)
Professional Excel workbook with multiple sheets:
- **Repository_Data**: Complete repository information with all metrics and organization attribution
- **Summary**: High-level statistics across all analyzed organizations
- **🆕 Organization_Breakdown**: Per-organization statistics (multi-org mode only)
- **Contributors**: Top contributors analysis with contribution counts
- **Languages**: Language distribution and code statistics
- **Errors**: Error tracking and debugging information

### JSON Output
Structured JSON with complete data hierarchy:

**Single Organization:**
```json
{
  "organizations": ["your-org"],
  "analysis_mode": "single-organization",
  "analyzed_at": "2025-05-29T22:30:00",
  "total_repositories": 150,
  "repositories": [...]
}
```

**Multi-Organization:**
```json
{
  "organizations": ["org1", "org2", "org3"],
  "analysis_mode": "multi-organization",
  "analyzed_at": "2025-05-29T22:30:00",
  "total_repositories": 450,
  "repositories": [
    {
      "organization": "org1",
      "name": "repo1",
      "full_name": "org1/repo1",
      ...
    }
  ]
}
```

### CSV Output
Flattened data suitable for spreadsheet analysis and data processing tools, with organization column for multi-org analysis.

## ⚙️ Configuration File

Use a JSON configuration file for complex setups:

```bash
python github_org_stats.py --config config/example_config.json --org your-org
```

Example configuration:
```json
{
  "authentication": {
    "app_id": 12345,
    "private_key_path": "/path/to/private-key.pem",
    "installation_mappings": {
      "org1": 67890,
      "org2": 11111
    }
  },
  "analysis": {
    "days_back": 60,
    "max_repos": 200,
    "include_forks": false,
    "exclude_bots": true
  },
  "output": {
    "format": "excel",
    "output_dir": "./reports"
  }
}
```

## 🔍 Advanced Features

### Language Name Sanitization
Intelligent handling of problematic programming language names that can cause issues in Excel exports:

- **C# → CSharp**: Prevents conflicts with C language statistics
- **C++ → CPlusPlus**: Avoids Excel column name parsing issues
- **F# → FSharp**: Ensures proper Excel compatibility

**Benefits:**
- Eliminates Excel column name conflicts
- Preserves accurate language statistics and byte counts
- Maintains data integrity across all output formats
- Automatic transformation with comprehensive logging

**Example:**
```json
// Before sanitization
"languages": {"C#": 1500000, "C": 800000, "C++": 500000}

// After sanitization
"languages": {"CSharp": 1500000, "C": 800000, "CPlusPlus": 500000}
```

### Dependency Analysis
Automatically detects and analyzes dependencies from:
- **Node.js**: package.json
- **Python**: requirements.txt
- **Ruby**: Gemfile
- **Java**: pom.xml
- **Gradle**: build.gradle
- **Rust**: Cargo.toml
- **Go**: go.mod

### Bot Detection
Advanced bot account filtering with configurable patterns:
- GitHub Actions bots
- Dependabot and Renovate
- Code quality bots (CodeCov, SonarCloud)
- Security bots (Snyk, WhiteSource)
- Custom bot patterns

### GitHub Actions Integration
- Workflow count and status
- Recent workflow runs
- Action configuration analysis

### Security Analysis
- Branch protection settings
- Collaborator permissions
- Team access analysis
- Admin user identification

## 🧪 Testing

Run the comprehensive test suite:

```bash
cd tests
python test_github_org_stats.py
```

Run specific test categories:

```bash
python test_github_org_stats.py --category auth
python test_github_org_stats.py --category data
python test_github_org_stats.py --category excel
```

## 🛠️ Development Setup

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Install in development mode: `pip install -e .[dev]`
4. Make your changes
5. Run tests: `python -m pytest tests/`
6. Run linting: `black . && flake8`
7. Commit your changes: `git commit -m 'Add amazing feature'`
8. Push to the branch: `git push origin feature/amazing-feature`
9. Open a Pull Request

### Development Dependencies

Development dependencies are defined in [`pyproject.toml`](pyproject.toml) and can be installed with:

```bash
pip install -e .[dev]
```

### Code Style

This project uses:
- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking

## 🐛 Troubleshooting

### Common Issues

#### Authentication Errors
```
Error: Authentication required
```
**Solution**: Ensure you provide either `--token` or both `--app-id` and `--private-key`

#### Rate Limit Issues
```
Rate limit exceeded
```
**Solution**: 
- Use GitHub App authentication for higher limits
- Reduce `--max-repos` value
- Increase `--days-back` to reduce API calls

#### Permission Errors
```
403 Forbidden
```
**Solution**: 
- Verify token has required permissions (`repo`, `read:org`, `read:user`)
- For GitHub Apps, ensure proper installation and permissions

#### Memory Issues
```
MemoryError or system slowdown
```
**Solution**:
- Reduce `--max-repos` value
- Use `--format json` or `--format csv` instead of Excel
- Process organizations in smaller batches

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
python github_org_stats.py \
  --org your-org \
  --token your-token \
  --log-level DEBUG \
  --log-file debug.log
```

### Performance Optimization

For large organizations:
```bash
# Optimize for speed
python github_org_stats.py \
  --org large-org \
  --token your-token \
  --max-repos 500 \
  --days-back 30 \
  --exclude-bots \
  --format json
```

## 📈 Usage Examples

### Multi-Organization Analysis (Single Command)
Analyze multiple organizations in a single run using the new `--org-ids` parameter:

```bash
# Using environment variables (recommended)
export GITHUB_APP_ID=12345
export GITHUB_PRIVATE_KEY_PATH=/secure/enterprise-key.pem

python github_org_stats.py \
  --org-ids "kaltura:68242466,kaltura-ps:68357040" \
  --include-forks \
  --include-archived \
  --exclude-bots \
  --include-empty \
  --max-repos 6000 \
  --days-back 365 \
  --format all \
  --log-level INFO \
  --log-file multi_org_analysis.log \
  --output-dir ./multi_org_reports
```

### Multi-Organization Analysis with Explicit Parameters
```bash
python github_org_stats.py \
  --org-ids "first-org:11111,second-org:22222,third-org:33333" \
  --app-id 12345 \
  --private-key /secure/enterprise-key.pem \
  --include-forks \
  --include-archived \
  --exclude-bots \
  --include-empty \
  --max-repos 9000 \
  --days-back 365 \
  --format all \
  --log-level INFO \
  --log-file multi_org_analysis.log \
  --output-dir ./multi_org_reports
```

### Single Organization Analysis (Legacy Mode)
For analyzing a single organization:

```bash
python github_org_stats.py \
  --org enterprise-org \
  --installation-id 67890 \
  --include-forks \
  --include-archived \
  --exclude-bots \
  --include-empty \
  --max-repos 3000 \
  --days-back 365 \
  --format all \
  --log-level INFO \
  --log-file enterprise_analysis.log \
  --output-dir ./enterprise_reports
```

### Enterprise Analysis with Explicit Parameters
```bash
python github_org_stats.py \
  --org enterprise-org \
  --app-id 12345 \
  --private-key /secure/enterprise-key.pem \
  --installation-id 67890 \
  --include-forks \
  --include-archived \
  --exclude-bots \
  --include-empty \
  --max-repos 3000 \
  --days-back 365 \
  --format all \
  --log-level INFO \
  --log-file enterprise_analysis.log \
  --output-dir ./enterprise_reports
```

### Quick Overview
```bash
python github_org_stats.py \
  --org your-org \
  --token ghp_token \
  --max-repos 10 \
  --days-back 7 \
  --format json
```

### Comprehensive Analysis with Personal Access Token
```bash
python github_org_stats.py \
  --org your-org \
  --token ghp_token \
  --include-forks \
  --include-archived \
  --exclude-bots \
  --include-empty \
  --max-repos 1000 \
  --days-back 365 \
  --format all \
  --log-level INFO \
  --log-file comprehensive_analysis.log \
  --output-dir ./comprehensive_reports
```

### Large Scale Analysis (High Repository Count)
For organizations with many repositories:
```bash
python github_org_stats.py \
  --org large-org \
  --installation-id 99999 \
  --include-forks \
  --include-archived \
  --exclude-bots \
  --include-empty \
  --max-repos 5000 \
  --days-back 365 \
  --format all \
  --log-level INFO \
  --log-file large_org_analysis.log \
  --output-dir ./large_org_reports
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: This comprehensive README and example configurations
- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/zoharbabin/github-org-stats/issues)
- **Discussions**: Join the conversation in [GitHub Discussions](https://github.com/zoharbabin/github-org-stats/discussions)

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=zoharbabin/github-org-stats&type=Date)](https://star-history.com/#zoharbabin/github-org-stats&Date)

## 🙏 Acknowledgments

- Thanks to all contributors who have helped improve this tool
- Built with [PyGithub](https://github.com/PyGithub/PyGithub) for GitHub API access
- Inspired by the need for comprehensive GitHub organization analysis
- Special thanks to the open-source community for feedback and contributions

---

**Made with ❤️ by the open-source community**

**Version 1.1.0** | [Changelog](CHANGELOG.md) | [Contributing Guidelines](CONTRIBUTING.md)

## 🎯 What's New in v1.1.0

- **🚀 Multi-Organization Analysis**: Analyze multiple GitHub organizations in a single command
- **🔧 Enhanced Authentication**: Better environment variable support and GitHub App integration
- **📊 Improved Excel Output**: Organization breakdown sheets and enhanced reporting
- **🛠️ Better Error Handling**: More robust authentication and API error management
- **📖 Updated Documentation**: Comprehensive examples and usage guides

Ready to analyze your GitHub organizations? Get started with the [Quick Start](#-quick-start) guide!