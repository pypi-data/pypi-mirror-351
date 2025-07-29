"""
TestIndex test-suggest command.

This module implements the `testindex test-suggest` command that generates test suggestions
for implementation nodes.
"""

import os
import sys
import traceback
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from testindex.core.cli.runner import common_options
from testindex.core.logging import get_logger
from testindex.core.path_resolution import PathResolver
from testindex.cli.utils.env_check import needs_env

# Set up logger
logger = get_logger(__name__)

# Create rich console
console = Console()


@click.command('test-suggest', help='Generate test suggestions for functions')
@click.argument('target', type=str, required=True)
@click.option('--k', type=int, default=5,
              help='Maximum number of suggestions to generate (default: 5)')
@click.option('--yaml', 'yaml_output', type=click.Path(),
              help='Path to write YAML output')
@click.option('--json', 'json_output', type=click.Path(),
              help='Path to write JSON output')
@click.option('--llm', is_flag=True,
              help='Use LLM fallback if heuristics fail')
@click.option('--model', type=str, default="gpt-4o",
              help='LLM model to use (default: gpt-4o)')
@click.option('--budget', type=float, default=0.03,
              help='Maximum cost per suggestion in dollars (default: 0.03)')
@click.option('--prompt', '-p', is_flag=True,
              help='Generate rich context for developers/AI agents to write tests instead of direct test suggestions')
