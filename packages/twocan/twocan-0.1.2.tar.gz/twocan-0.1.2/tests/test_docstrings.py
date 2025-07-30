"""
Pytest tests for docstring examples.

This module contains tests that verify all docstring examples
work correctly using pytest's doctest integration.
"""

import pytest
import doctest
import twocan
import twocan.base
import twocan.utils
import twocan.optimize
import twocan.callbacks
import twocan.plotting


class TestDocstrings:
    """Test class for all docstring examples."""

    def test_main_module_docstrings(self):
        """Test examples in the main twocan module."""
        doctest.testmod(twocan, raise_on_error=True)

    def test_base_module_docstrings(self):
        """Test examples in twocan.base module."""
        doctest.testmod(twocan.base, raise_on_error=True)

    def test_utils_module_docstrings(self):
        """Test examples in twocan.utils module."""
        doctest.testmod(twocan.utils, raise_on_error=True)

    def test_optimize_module_docstrings(self):
        """Test examples in twocan.optimize module."""
        doctest.testmod(twocan.optimize, raise_on_error=True)

    def test_callbacks_module_docstrings(self):
        """Test examples in twocan.callbacks module."""
        doctest.testmod(twocan.callbacks, raise_on_error=True)

    def test_plotting_module_docstrings(self):
        """Test examples in twocan.plotting module."""
        doctest.testmod(twocan.plotting, raise_on_error=True)


# Alternative: Test specific functions individually for better error reporting
@pytest.mark.parametrize("obj", [
    twocan.RegEstimator,
    twocan.IFProcessor,
    twocan.IMCProcessor,
    twocan.multi_channel_corr,
    twocan.registration_trial,
    twocan.iou_corr_single_objective,
    twocan.iou_corr_multi_objective,
])
def test_individual_docstrings(obj):
    """Test docstrings of individual functions/classes."""
    doctest.run_docstring_examples(obj, globals(), verbose=True) 