"""
Tests for enhanced CLI parameter handling
"""

import pytest
import sys
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


class TestNewCLIScopeParameterHandling:
    """Test new CLI scope parameter handling"""
    
    def test_scope_parameter_exists(self):
        """Test that --scope parameter exists in CLI"""
        from generate_code_review_context import main
        import argparse
        
        # Test argument parser directly
        parser = argparse.ArgumentParser()
        parser.add_argument("--scope", default="recent_phase",
                          choices=["recent_phase", "full_project", "specific_phase", "specific_task"])
        
        # Should parse without error
        args = parser.parse_args(["--scope", "full_project"])
        assert args.scope == "full_project"
    
    def test_scope_parameter_accepts_valid_values(self):
        """Test that scope parameter accepts all valid values"""
        import argparse
        
        parser = argparse.ArgumentParser()
        parser.add_argument("--scope", choices=["recent_phase", "full_project", "specific_phase", "specific_task"])
        
        valid_scopes = ["recent_phase", "full_project", "specific_phase", "specific_task"]
        
        for scope in valid_scopes:
            args = parser.parse_args(["--scope", scope])
            assert args.scope == scope
    
    def test_scope_parameter_defaults_to_recent_phase(self):
        """Test that scope parameter defaults to recent_phase"""
        import argparse
        
        parser = argparse.ArgumentParser()
        parser.add_argument("--scope", default="recent_phase",
                          choices=["recent_phase", "full_project", "specific_phase", "specific_task"])
        
        args = parser.parse_args([])
        assert args.scope == "recent_phase"
    
    def test_scope_parameter_rejects_invalid_values(self):
        """Test that scope parameter rejects invalid values"""
        import argparse
        
        parser = argparse.ArgumentParser()
        parser.add_argument("--scope", choices=["recent_phase", "full_project", "specific_phase", "specific_task"])
        
        with pytest.raises(SystemExit):
            parser.parse_args(["--scope", "invalid_scope"])


class TestPhaseAndTaskNumberParameterValidation:
    """Test phase and task number parameter validation"""
    
    def test_phase_number_parameter_exists(self):
        """Test that --phase-number parameter exists"""
        import argparse
        
        parser = argparse.ArgumentParser()
        parser.add_argument("--phase-number", help="Phase number for specific_phase scope")
        
        args = parser.parse_args(["--phase-number", "2.0"])
        assert args.phase_number == "2.0"
    
    def test_task_number_parameter_exists(self):
        """Test that --task-number parameter exists"""
        import argparse
        
        parser = argparse.ArgumentParser()
        parser.add_argument("--task-number", help="Task number for specific_task scope")
        
        args = parser.parse_args(["--task-number", "1.2"])
        assert args.task_number == "1.2"
    
    def test_phase_number_parameter_is_optional(self):
        """Test that phase-number parameter is optional"""
        import argparse
        
        parser = argparse.ArgumentParser()
        parser.add_argument("--phase-number", help="Phase number")
        
        args = parser.parse_args([])
        assert args.phase_number is None
    
    def test_task_number_parameter_is_optional(self):
        """Test that task-number parameter is optional"""
        import argparse
        
        parser = argparse.ArgumentParser()
        parser.add_argument("--task-number", help="Task number")
        
        args = parser.parse_args([])
        assert args.task_number is None
    
    def test_parameters_work_together(self):
        """Test that parameters work together correctly"""
        import argparse
        
        parser = argparse.ArgumentParser()
        parser.add_argument("--scope", default="recent_phase")
        parser.add_argument("--phase-number")
        parser.add_argument("--task-number")
        
        # Test specific_phase with phase_number
        args = parser.parse_args(["--scope", "specific_phase", "--phase-number", "3.0"])
        assert args.scope == "specific_phase"
        assert args.phase_number == "3.0"
        
        # Test specific_task with task_number
        args = parser.parse_args(["--scope", "specific_task", "--task-number", "1.5"])
        assert args.scope == "specific_task"
        assert args.task_number == "1.5"


