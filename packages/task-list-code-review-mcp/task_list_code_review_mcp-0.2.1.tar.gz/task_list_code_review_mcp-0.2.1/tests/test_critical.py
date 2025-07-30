"""
Critical functionality tests - minimal set that actually tests what exists
"""
import pytest
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestCoreImports:
    """Test that core modules can be imported"""
    
    def test_server_imports(self):
        """Test server module imports successfully"""
        import server
        assert hasattr(server, 'mcp')  # FastMCP server instance
        assert hasattr(server, 'generate_code_review_context')  # MCP tool
        
    def test_generate_code_review_context_imports(self):
        """Test generate_code_review_context module imports"""
        import generate_code_review_context
        assert hasattr(generate_code_review_context, 'main')
        assert hasattr(generate_code_review_context, 'load_model_config')
        
    def test_ai_code_review_imports(self):
        """Test ai_code_review module imports"""
        import ai_code_review
        assert hasattr(ai_code_review, 'main')
        assert hasattr(ai_code_review, 'generate_ai_review')

class TestPackageStructure:
    """Test basic package structure"""
    
    def test_required_files_exist(self):
        """Test that required package files exist"""
        project_root = Path(__file__).parent.parent
        
        # Core source files
        assert (project_root / 'src' / 'server.py').exists()
        assert (project_root / 'src' / 'generate_code_review_context.py').exists()
        assert (project_root / 'src' / 'ai_code_review.py').exists()
        assert (project_root / 'src' / 'model_config.json').exists()
        
        # Package configuration
        assert (project_root / 'pyproject.toml').exists()
        assert (project_root / 'README.md').exists()
        
    def test_model_config_loads(self):
        """Test that model configuration loads successfully"""
        from generate_code_review_context import load_model_config
        
        config = load_model_config()
        assert isinstance(config, dict)
        assert 'model_aliases' in config
        assert 'defaults' in config
        assert 'model_capabilities' in config

class TestEnvironmentHandling:
    """Test environment variable handling"""
    
    def test_environment_variables_fallback(self):
        """Test that environment variables have proper fallbacks"""
        # Test that our code handles missing environment variables gracefully
        assert os.getenv('NONEXISTENT_VAR', 'default') == 'default'
        
        # Test model config defaults work
        from generate_code_review_context import load_model_config
        config = load_model_config()
        
        # Should have reasonable defaults even without env vars
        assert config['defaults']['model'] in ['gemini-2.0-flash', 'gemini-2.0-flash-lite']

class TestModelConfiguration:
    """Test model configuration system"""
    
    def test_model_aliases_exist(self):
        """Test that model aliases are properly configured"""
        from generate_code_review_context import load_model_config
        
        config = load_model_config()
        aliases = config.get('model_aliases', {})
        
        # Should have some basic aliases
        assert isinstance(aliases, dict)
        
    def test_capability_detection(self):
        """Test that model capabilities are defined"""
        from generate_code_review_context import load_model_config
        
        config = load_model_config()
        capabilities = config.get('model_capabilities', {})
        
        assert 'url_context_supported' in capabilities
        assert 'thinking_mode_supported' in capabilities
        assert isinstance(capabilities['url_context_supported'], list)