# GitHub Organization Statistics Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![GitHub Issues](https://img.shields.io/github/issues/zoharbabin/github-org-stats.svg)](https://github.com/zoharbabin/github-org-stats/issues)
[![GitHub Stars](https://img.shields.io/github/stars/zoharbabin/github-org-stats.svg)](https://github.com/zoharbabin/github-org-stats/stargazers)

A comprehensive, open-source tool for analyzing GitHub organization statistics including repository metrics, contributor activity, code quality insights, and multi-organization support with GitHub Apps.

## 🚀 Features

- **Repository Analysis**: Comprehensive metrics including stars, forks, issues, languages, and activity
- **Contributor Insights**: Detailed contributor analysis with bot filtering capabilities
- **Code Quality Metrics**: Language statistics, dependency analysis, and security insights
- **Multi-Organization Support**: GitHub App authentication for analyzing multiple organizations
- **Flexible Output**: JSON, CSV, and Excel formats with rich formatting
- **Advanced Filtering**: Include/exclude forks, archived repos, empty repos, and bot accounts
- **Rate Limit Management**: Intelligent rate limiting and retry mechanisms
- **Error Handling**: Robust error handling with detailed logging and recovery

## 📦 Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Quick Install

```bash
git clone https://github.com/zoharbabin/github-org-stats.git
cd github-org-stats
pip install -r requirements.txt
```

## 🔧 Quick Start

### Basic Usage

Analyze a GitHub organization with a personal access token:

```bash
python github_org_stats.py --org your-org --token ghp_your_token_here
```

### GitHub App Authentication

For enterprise use and higher rate limits:

```bash
python github_org_stats.py \
  --org your-org \
  --app-id 12345 \
  --private-key /path/to/private-key.pem \
  --installation-id 67890
```

### Advanced Usage

```bash
# Generate all output formats with bot filtering
python github_org_stats.py \
  --org your-org \
  --token ghp_token \
  --format all \
  --exclude-bots \
  --days-back 90 \
  --output-dir ./reports
```

## 📊 Output Formats

### Excel Output (Default)
- **Repository_Data**: Complete repository information
- **Summary**: High-level organization statistics
- **Contributors**: Top contributors analysis
- **Languages**: Language distribution
- **Errors**: Error tracking information

### JSON Output
Structured JSON with complete data hierarchy for programmatic access.

### CSV Output
Flattened data suitable for spreadsheet analysis and data processing tools.

## 🔐 Authentication

### Personal Access Token
For individual use or small-scale analysis:
- Required permissions: `repo`, `read:org`, `read:user`

### GitHub App
For enterprise use and multi-organization analysis:
- Higher rate limits
- Better security
- Multi-organization support

See [docs/USAGE.md](docs/USAGE.md) for detailed authentication setup.

## 📖 Documentation

- **[Usage Guide](docs/USAGE.md)** - Comprehensive usage documentation
- **[Migration Guide](docs/MIGRATION.md)** - Migration from other tools
- **[Development Guide](docs/DEVELOPMENT.md)** - Contributing and development setup

## 🧪 Testing

Run the test suite:

```bash
cd tests
python test_github_org_stats.py
```

Run specific test categories:

```bash
python test_github_org_stats.py --category auth
python test_github_org_stats.py --category data
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Install development dependencies: `pip install -r requirements-dev.txt`
4. Make your changes
5. Run tests: `python -m pytest tests/`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check our comprehensive [usage guide](docs/USAGE.md)
- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/zoharbabin/github-org-stats/issues)
- **Discussions**: Join the conversation in [GitHub Discussions](https://github.com/zoharbabin/github-org-stats/discussions)

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=zoharbabin/github-org-stats&type=Date)](https://star-history.com/#zoharbabin/github-org-stats&Date)

## 🙏 Acknowledgments

- Thanks to all contributors who have helped improve this tool
- Built with [PyGithub](https://github.com/PyGithub/PyGithub) for GitHub API access
- Inspired by the need for comprehensive GitHub organization analysis

---

**Made with ❤️ by the open-source community**