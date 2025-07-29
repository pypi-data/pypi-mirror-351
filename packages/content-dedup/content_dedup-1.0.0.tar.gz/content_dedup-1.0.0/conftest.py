"""
Global pytest configuration
"""

import pytest
import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging for tests
logging.basicConfig(level=logging.WARNING)

# Disable specific loggers during testing
logging.getLogger('content_dedup').setLevel(logging.ERROR)


def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "cli: mark test as CLI test")


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    for item in items:
        # Mark CLI tests
        if "cli" in item.nodeid:
            item.add_marker(pytest.mark.cli)
        
        # Mark integration tests
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
