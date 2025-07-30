"""
Tests for the dynamicwf package.
"""

import unittest
import sys
from pathlib import Path

# Add the src directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dynamicwf import __version__


class TestDynamicWF(unittest.TestCase):
    """Tests for the dynamicwf package."""

    def test_version(self):
        """Test the version is a string."""
        self.assertIsInstance(__version__, str)
        self.assertGreater(len(__version__), 0)


if __name__ == "__main__":
    unittest.main()
