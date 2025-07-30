# SnapLogic Common Robot Framework Library

A comprehensive Robot Framework library providing keywords for SnapLogic platform automation and testing.

## 🚀 Features

- **SnapLogic APIs**: Low-level API keywords for direct platform interaction
- **SnapLogic Keywords**: High-level business keywords for common operations  
- **Common Utilities**: Shared utilities for database connections and file operations
- **Comprehensive Documentation**: HTML documentation with navigation and examples



```bash
pip install snaplogic-common-robot
```

## 🔧 Quick Start

```robot
*** Settings ***
Resource    snaplogic_apis_keywords/snaplogic_apis.resource
Resource    snaplogic_apis_keywords/snaplogic_keywords.resource  
Resource    snaplogic_apis_keywords/common_utilities.resource


## 📚 Documentation

After installation, access the comprehensive HTML documentation:

```python
import pkg_resources
import webbrowser

# Locate and open documentation
docs_path = pkg_resources.resource_filename(
    'snaplogic_common_robot', 'libdocs/index.html'
)
webbrowser.open(f'file://{docs_path}')
```

## 🔑 Available Keywords

### SnapLogic APIs
- Pipeline management and execution
- Task monitoring and control
- Data operations and validation

### SnapLogic Keywords  
- High-level business operations
- Pre-built test scenarios
- Error handling and reporting

### Common Utilities
- **Connect to Oracle Database**: Sets up database connections using environment variables
- File operations and data handling
- Environment setup and configuration

## 🛠️ Requirements

- Python 3.12+
- Robot Framework
- Database connectivity libraries
- HTTP request libraries

## 🏗️ Development

```bash
# Clone the repository
git clone <repository-url>

# Install development dependencies
pip install -r src/requirements.txt

```


## 🏢 About SnapLogic

This library is designed for testing and automation of SnapLogic integration platform operations.
