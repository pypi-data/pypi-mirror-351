"""Helper functions for CLI validation integration.

Provides utilities for validating pipelines with caching and formatting errors
for CLI output.
"""

from pathlib import Path
from typing import List

import typer

from sqlflow.cli.validation_cache import ValidationCache
from sqlflow.logging import get_logger
from sqlflow.parser.parser import Parser
from sqlflow.validation.errors import ValidationError

logger = get_logger(__name__)


def _read_pipeline_file(pipeline_path: str) -> str:
    """Read pipeline file content with error handling.

    Args:
    ----
        pipeline_path: Path to the pipeline file

    Returns:
    -------
        Pipeline file content

    Raises:
    ------
        typer.Exit: If file cannot be read

    """
    pipeline_file = Path(pipeline_path)
    if not pipeline_file.exists():
        typer.echo(f"❌ Pipeline file not found: {pipeline_path}")
        raise typer.Exit(1)

    try:
        with open(pipeline_file, "r", encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError) as e:
        typer.echo(f"❌ Cannot read pipeline file {pipeline_path}: {str(e)}")
        raise typer.Exit(1)


def _parse_and_validate_pipeline(
    pipeline_text: str, pipeline_path: str
) -> List[ValidationError]:
    """Parse and validate pipeline text.

    Args:
    ----
        pipeline_text: Pipeline content to parse
        pipeline_path: Path for logging purposes

    Returns:
    -------
        List of validation errors

    """
    parser = Parser()
    errors = []

    try:
        # Parse with validation enabled
        parser.parse(pipeline_text, validate=True)
        logger.debug("Pipeline validation passed for %s", pipeline_path)

    except ValidationError as e:
        # Single validation error
        errors = [e]
        logger.debug("Pipeline validation found 1 error for %s", pipeline_path)

    except Exception as e:
        # Check if this is an AggregatedValidationError
        from sqlflow.validation import AggregatedValidationError

        if isinstance(e, AggregatedValidationError):
            # Extract all validation errors from the aggregated error
            errors = e.errors
            logger.debug(
                "Pipeline validation found %d errors for %s", len(errors), pipeline_path
            )
        else:
            # Parser error or other issues
            error_msg = str(e)
            if "Multiple errors found:" in error_msg:
                # Handle multiple parsing errors - convert to validation errors
                errors = [
                    ValidationError(
                        message=error_msg, line=1, error_type="Parser Error"
                    )
                ]
            else:
                # Single parser error
                errors = [
                    ValidationError(
                        message=error_msg, line=1, error_type="Parser Error"
                    )
                ]
            logger.debug("Pipeline parsing failed for %s: %s", pipeline_path, error_msg)

    return errors


def validate_pipeline_with_caching(
    pipeline_path: str, project_dir: str = "."
) -> List[ValidationError]:
    """Validate a pipeline file with smart caching.

    Args:
    ----
        pipeline_path: Path to the pipeline file
        project_dir: Project directory (defaults to current directory)

    Returns:
    -------
        List of validation errors (empty if valid)

    Raises:
    ------
        typer.Exit: If pipeline file cannot be read

    """
    try:
        # Initialize cache
        cache = ValidationCache(project_dir)

        # Check cache first
        cached_errors = cache.get_cached_errors(pipeline_path)
        if cached_errors is not None:
            logger.debug("Using cached validation results for %s", pipeline_path)
            return cached_errors

        # Read and validate pipeline
        pipeline_text = _read_pipeline_file(pipeline_path)
        errors = _parse_and_validate_pipeline(pipeline_text, pipeline_path)

        # Cache the results
        cache.store_errors(pipeline_path, errors)

        return errors

    except typer.Exit:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during validation of %s: %s", pipeline_path, str(e)
        )
        return [
            ValidationError(
                message=f"Validation failed: {str(e)}",
                line=1,
                error_type="Internal Error",
            )
        ]


def _group_errors_by_type(errors: List[ValidationError]) -> dict:
    """Group validation errors by type.

    Args:
    ----
        errors: List of validation errors

    Returns:
    -------
        Dictionary mapping error types to lists of errors

    """
    error_groups = {}
    for error in errors:
        error_type = error.error_type
        if error_type not in error_groups:
            error_groups[error_type] = []
        error_groups[error_type].append(error)
    return error_groups


def _format_single_error(error: ValidationError, show_details: bool) -> List[str]:
    """Format a single validation error.

    Args:
    ----
        error: Validation error to format
        show_details: Whether to show detailed information

    Returns:
    -------
        List of formatted lines for this error

    """
    lines = []

    # Main error line
    if error.column > 0:
        lines.append(f"  Line {error.line}, Column {error.column}: {error.message}")
    else:
        lines.append(f"  Line {error.line}: {error.message}")

    # Show suggestions if available and details requested
    if show_details and error.suggestions:
        for suggestion in error.suggestions:
            lines.append(f"    💡 {suggestion}")

    # Show help URL if available
    if show_details and error.help_url:
        lines.append(f"    📖 Help: {error.help_url}")

    lines.append("")  # Empty line between errors
    return lines


def format_validation_errors_for_cli(
    errors: List[ValidationError], show_details: bool = True
) -> str:
    """Format validation errors for CLI output.

    Args:
    ----
        errors: List of validation errors
        show_details: Whether to show detailed error information

    Returns:
    -------
        Formatted error message string

    """
    if not errors:
        return "✅ Pipeline validation passed!"

    # Group errors by type for better organization
    error_groups = _group_errors_by_type(errors)

    # Format output
    lines = []
    lines.append(f"❌ Pipeline validation failed with {len(errors)} error(s):")
    lines.append("")

    for error_type, type_errors in error_groups.items():
        if len(error_groups) > 1:
            lines.append(f"📋 {error_type}s:")

        for error in type_errors:
            lines.extend(_format_single_error(error, show_details))

    # Add summary
    if not show_details:
        lines.append("Run with --verbose for detailed suggestions.")

    return "\n".join(lines).rstrip()


def print_validation_summary(
    errors: List[ValidationError], pipeline_name: str, quiet: bool = False
) -> None:
    """Print validation summary to console.

    Args:
    ----
        errors: List of validation errors
        pipeline_name: Name of the pipeline being validated
        quiet: Whether to use quiet output mode

    """
    if not errors:
        if not quiet:
            typer.echo(f"✅ Pipeline '{pipeline_name}' validation passed!")
        return

    # Show detailed errors unless in quiet mode
    show_details = not quiet
    formatted_errors = format_validation_errors_for_cli(
        errors, show_details=show_details
    )

    # Use stderr for errors
    typer.echo(formatted_errors, err=True)


def validate_and_exit_on_error(
    pipeline_path: str, pipeline_name: str, quiet: bool = False
) -> None:
    """Validate pipeline and exit with error code if validation fails.

    This is a convenience function for CLI commands that should stop execution
    if validation fails.

    Args:
    ----
        pipeline_path: Path to the pipeline file
        pipeline_name: Name of the pipeline for display
        quiet: Whether to use quiet output mode

    Raises:
    ------
        typer.Exit: If validation fails (exit code 1)

    """
    errors = validate_pipeline_with_caching(pipeline_path)

    if errors:
        print_validation_summary(errors, pipeline_name, quiet=quiet)
        raise typer.Exit(1)

    if not quiet:
        logger.debug("Pipeline validation passed for %s", pipeline_name)
