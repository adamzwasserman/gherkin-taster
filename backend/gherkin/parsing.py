"""
Gherkin Parsing
Pure functions for parsing Gherkin into structured data for preview
"""

from typing import Optional
from dataclasses import dataclass
from gherkin.parser import Parser


@dataclass
class GherkinStep:
    """Gherkin step"""

    keyword: str
    text: str
    doc_string: Optional[str] = None
    data_table: Optional[list[list[str]]] = None


@dataclass
class GherkinScenario:
    """Gherkin scenario or scenario outline"""

    keyword: str
    name: str
    description: Optional[str]
    steps: list[GherkinStep]
    examples: Optional[list[list[str]]] = None


@dataclass
class GherkinFeature:
    """Gherkin feature"""

    name: str
    description: Optional[str]
    tags: list[str]


@dataclass
class ParsedFeature:
    """Parsed Gherkin feature with all elements"""

    feature: GherkinFeature
    scenarios: list[GherkinScenario]


def parse_gherkin(content: str) -> Optional[ParsedFeature]:
    """
    Parse Gherkin content into structured data for preview

    Args:
        content: Gherkin feature file content

    Returns:
        ParsedFeature if valid, None if parsing fails
    """
    parser = Parser()

    try:
        gherkin_document = parser.parse(content)
        feature_node = gherkin_document["feature"]

        if not feature_node:
            return None

        # Parse feature
        feature = GherkinFeature(
            name=feature_node.get("name", ""),
            description=feature_node.get("description", "").strip() or None,
            tags=[tag["name"] for tag in feature_node.get("tags", [])],
        )

        # Parse scenarios
        scenarios = []
        for child in feature_node.get("children", []):
            if "scenario" in child:
                scenario_node = child["scenario"]
                scenarios.append(_parse_scenario(scenario_node))

        return ParsedFeature(feature=feature, scenarios=scenarios)

    except Exception:
        return None


def _parse_scenario(scenario_node: dict) -> GherkinScenario:
    """
    Parse scenario node into GherkinScenario

    Args:
        scenario_node: Scenario dict from parser

    Returns:
        GherkinScenario
    """
    # Parse steps
    steps = []
    for step_node in scenario_node.get("steps", []):
        step = GherkinStep(
            keyword=step_node["keyword"],
            text=step_node["text"],
        )

        # Parse doc string
        if "docString" in step_node:
            step.doc_string = step_node["docString"]["content"]

        # Parse data table
        if "dataTable" in step_node:
            rows = []
            for row in step_node["dataTable"]["rows"]:
                cells = [cell["value"] for cell in row["cells"]]
                rows.append(cells)
            step.data_table = rows

        steps.append(step)

    # Parse examples (for scenario outlines)
    examples = None
    if scenario_node.get("examples"):
        examples_node = scenario_node["examples"][0]
        if "tableHeader" in examples_node and "tableBody" in examples_node:
            examples = []

            # Header row
            header = [cell["value"] for cell in examples_node["tableHeader"]["cells"]]
            examples.append(header)

            # Data rows
            for row in examples_node["tableBody"]:
                cells = [cell["value"] for cell in row["cells"]]
                examples.append(cells)

    return GherkinScenario(
        keyword=scenario_node["keyword"],
        name=scenario_node["name"],
        description=scenario_node.get("description", "").strip() or None,
        steps=steps,
        examples=examples,
    )
