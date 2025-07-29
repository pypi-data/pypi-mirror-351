# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub Actions CI/CD pipeline for automated testing and publishing
- Support for publishing to PyPI and TestPyPI
- Automated version management workflow
- Code quality checks with pylint, black, and mypy
- Security scanning with safety and bandit

## [1.0.0] - 2025-05-27

### Added
- Initial release of py-content-dedup
- Content deduplication and clustering functionality
- Support for multiple languages (Chinese, English, mixed content)
- Configurable field mapping system with three levels:
  - FieldMapping (standard 5 fields)
  - BalancedFieldMapping (4 fields)  
  - MinimalFieldMapping (3 fields)
- Command-line interface for easy usage
- Comprehensive test suite with 102 tests
- Support for various input formats (JSONL, JSON)
- Flexible similarity thresholds and clustering options

### Features
- **Core Functionality**:
  - Exact duplicate detection
  - Content similarity clustering
  - Language-aware text processing
  - Configurable similarity thresholds

- **Field Mapping System**:
  - Simplified field structure focusing on core deduplication
  - Single `id_field` replacing `url_field` and `original_url_field`
  - Backward compatibility with legacy parameter names
  - Support for custom field mappings

- **Language Support**:
  - Chinese text processing with jieba
  - English text processing with NLTK
  - Mixed-language content handling
  - Automatic language detection

- **CLI Interface**:
  - Simple command-line tool
  - Support for different output formats
  - Configurable mapping types
  - Progress reporting and detailed logging

- **Developer Experience**:
  - Comprehensive documentation
  - Rich examples and sample data
  - Extensive test coverage
  - Type hints and mypy support

### Technical Details
- Python 3.8+ support
- Optimized for performance with large datasets
- Memory-efficient processing
- Modular architecture for easy extension

## [Development Notes]

### Version 1.0.0 Optimization Process
This release represents a major optimization of the codebase:

1. **Field Structure Simplification**: Reduced from 9 fields to 5 core fields
2. **API Modernization**: Updated parameter names for better consistency  
3. **Documentation Improvement**: Simplified installation and usage guides
4. **Test Coverage**: Achieved 100% test pass rate (102/102 tests)
5. **Code Quality**: Improved maintainability and reduced complexity

### Migration from Pre-1.0 Versions
- `url_field` parameter → `id_field`
- Removed `author_field`, `images_field`, `fetch_time_field`
- CLI parameter `--url-field` → `--id-field`
- All changes maintain backward compatibility

---

## Release Process

### For Maintainers

1. **Version Bumping**:
   ```bash
   # Use GitHub Actions "Version Management" workflow
   # Or manually:
   bump2version patch  # or minor, major
   ```

2. **Testing Release**:
   ```bash
   # Publish to TestPyPI first
   python -m build
   twine upload --repository testpypi dist/*
   ```

3. **Production Release**:
   ```bash
   # Create and push tag
   git tag v1.0.1
   git push origin v1.0.1
   # GitHub Actions will automatically publish to PyPI
   ```

### For Users

Install the latest version:
```bash
pip install py-content-dedup
```

Install from TestPyPI (for testing):
```bash
pip install -i https://test.pypi.org/simple/ py-content-dedup
```
