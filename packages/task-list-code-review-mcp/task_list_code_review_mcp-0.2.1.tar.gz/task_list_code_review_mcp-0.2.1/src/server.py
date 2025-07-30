"""
FastMCP server for generating code review context from PRDs and git changes
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

try:
    from fastmcp import FastMCP
    from generate_code_review_context import main as generate_review_context
    from ai_code_review import generate_ai_review
except ImportError as e:
    print(f"Required dependencies not available: {e}", file=sys.stderr)
    sys.exit(1)

# Create FastMCP server with ERROR log level to avoid info noise
mcp = FastMCP("MCP Server - Code Review Context Generator")


@mcp.tool()
def generate_code_review_context(
    project_path: str,
    scope: str = "recent_phase",
    phase_number: Optional[str] = None,
    task_number: Optional[str] = None,
    current_phase: Optional[str] = None,
    output_path: Optional[str] = None,
    enable_gemini_review: bool = True,
    temperature: float = 0.5
) -> str:
    """Generate code review context with flexible scope options.
    
    Args:
        project_path: Absolute path to project root directory
        scope: Review scope - 'recent_phase' (default), 'full_project', 'specific_phase', 'specific_task'
        phase_number: Phase number for specific_phase scope (e.g., '2.0')
        task_number: Task number for specific_task scope (e.g., '1.2')
        current_phase: Legacy phase override (e.g., '2.0'). If not provided, auto-detects from task list
        output_path: Custom output file path. If not provided, uses default timestamped path
        enable_gemini_review: Enable Gemini AI code review generation (default: true)
        temperature: Temperature for AI model (default: 0.5, range: 0.0-2.0)
    
    Returns:
        Success message with generated content and output file path
    """
    
    # Comprehensive error handling to prevent TaskGroup issues
    try:
        # Validate project_path
        if not project_path:
            return "ERROR: project_path is required"
        
        if not os.path.isabs(project_path):
            return "ERROR: project_path must be an absolute path"
        
        if not os.path.exists(project_path):
            return f"ERROR: Project path does not exist: {project_path}"
        
        if not os.path.isdir(project_path):
            return f"ERROR: Project path must be a directory: {project_path}"
        
        # Handle temperature: MCP parameter takes precedence, then env var, then default 0.5
        if temperature == 0.5:  # Default value, check if env var should override
            temperature = float(os.getenv('GEMINI_TEMPERATURE', '0.5'))
        
        # Generate review context using enhanced logic
        try:
            output_file = generate_review_context(
                project_path=project_path,
                phase=current_phase,  # Legacy parameter
                output=output_path,
                enable_gemini_review=enable_gemini_review,
                scope=scope,
                phase_number=phase_number,
                task_number=task_number,
                temperature=temperature
            )
            
            # Read the generated content to return
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                content = f"Generated file at: {output_file} (could not read content: {e})"
            
            return f"Successfully generated code review context.\n\nOutput file: {output_file}\n\nContent:\n{content[:2000]}{'...' if len(content) > 2000 else ''}"
            
        except Exception as e:
            return f"ERROR: Error generating code review context: {str(e)}"
            
    except Exception as e:
        # Catch-all to ensure no exceptions escape the tool function
        return f"ERROR: Unexpected error: {str(e)}"


@mcp.tool()
def generate_ai_code_review(
    context_file_path: str,
    output_path: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.5
) -> str:
    """Generate AI-powered code review from existing context file.
    
    Args:
        context_file_path: Path to existing code review context file (.md)
        output_path: Custom output file path for AI review. If not provided, uses default timestamped path
        model: Optional Gemini model name (e.g., 'gemini-2.0-flash-exp', 'gemini-1.5-pro')
        temperature: Temperature for AI model (default: 0.5, range: 0.0-2.0)
    
    Returns:
        Success message with generated AI review content and output file path
    """
    
    # Comprehensive error handling
    try:
        # Validate context_file_path
        if not context_file_path:
            return "ERROR: context_file_path is required"
        
        if not os.path.isabs(context_file_path):
            return "ERROR: context_file_path must be an absolute path"
        
        if not os.path.exists(context_file_path):
            return f"ERROR: Context file does not exist: {context_file_path}"
        
        if not os.path.isfile(context_file_path):
            return f"ERROR: Context file path must be a file: {context_file_path}"
        
        # Handle temperature: MCP parameter takes precedence, then env var, then default 0.5
        if temperature == 0.5:  # Default value, check if env var should override
            temperature = float(os.getenv('GEMINI_TEMPERATURE', '0.5'))
        
        # Generate AI review using standalone tool
        try:
            output_file = generate_ai_review(
                context_file_path=context_file_path,
                output_path=output_path,
                model=model,
                temperature=temperature
            )
            
            if output_file:
                # Read the generated content to return
                try:
                    with open(output_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    return f"Successfully generated AI code review: {output_file}\n\n{content}"
                    
                except Exception as e:
                    return f"AI review generated at {output_file}, but could not read content: {str(e)}"
            else:
                return "ERROR: AI review generation failed - no output file created"
            
        except Exception as e:
            return f"ERROR: Error generating AI code review: {str(e)}"
            
    except Exception as e:
        # Catch-all to ensure no exceptions escape the tool function
        return f"ERROR: Unexpected error: {str(e)}"


def main():
    """Entry point for uvx execution"""
    # FastMCP handles all the server setup, protocol, and routing
    # Use stdio transport explicitly (more reliable than SSE/streamable-http)
    mcp.run(transport="stdio", log_level="ERROR")


if __name__ == "__main__":
    main()