# Changelog

All notable changes to the README to Word Converter project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-05-27

### Added
- 🎉 **Initial Release**: Complete README to Word converter with Mermaid diagram support
- 📄 **Core Converter**: Full Markdown to Word document conversion
- 🎨 **Mermaid Integration**: Automatic diagram conversion using Mermaid.ink API
- 🖥️ **Streamlit Web Interface**: Professional UI with light/dark theme toggle
- 🐳 **Docker Support**: Complete containerization with production and development environments
- ☸️ **Kubernetes Deployment**: Comprehensive Helm charts for K8s deployment
- 🧪 **Testing Suite**: Comprehensive test coverage for all components
- 📚 **Documentation**: Complete setup and usage documentation
- 🔧 **CLI Interface**: Command-line tool for batch processing
- 📦 **PyPI Package**: Installable Python package with entry points

### Features
- **Document Conversion**:
  - Markdown to Word (.docx) conversion
  - Table of contents generation
  - Professional styling and formatting
  - Code block syntax highlighting
  - Table structure preservation
  - Image embedding support

- **Mermaid Diagram Support**:
  - Flowcharts, sequence diagrams, class diagrams
  - Multiple themes (default, neutral, dark, forest)
  - High-quality PNG generation
  - Automatic embedding in Word documents
  - Error handling and fallback support

- **Web Interface**:
  - Drag & drop file upload
  - Real-time preview
  - Theme switching (light/dark)
  - Progress tracking
  - Download management
  - Responsive design

- **Command Line Interface**:
  - Batch file processing
  - Multiple output formats
  - Debug mode support
  - Theme selection
  - Custom output naming

- **Deployment Options**:
  - Local Python installation
  - Docker containers
  - Kubernetes clusters
  - Cloud deployment ready

- **Development Tools**:
  - Comprehensive test suite
  - Docker development environment
  - Kubernetes local deployment
  - CI/CD ready configuration

### Technical Details
- **Python 3.8+** compatibility
- **Dependencies**: Streamlit, python-docx, markdown, beautifulsoup4, requests, Pillow
- **Architecture**: Modular design with separate CLI and web interfaces
- **Testing**: Unit tests, integration tests, and end-to-end testing
- **Documentation**: Complete API documentation and user guides
- **Packaging**: Modern Python packaging with pyproject.toml

### Installation
```bash
# Install from PyPI
pip install readme2word

# Install with all extras
pip install readme2word[all]

# Install for development
pip install readme2word[dev]
```

### Usage
```bash
# Command line
readme2word README.md

# Web interface
readme2word --web

# Docker
docker run -p 8501:8501 readme2word

# Kubernetes
helm install readme2word ./infra/helm/readme2word
```

### Contributors
- **Vishal Mishra** - Initial development and architecture
- **Zain Quraishi** - Inspiration for the original idea

### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## [Unreleased]

### Planned Features
- [ ] **Enhanced Themes**: Additional Mermaid diagram themes
- [ ] **Export Formats**: PDF and HTML export options
- [ ] **Plugin System**: Extensible converter plugins
- [ ] **Cloud Storage**: Direct integration with cloud storage providers
- [ ] **Collaboration**: Multi-user editing and sharing features
- [ ] **API Service**: REST API for programmatic access
- [ ] **Performance**: Optimization for large documents
- [ ] **Internationalization**: Multi-language support

### Known Issues
- Large documents with many diagrams may take longer to process
- Some complex Markdown features may require manual adjustment in Word
- Network connectivity required for Mermaid diagram conversion

### Contributing
We welcome contributions! Please see our [Contributing Guide](README.md#contributing) for details.

### Support
- 📋 [Issues](https://github.com/vishalm/readme2readall/issues)
- 💬 [Discussions](https://github.com/vishalm/readme2readall/discussions)
- 📖 [Documentation](https://github.com/vishalm/readme2readall#readme) 