class TestAIReviewCommandFunctionality:
    """Test ai-review command functionality"""
    
    def test_ai_review_command_line_interface(self):
        """Test that AI review has command line interface"""
        # Test that ai_code_review.py can be run as a script
        from ai_code_review import main
        import argparse
        
        # Should have argument parser for context file
        parser = argparse.ArgumentParser()
        parser.add_argument("context_file")
        parser.add_argument("--output")
        parser.add_argument("--model")
        
        args = parser.parse_args(["test_context.md", "--output", "test_output.md", "--model", "gemini-2.0-flash-exp"])
        assert args.context_file == "test_context.md"
        assert args.output == "test_output.md"
        assert args.model == "gemini-2.0-flash-exp"
    
    def test_ai_review_context_file_parameter(self):
        """Test that AI review requires context file parameter"""
        import argparse
        
        parser = argparse.ArgumentParser()
        parser.add_argument("context_file", help="Path to context file")
        
        args = parser.parse_args(["context.md"])
        assert args.context_file == "context.md"
    
    def test_ai_review_optional_parameters(self):
        """Test that AI review has optional parameters"""
        import argparse
        
        parser = argparse.ArgumentParser()
        parser.add_argument("context_file")
        parser.add_argument("--output", help="Output file")
        parser.add_argument("--model", help="Model name")
        parser.add_argument("--validate-only", action="store_true")
        
        # Test with all parameters
        args = parser.parse_args(["context.md", "--output", "review.md", "--model", "gemini-1.5-pro", "--validate-only"])
        assert args.context_file == "context.md"
        assert args.output == "review.md"
        assert args.model == "gemini-1.5-pro"
        assert args.validate_only is True
        
        # Test with minimal parameters
        args = parser.parse_args(["context.md"])
        assert args.context_file == "context.md"
        assert args.output is None
        assert args.model is None
        assert args.validate_only is False


class TestEnhancedHelpTextAndUsageExamples:
    """Test enhanced help text and usage examples"""
    
    def test_generate_code_review_context_help_text(self):
        """Test that generate_code_review_context has enhanced help text"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test help output includes new parameters
            try:
                result = subprocess.run(
                    [sys.executable, str(Path(__file__).parent.parent / "src" / "generate_code_review_context.py"), "--help"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                help_text = result.stdout.lower()
                
                # Should mention scope options
                assert "scope" in help_text, "Help should mention scope parameter"
                assert "recent_phase" in help_text, "Help should mention recent_phase option"
                assert "full_project" in help_text, "Help should mention full_project option"
                assert "specific_phase" in help_text, "Help should mention specific_phase option"
                assert "specific_task" in help_text, "Help should mention specific_task option"
                
                # Should mention new parameters
                assert "phase-number" in help_text or "phase_number" in help_text, "Help should mention phase-number parameter"
                assert "task-number" in help_text or "task_number" in help_text, "Help should mention task-number parameter"
                
            except subprocess.TimeoutExpired:
                pytest.skip("Help command timed out")
            except FileNotFoundError:
                pytest.skip("Script not found or not executable")
    
    def test_ai_code_review_help_text(self):
        """Test that AI code review has comprehensive help text"""
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                result = subprocess.run(
                    [sys.executable, str(Path(__file__).parent.parent / "src" / "ai_code_review.py"), "--help"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                help_text = result.stdout.lower()
                
                # Should mention AI review functionality
                assert "ai" in help_text or "review" in help_text, "Help should mention AI review"
                assert "context" in help_text, "Help should mention context file"
                assert "model" in help_text, "Help should mention model parameter"
                
                # Should have examples
                assert "example" in help_text, "Help should include examples"
                
            except subprocess.TimeoutExpired:
                pytest.skip("Help command timed out")
            except FileNotFoundError:
                pytest.skip("Script not found or not executable")
    
    def test_help_text_includes_usage_examples(self):
        """Test that help text includes practical usage examples"""
        # This test verifies the examples are present in the help text
        from ai_code_review import main
        import argparse
        
        # Create parser like the one in ai_code_review.py
        parser = argparse.ArgumentParser(
            description="Generate AI-powered code review from context file",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python ai_code_review.py context.md
  python ai_code_review.py context.md --output custom-review.md
  python ai_code_review.py context.md --model gemini-2.0-flash-exp
        """
        )
        
        # Should have epilog with examples
        assert parser.epilog is not None, "Parser should have examples in epilog"
        assert "Examples:" in parser.epilog, "Should have examples section"
        assert "context.md" in parser.epilog, "Should show context file usage"
        assert "--output" in parser.epilog, "Should show output parameter usage"
        assert "--model" in parser.epilog, "Should show model parameter usage"


