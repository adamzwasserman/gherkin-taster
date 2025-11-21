"""
Gherkin Validation
Pure functions for validating Gherkin syntax using gherkin-official parser
"""

from typing import Optional
from dataclasses import dataclass
from gherkin.parser import Parser
from gherkin.pickles.compiler import Compiler


@dataclass
class ValidationError:
    """Gherkin syntax error"""

    line: int
    column: int
    message: str


@dataclass
class ValidationResult:
    """Result of Gherkin validation"""

    is_valid: bool
    errors: list[ValidationError]
    scenario_count: int
    step_count: int


def validate_gherkin(content: str) -> ValidationResult:
    """
    Validate Gherkin syntax and return detailed results

    Args:
        content: Gherkin feature file content

    Returns:
        ValidationResult with validity status, errors, and metrics
    """
    parser = Parser()
    errors = []
    scenario_count = 0
    step_count = 0

    try:
        # Parse Gherkin content
        gherkin_document = parser.parse(content)

        # Compile to pickles (scenarios with examples expanded)
        compiler = Compiler()
        pickles = compiler.compile(gherkin_document)

        # Count scenarios and steps
        scenario_count = len(pickles)
        step_count = sum(len(pickle.steps) for pickle in pickles)

        return ValidationResult(
            is_valid=True,
            errors=[],
            scenario_count=scenario_count,
            step_count=step_count,
        )

    except Exception as e:
        # Parse error to extract line/column info
        error_message = str(e)
        line_number = _extract_line_number(error_message)

        errors.append(
            ValidationError(
                line=line_number,
                column=0,
                message=error_message,
            )
        )

        return ValidationResult(
            is_valid=False,
            errors=errors,
            scenario_count=0,
            step_count=0,
        )


def _extract_line_number(error_message: str) -> int:
    """
    Extract line number from Gherkin parser error message

    Args:
        error_message: Error message from parser

    Returns:
        int: Line number (1 if not found)
    """
    # Gherkin parser errors often include "(line: N)" format
    import re

    match = re.search(r"\((\d+):", error_message)
    if match:
        return int(match.group(1))

    match = re.search(r"line (\d+)", error_message, re.IGNORECASE)
    if match:
        return int(match.group(1))

    return 1


def validate_business_rules(content: str) -> list[str]:
    """
    Validate business-specific Gherkin rules beyond syntax

    Args:
        content: Gherkin feature file content

    Returns:
        list[str]: List of business rule violations (empty if valid)
    """
    violations = []

    # Rule: Feature must have description
    if "Feature:" in content:
        feature_line_idx = content.index("Feature:")
        next_scenario = content.find("Scenario:", feature_line_idx)
        feature_section = (
            content[feature_line_idx:next_scenario]
            if next_scenario != -1
            else content[feature_line_idx:]
        )

        # Check if there's text after "Feature: <name>"
        lines = feature_section.split("\n")
        if len(lines) < 3:  # Feature line + blank + description
            violations.append(
                "Feature must include a description explaining business value"
            )

    # Rule: Scenarios must have Given steps
    if "Scenario:" in content:
        scenarios = content.split("Scenario:")[1:]
        for idx, scenario in enumerate(scenarios, 1):
            if "Given" not in scenario:
                violations.append(
                    f"Scenario {idx} must include at least one Given step (preconditions)"
                )

    # Rule: No commented-out scenarios (indicates incomplete work)
    if "#Scenario:" in content or "# Scenario:" in content:
        violations.append(
            "Commented-out scenarios detected - remove or complete before approval"
        )

    return violations
