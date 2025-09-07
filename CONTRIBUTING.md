# Contributing to Suricata ML-IDS

Thank you for your interest in contributing! This project welcomes contributions from developers, researchers, and security professionals.

## 🚀 Quick Start

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- Python 3.9+

### Development Setup
```bash
# Clone and setup
git clone https://github.com/your-username/suricata-ml-ids.git
cd suricata-ml-ids

# Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start development environment
./scripts/setup.sh
./scripts/demo.sh start
```

## 🛠️ Development Workflow

### Making Changes
1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes in `services/*/src/` directories
3. Rebuild services: `./scripts/dev-rebuild.sh <service-name>`
4. Test: `./scripts/demo.sh status`
5. Commit with conventional format: `feat:`, `fix:`, `docs:`

### Code Guidelines
- **Python**: Follow PEP 8
- **Documentation**: Update relevant docs
- **Testing**: Ensure health checks pass
- **Commits**: Use conventional commit messages

## 📝 Contribution Areas

### 🐛 Bug Fixes & Improvements
- Fix existing functionality issues
- Performance optimizations
- Better error handling

### ✨ New Features
- Additional ML algorithms (SVM, Neural Networks)
- Enhanced preprocessing tools
- New API endpoints
- Dashboard improvements

### 📚 Documentation
- Improve existing guides
- Add tutorials and examples
- Fix typos and clarity issues

## 🔍 Pull Request Process

1. Fork repository and create branch from `main`
2. Make changes following style guidelines
3. Update documentation if needed
4. Test thoroughly with demo scripts
5. Submit PR with clear description

### PR Checklist
- [ ] Code follows project standards
- [ ] All services pass health checks
- [ ] Documentation updated (if applicable)
- [ ] Changes tested with sample data

## 🤝 Community Guidelines

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Use GitHub issues for bugs and feature requests

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Ready to contribute?** Check out our [open issues](https://github.com/your-username/suricata-ml-ids/issues) to get started!