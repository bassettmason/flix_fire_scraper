from api.scraper.scraper import trial_function

import pytest

# Test the test_function from scraper.py

def test_trial_function():
    assert trial_function(1, 2) == 3
    assert trial_function(-1, -2) == -3
    assert trial_function(0, 0) == 0
    # More tests can be added, including edge