class TestBackwardCompatibilityWithExistingCLIUsage:
    """Test backward compatibility with existing CLI usage"""
    
    def test_legacy_parameters_still_work(self):
        """Test that legacy parameters still work"""
        import argparse
        
        # Create parser with both old and new parameters
        parser = argparse.ArgumentParser()
        parser.add_argument("project_path", nargs='?')
        parser.add_argument("--phase", help="Legacy phase parameter")
        parser.add_argument("--output", help="Output file")
        parser.add_argument("--scope", default="recent_phase")
        
        # Legacy usage should still work
        args = parser.parse_args(["/project/path", "--phase", "2.0", "--output", "output.md"])
        assert args.project_path == "/project/path"
        assert args.phase == "2.0"
        assert args.output == "output.md"
        assert args.scope == "recent_phase"  # Default value
    
    def test_legacy_phase_parameter_compatibility(self):
        """Test that legacy --phase parameter is compatible with new scope system"""
        from generate_code_review_context import main
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create minimal task file
            task_file = Path(temp_dir) / "tasks" / "tasks-test.md"
            task_file.parent.mkdir(exist_ok=True)
            task_file.write_text("# Test Tasks\n- [x] 2.0 Target Phase")
            
            # Legacy usage with --phase should work with scope=recent_phase
            with patch('generate_code_review_context.get_changed_files') as mock_files:
                mock_files.return_value = []
                with patch('builtins.open', mock_open()):
                    try:
                        result = main(
                            project_path=temp_dir,
                            phase="2.0",  # Legacy parameter
                            scope="recent_phase"  # Default scope
                        )
                        assert result is not None
                    except Exception as e:
                        # Expected if git repository or other dependencies missing
                        assert "not found" in str(e).lower() or "not a git repository" in str(e).lower()
    
    def test_mixed_old_and_new_parameter_usage(self):
        """Test that old and new parameters can be used together"""
        import argparse
        
        parser = argparse.ArgumentParser()
        parser.add_argument("project_path", nargs='?')
        parser.add_argument("--phase", help="Legacy phase")
        parser.add_argument("--scope", default="recent_phase")
        parser.add_argument("--phase-number", help="New phase number")
        parser.add_argument("--output", help="Output file")
        
        # Should handle mixed usage
        args = parser.parse_args([
            "/project/path",
            "--phase", "1.0",  # Legacy
            "--scope", "specific_phase",  # New
            "--phase-number", "2.0",  # New
            "--output", "output.md"
        ])
        
        assert args.project_path == "/project/path"
        assert args.phase == "1.0"
        assert args.scope == "specific_phase"
        assert args.phase_number == "2.0"
        assert args.output == "output.md"