@click.option('--debug', is_flag=True, help='Enable detailed debugging output')
@click.option('--no-env-check', is_flag=True, help='Skip environment dependency check')
@common_options
@needs_env('test-suggest')
def test_suggest_command(
    target: str,
    k: int,
    yaml_output: Optional[str],
    json_output: Optional[str],
    llm: bool,
    model: str,
    budget: float,
    prompt: bool,
    debug: bool,
    verbose: bool,
    no_env_check: bool,
    **kwargs
):
    """Generate test suggestions for implementation nodes.
    
    Args:
        target: Path to file or fully-qualified node name
        k: Maximum number of suggestions to generate
        yaml_output: Path to write YAML output
        json_output: Path to write JSON output
        llm: Use LLM fallback if heuristics fail
        model: LLM model to use
        budget: Maximum cost per suggestion in dollars
        prompt: Generate rich context for developers/AI agents
        debug: Enable detailed debugging output
        verbose: Show verbose output
        no_env_check: Skip environment dependency check
    """
    try:
        # Set debug mode if requested
        if debug:
            import logging
            logging.getLogger("testindex").setLevel(logging.DEBUG)
            logger.debug("Debug mode enabled")
        
        # Import the test suggestion engine
        from testindex.analysis.test_suggest import TestSuggestionEngine
        
        # Get the repository root
        repo_root = PathResolver.repo_root()
        cwd = Path.cwd()
        
        # Check if target exists or resolve common target patterns
        target_exists = os.path.exists(target)
        if not target_exists and '/' not in target and '::' not in target:
            # Try various paths for the target
            possible_paths = [
                target,
                os.path.join('src', target),
                os.path.join('testindex', target),
                os.path.join('django', target),
            ]
            
            # Also try repo-root based paths
            possible_paths.extend([
                os.path.join(repo_root, target),
                os.path.join(repo_root, 'src', target),
                os.path.join(repo_root, 'testindex', target),
                os.path.join(repo_root, 'django', target),
            ])
            
            found = False
            for path in possible_paths:
                if os.path.exists(path):
                    target = path
                    found = True
                    if debug:
                        logger.debug(f"Resolved target to '{path}'")
                    break
                    
            if not found:
                if debug:
                    logger.debug(f"Target '{target}' not found in any of these paths: {possible_paths}")
                console.print(f"[yellow]Warning:[/yellow] Target '{target}' does not exist as a file. " +
                              "Treating as a node name.")
        elif debug and target_exists:
            logger.debug(f"Target '{target}' exists as a file")
        
        # Check if repo has django subdirectory
        django_dir = cwd / "django"
        has_django_dir = django_dir.exists() and django_dir.is_dir()
        if has_django_dir and debug:
            logger.debug(f"Found Django directory at {django_dir}")
            
            # Special case for django paths
            if target.startswith("django/") and not os.path.exists(target):
                alt_target = target.replace("django/", "")
                django_relative_path = django_dir / alt_target
                if django_relative_path.exists():
                    target = str(django_relative_path)
                    if debug:
                        logger.debug(f"Resolved Django-relative path to {target}")
        
        # Initialize the engine
        console.print(f"Generating test suggestions for [bold]{target}[/bold]...")
        if llm and not prompt:
            # Check if the OpenAI API key is set
            if not os.environ.get("OPENAI_API_KEY"):
                console.print("[red]Error:[/red] OPENAI_API_KEY environment variable not set.")
                console.print("Set it or use without --llm flag.")
                sys.exit(2)
                
            console.print(f"Using LLM fallback with model [bold]{model}[/bold] (budget: ${budget})...")
        
        if prompt:
            console.print("[bold blue]Generating test context in prompt mode[/bold blue]")
            
        engine = TestSuggestionEngine(llm_enabled=llm, model=model, budget=budget)
        
        # Generate suggestions
        output_file = None
        if json_output:
            output_file = json_output
        
        suggestions = engine.generate_suggestions(
            target=target,
            k=k,
            output_file=output_file
        )
        
        if not suggestions:
            console.print("[yellow]No test suggestions generated.[/yellow] " +
                          "This could be due to:")
            console.print("• No matching nodes found in the knowledge graph")
            console.print("• No function parameters to generate tests for")
            console.print("• Source file not found or parse error")
            
            if not llm and not prompt:
                console.print("\nTry using [bold]--llm[/bold] flag for more advanced suggestions.")
            
            sys.exit(1)
        
        # In prompt mode, generate rich context instead of test suggestions
        if prompt:
            # Get the target node info
            target_nodes = engine._identify_target_nodes(target, os.path.exists(target))
            if target_nodes:
                target_node = target_nodes[0]
                target_file = target_node.get("file_path", "")
                target_name = target_node.get("name", "")
                
                # Get source code
                source_code = ""
                try:
                    source_path = engine._find_source_file(target_file)
                    if source_path:
                        with open(source_path, 'r', encoding='utf-8') as f:
                            source_code = f.read()
                except Exception as e:
                    logger.warning(f"Failed to read source file: {e}")
                
                # Generate rich context for the developer or AI agent
                console.print("\n[bold green]RICH TEST CONTEXT[/bold green]")
                
                # Metadata section
                console.print("[bold]TARGET METADATA[/bold]")
                console.print(f"File: {target_file}")
                console.print(f"Function: {target_name}")
                if "properties" in target_node:
                    properties = target_node.get("properties", {})
                    console.print(f"Type: {target_node.get('type', 'Unknown')}")
                    console.print(f"Lines: {properties.get('line_start', '?')}-{properties.get('line_end', '?')}")
                    console.print(f"Coverage: {properties.get('coverage', '?')}%")
                    
                    if isinstance(properties, dict) and "complexity" in properties:
                        console.print(f"Complexity: {properties.get('complexity', '?')}")
                
                # Source code section
                if source_code:
                    console.print("\n[bold]SOURCE CODE[/bold]")
                    syntax = Syntax(source_code, "python", theme="monokai", line_numbers=True)
                    console.print(syntax)
                
                # Dependencies section
                console.print("\n[bold]DEPENDENCIES[/bold]")
                dependencies = engine._extract_dependencies(target_node)
                if dependencies:
                    console.print("This function depends on:")
                    for dep in dependencies:
                        console.print(f"- {dep}")
                else:
                    console.print("No dependencies detected")
                
                # Parameter section
                console.print("\n[bold]PARAMETERS[/bold]")
                params, type_hints = engine._extract_params_from_node(target_node, source_code)
                if params:
                    for param in params:
                        hint = type_hints.get(param, "unknown")
                        console.print(f"- {param}: {hint}")
                else:
                    console.print("No parameters detected")
                
                # Test patterns section
                console.print("\n[bold]RECOMMENDED TEST PATTERNS[/bold]")
                for i, suggestion in enumerate(suggestions, 1):
                    console.print(f"{i}. {suggestion.get('description', 'Test case')}")
                
                # End prompt
                console.print("\n[bold green]Use this context to write comprehensive tests for this function.[/bold green]")
                console.print("[italic]This information is also saved in the test_suggestions.json file.[/italic]")
                
                return 0
        
        # Display suggestions (non-prompt mode)
        console.print(f"\n[bold green]Generated {len(suggestions)} test suggestions:[/bold green]\n")
        
        for i, suggestion in enumerate(suggestions, 1):
            test_name = suggestion.get("test_name", "")
            target_node = suggestion.get("target_node", "")
            skeleton = suggestion.get("skeleton", "")
            
            # Create a syntax-highlighted panel for the skeleton
            syntax = Syntax(skeleton, "python", theme="monokai", line_numbers=True)
            
            # Determine source of suggestion
            source = "[bold blue]Heuristic[/bold blue]"
            if suggestion.get("llm", False):
                model_name = suggestion.get("model", "LLM")
                source = f"[bold magenta]{model_name}[/bold magenta]"
            
            panel = Panel(
                syntax,
                title=f"[{i}] {test_name}",
                subtitle=f"Target: {target_node} | Source: {source}"
            )
            
            console.print(panel)
            console.print()
        
        # Output file path
        if not json_output:
            output_file = PathResolver.knowledge_graph_dir() / "test_suggestions.json"
            console.print(f"Suggestions written to: [bold]{output_file}[/bold]")
        else:
            console.print(f"Suggestions written to: [bold]{json_output}[/bold]")
            
        console.print("\nTo run these tests, create a test file with the suggested functions.")
        
    except Exception as e:
        logger.error(f"Failed to generate test suggestions: {e}")
        if verbose:
            logger.error(traceback.format_exc())
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(2) 