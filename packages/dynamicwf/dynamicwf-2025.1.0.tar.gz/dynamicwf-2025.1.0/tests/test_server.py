import pytest
from dynamicwf.server import get_adobe_interns, filter_adobe_interns

def test_get_adobe_interns():
    """Test that get_adobe_interns returns a list of interns."""
    interns = get_adobe_interns()
    assert isinstance(interns, list)
    assert len(interns) > 0
    assert all(isinstance(intern, str) for intern in interns)

def test_filter_adobe_interns():
    """Test that filter_adobe_interns filters the list of interns correctly."""
    # Test with no filter
    interns = filter_adobe_interns()
    assert isinstance(interns, list)
    assert len(interns) > 0
    
    # Test with a filter that should match something
    filtered_interns = filter_adobe_interns(name_contains="a")
    assert isinstance(filtered_interns, list)
    assert all("a" in intern.lower() or "A" in intern for intern in filtered_interns)
    
    # Test with a filter that should match nothing
    filtered_interns = filter_adobe_interns(name_contains="xyz123")
    assert isinstance(filtered_interns, list)
    assert len(filtered_interns) == 0