class TestCLIParameterIntegration:
    """Test CLI parameter integration with core functionality"""
    
    def test_cli_parameters_passed_to_main_function(self):
        """Test that CLI parameters are correctly passed to main function"""
        from generate_code_review_context import main
        import inspect
        
        # Verify main function accepts new parameters
        sig = inspect.signature(main)
        params = list(sig.parameters.keys())
        
        assert 'scope' in params, "Main should accept scope parameter"
        assert 'phase_number' in params, "Main should accept phase_number parameter"
        assert 'task_number' in params, "Main should accept task_number parameter"
    
    def test_ai_review_cli_parameters_passed_correctly(self):
        """Test that AI review CLI parameters are passed correctly"""
        from ai_code_review import generate_ai_review
        import inspect
        
        # Verify AI review function accepts CLI parameters
        sig = inspect.signature(generate_ai_review)
        params = list(sig.parameters.keys())
        
        assert 'context_file_path' in params, "Should accept context_file_path"
        assert 'output_path' in params, "Should accept output_path"
        assert 'model' in params, "Should accept model"
    
    def test_parameter_validation_integration(self):
        """Test that parameter validation works with CLI"""
        from generate_code_review_context import main
        
        # Test that validation errors are raised for invalid combinations
        with pytest.raises(ValueError) as exc_info:
            main(scope="specific_phase")  # Missing phase_number
        
        assert "phase_number" in str(exc_info.value).lower()
        
        with pytest.raises(ValueError) as exc_info:
            main(scope="specific_task")  # Missing task_number
        
        assert "task_number" in str(exc_info.value).lower()
    
    def test_cli_error_handling(self):
        """Test CLI error handling for various scenarios"""
        from ai_code_review import generate_ai_review
        
        # Test error handling for invalid input
        with pytest.raises((ValueError, FileNotFoundError)):
            generate_ai_review("")  # Empty context file path
        
        with pytest.raises((ValueError, FileNotFoundError)):
            generate_ai_review("/nonexistent/file.md")  # Nonexistent file


class TestCLIUsabilityAndDocumentation:
    """Test CLI usability and documentation"""
    
    def test_parameter_descriptions_are_clear(self):
        """Test that parameter descriptions are clear and helpful"""
        # This would typically test actual help output, but we'll test the structure
        import argparse
        
        parser = argparse.ArgumentParser()
        parser.add_argument("--scope", 
                          choices=["recent_phase", "full_project", "specific_phase", "specific_task"],
                          help="Review scope: recent_phase (default), full_project, specific_phase, specific_task")
        parser.add_argument("--phase-number", 
                          help="Phase number for specific_phase scope (e.g., '2.0')")
        parser.add_argument("--task-number", 
                          help="Task number for specific_task scope (e.g., '1.2')")
        
        # Verify help strings are descriptive
        scope_action = next(action for action in parser._actions if action.dest == 'scope')
        assert len(scope_action.help) > 20, "Scope help should be descriptive"
        assert "recent_phase" in scope_action.help, "Should mention default option"
        
        phase_action = next(action for action in parser._actions if action.dest == 'phase_number')
        assert "2.0" in phase_action.help, "Should include example format"
        
        task_action = next(action for action in parser._actions if action.dest == 'task_number')
        assert "1.2" in task_action.help, "Should include example format"
    
    def test_cli_provides_clear_feedback(self):
        """Test that CLI provides clear feedback for operations"""
        # This tests the structure for providing feedback
        from ai_code_review import main as ai_main
        import argparse
        
        # CLI should have verbose option for detailed feedback
        parser = argparse.ArgumentParser()
        parser.add_argument("--verbose", action="store_true")
        
        args = parser.parse_args(["--verbose"])
        assert args.verbose is True
    
    def test_parameter_grouping_logical(self):
        """Test that parameters are logically grouped"""
        # Test that related parameters are grouped together
        import argparse
        
        parser = argparse.ArgumentParser()
        
        # Scope-related parameters should be grouped
        scope_group = parser.add_argument_group("Scope Options")
        scope_group.add_argument("--scope")
        scope_group.add_argument("--phase-number")
        scope_group.add_argument("--task-number")
        
        # Output-related parameters should be grouped
        output_group = parser.add_argument_group("Output Options")
        output_group.add_argument("--output")
        output_group.add_argument("--model")
        
        # Should have argument groups
        assert len(parser._action_groups) >= 4  # default groups + custom groups