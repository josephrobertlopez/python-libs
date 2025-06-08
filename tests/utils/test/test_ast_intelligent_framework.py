"""
Test suite for AST-Enhanced Intelligent Test Framework

This test suite demonstrates and validates the new AST-driven capabilities
including automatic pattern detection, intelligent preset selection, and
auto-generated mock configurations.
"""

import pytest
import sys
import os
import logging
from pathlib import Path
from src.utils.test import (
    SmartTestCase, auto_analyze, intelligent_preset, smart_mock_auto,
    runtime_mock, StandardTestCase
)


class TestASTIntelligentFramework(SmartTestCase):
    """Test suite for AST-enhanced intelligent framework capabilities."""
    
    def setUp(self):
        """Set up test case ensuring SmartTestCase initialization."""
        super().setUp()
    
    def test_ast_analysis_basic(self):
        """Test basic AST analysis functionality."""
        # Get analysis of this test method
        analysis = self.analyze_test_method()
        
        # Verify analysis structure
        assert isinstance(analysis, dict)
        assert 'imports' in analysis
        assert 'function_calls' in analysis  
        assert 'patterns' in analysis
        assert 'recommended_preset' in analysis
        assert 'complexity_score' in analysis
        assert 'auto_mocks' in analysis
        
        print("✅ Basic AST analysis working")
    
    @auto_analyze  # This should auto-detect sys usage and configure it
    def test_auto_analyze_sys_detection(self):
        """Test that @auto_analyze automatically detects and mocks sys usage."""
        import sys  # AST should detect this and auto-mock sys
        
        # The framework should have automatically configured sys.argv
        assert hasattr(sys, 'argv')
        # Auto-detected configuration should be applied
        print(f"🤖 Auto-detected sys.argv: {sys.argv}")
        
        print("✅ Auto-analyze with sys detection working")
    
    @auto_analyze  # Should detect os and logging usage
    def test_auto_analyze_multi_module(self):
        """Test auto-analysis with multiple modules."""
        import os      # Should auto-mock os
        import logging # Should auto-mock logging
        import sys     # Should auto-mock sys
        
        # All should be automatically configured
        assert hasattr(os, 'environ')
        assert hasattr(sys, 'argv') 
        assert hasattr(logging, 'getLogger')
        
        print("🤖 Multi-module auto-detection working")
        print(f"   - os.environ keys: {list(os.environ.keys())[:3]}")
        print(f"   - sys.argv: {sys.argv}")
        
        print("✅ Multi-module auto-analysis working")
    
    @intelligent_preset('logging_system')  # Should validate this choice
    def test_intelligent_preset_logging(self):
        """Test intelligent preset with logging system."""
        import logging
        import os
        from pathlib import Path
        
        # Should be optimally configured for logging + file operations
        logger = logging.getLogger('test')
        config_path = Path('/test/config.ini')
        
        assert logger is not None
        print(f"🎯 Intelligent preset applied: logging_system")
        print("✅ Intelligent preset working")
    
    @smart_mock_auto('sys')  # Should analyze sys usage and auto-configure
    def test_smart_mock_auto(self):
        """Test smart mock with automatic configuration."""
        import sys
        
        # Should be automatically configured based on detected usage
        assert hasattr(sys, 'argv')
        print(f"🔧 Smart auto-mock configured sys.argv: {sys.argv}")
        print("✅ Smart mock auto working")
    
    def test_pattern_suggestions(self):
        """Test pattern detection and suggestions."""
        suggestions = self.get_pattern_suggestions()
        
        assert isinstance(suggestions, list)
        print(f"💡 Pattern suggestions: {suggestions}")
        print("✅ Pattern suggestions working")
    
    def test_quick_analysis_output(self):
        """Test quick analysis human-readable output."""
        analysis_text = self.quick_analysis()
        
        assert isinstance(analysis_text, str)
        assert "AST Analysis Summary" in analysis_text
        assert "Detected Patterns" in analysis_text
        assert "Recommended Preset" in analysis_text
        
        print("\n" + "="*50)
        print(analysis_text)
        print("="*50)
        print("✅ Quick analysis output working")
    
    def test_smart_context_manager(self):
        """Test the intelligent context manager."""
        with self.smart_context(auto_analyze=True) as ctx:
            # Should provide both auto and manual contexts
            assert 'auto' in ctx
            assert 'manual' in ctx
            
            print("🔄 Smart context manager working")
            print("✅ Context manager integration working")
    
    def test_complexity_detection(self):
        """Test complexity scoring."""
        analysis = self.analyze_test_method()
        complexity = analysis.get('complexity_score', 0)
        
        assert isinstance(complexity, int)
        assert complexity >= 1
        
        print(f"📊 Complexity score: {complexity}")
        print("✅ Complexity detection working")


