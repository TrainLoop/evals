"""
Unit tests for the register module.
"""
import pytest
from trainloop_llm_logging import HEADER_NAME, trainloop_tag


class TestRegisterModule:
    """Test the public API functions."""
    
    @pytest.mark.unit
    def test_header_name_constant(self):
        """Test that HEADER_NAME is correctly defined."""
        assert HEADER_NAME == "X-Trainloop-Tag"
    
    @pytest.mark.unit
    def test_trainloop_tag_returns_dict(self):
        """Test that trainloop_tag returns a dictionary with the correct header."""
        tag = "test-tag"
        result = trainloop_tag(tag)
        
        assert isinstance(result, dict)
        assert HEADER_NAME in result
        assert result[HEADER_NAME] == tag
    
    @pytest.mark.unit
    def test_trainloop_tag_with_empty_string(self):
        """Test trainloop_tag with empty string."""
        result = trainloop_tag("")
        
        assert result == {HEADER_NAME: ""}
    
    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_trainloop_tag_with_special_characters(self):
        """Test trainloop_tag with special characters."""
        special_tag = "test-tag-αβγ-🚀-@#$%"
        result = trainloop_tag(special_tag)
        
        assert result[HEADER_NAME] == special_tag
    
    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_trainloop_tag_with_very_long_string(self):
        """Test trainloop_tag with very long string."""
        long_tag = "x" * 1000
        result = trainloop_tag(long_tag)
        
        assert result[HEADER_NAME] == long_tag
        assert len(result[HEADER_NAME]) == 1000