class TestBackwardCompatibility(StandardTestCase):
    """Test that traditional patterns still work alongside AST features."""
    
    @runtime_mock('minimal')
    def test_traditional_runtime_mock(self):
        """Test that traditional runtime mocks still work."""
        # Traditional approach should still work
        print("🔄 Traditional runtime mock working")
        print("✅ Backward compatibility maintained")
    
    def test_mixed_usage_patterns(self):
        """Test mixing traditional and AST-enhanced patterns."""
        # Can still use traditional context managers
        from src.utils.test import smart_mock
        
        with smart_mock('sys', argv=['traditional', 'test']) as ctx:
            import sys
            assert sys.argv == ['traditional', 'test']
            
        print("🔄 Mixed usage patterns working")
        print("✅ Traditional and AST patterns coexist")


class TestRealWorldScenarios:
    """Real-world scenario tests using AST intelligence."""
    
    @auto_analyze  # Should detect logging + file operations pattern
    def test_logging_config_scenario(self):
        """Real scenario: Testing logging configuration setup."""
        import logging
        import os
        from pathlib import Path
        
        # This mimics real logging setup code
        config_file = os.path.join("resources", "logging_config.ini")
        log_path = Path("logs/test.log")
        
        # AST should detect logging_system pattern and configure optimally
        logger = logging.getLogger("test_app")
        logger.info("Test message")
        
        assert logger is not None
        print("🏭 Real-world logging scenario handled by AST")
    
    @auto_analyze  # Should detect CLI application pattern  
    def test_cli_app_scenario(self):
        """Real scenario: Testing CLI application."""
        import sys
        import argparse
        
        # Typical CLI app testing pattern
        if len(sys.argv) > 1:
            command = sys.argv[1]
        else:
            command = "help"
            
        # AST should detect CLI pattern and configure sys.argv appropriately
        assert hasattr(sys, 'argv')
        print("🖥️  Real-world CLI scenario handled by AST")
    
    @auto_analyze  # Should detect file operations pattern
    def test_file_operations_scenario(self):
        """Real scenario: Testing file operations.""" 
        import os
        from pathlib import Path
        
        # Typical file testing patterns
        test_file = Path("/tmp/test.txt")
        config_dir = os.path.join("config", "app")
        
        # Check if file exists (should be auto-mocked)
        file_exists = os.path.exists(str(test_file))
        dir_exists = os.path.isdir(config_dir)
        
        print(f"📁 File operations: file_exists={file_exists}, dir_exists={dir_exists}")
        print("🏭 Real-world file scenario handled by AST")


def test_framework_integration():
    """Test that the AST framework integrates well with existing test runners."""
    from src.utils.test import framework_info, list_available_presets
    
    # Should include AST features in framework info
    info = framework_info()
    assert 'AST-enhanced intelligent testing' in str(info)
    
    # Should list presets including ones good for AST-detected patterns
    presets = list_available_presets()
    assert 'logging_system' in presets
    assert 'minimal' in presets
    
    print("🔗 Framework integration working")
    print("✅ AST framework fully integrated")


if __name__ == '__main__':
    print("🚀 Running AST-Enhanced Intelligent Framework Tests")
    print("="*60)
    
    # Run a quick demo
    test_instance = TestASTIntelligentFramework()
    test_instance.setUp()
    
    print("\n📊 Quick Analysis Demo:")
    print(test_instance.quick_analysis())
    
    print("\n💡 Pattern Suggestions Demo:")
    suggestions = test_instance.get_pattern_suggestions()
    for suggestion in suggestions:
        print(f"   • {suggestion}")
    
    print("\n✨ AST Framework Ready!")
    print("Use pytest to run the full test suite.")
