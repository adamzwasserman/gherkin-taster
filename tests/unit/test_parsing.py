"""
Unit Tests: Gherkin Parsing
Tests for backend/gherkin/parsing.py
"""

import pytest
from backend.gherkin.parsing import parse_gherkin, ParsedFeature


def test_parse_gherkin_valid(sample_gherkin_valid):
    """Test parsing valid Gherkin content"""
    result = parse_gherkin(sample_gherkin_valid)

    assert result is not None
    assert isinstance(result, ParsedFeature)
    assert result.feature.name == "User Login"
    assert result.feature.description is not None
    assert len(result.scenarios) == 1
    assert result.scenarios[0].name == "Successful login with valid credentials"
    assert len(result.scenarios[0].steps) == 5


def test_parse_gherkin_with_tags():
    """Test parsing Gherkin with tags"""
    content = """@smoke @critical
Feature: User Login
  As a user
  I want to login

  Scenario: Login success
    Given I am on login page
    When I login
    Then I see dashboard
"""
    result = parse_gherkin(content)

    assert result is not None
    assert "@smoke" in result.feature.tags
    assert "@critical" in result.feature.tags


def test_parse_gherkin_with_data_table():
    """Test parsing Gherkin with data table"""
    content = """Feature: Data Entry
  Scenario: Enter user data
    Given I have the following users:
      | name  | email           |
      | Alice | alice@test.com  |
      | Bob   | bob@test.com    |
    When I submit the form
    Then users should be created
"""
    result = parse_gherkin(content)

    assert result is not None
    assert len(result.scenarios) == 1
    steps_with_table = [s for s in result.scenarios[0].steps if s.data_table]
    assert len(steps_with_table) == 1
    assert len(steps_with_table[0].data_table) == 3  # Header + 2 rows


def test_parse_gherkin_with_doc_string():
    """Test parsing Gherkin with doc string"""
    content = '''Feature: API Testing
  Scenario: Send JSON request
    Given I have a request body:
      """
      {
        "username": "test",
        "password": "secret"
      }
      """
    When I send POST request
    Then response is 200
'''
    result = parse_gherkin(content)

    assert result is not None
    steps_with_doc = [s for s in result.scenarios[0].steps if s.doc_string]
    assert len(steps_with_doc) == 1
    assert "username" in steps_with_doc[0].doc_string


def test_parse_gherkin_with_scenario_outline():
    """Test parsing Gherkin with scenario outline and examples"""
    content = """Feature: Login
  Scenario Outline: Login with credentials
    Given I am on login page
    When I enter username "<username>"
    And I enter password "<password>"
    Then I should see "<result>"

    Examples:
      | username | password | result    |
      | valid    | valid    | Dashboard |
      | invalid  | invalid  | Error     |
"""
    result = parse_gherkin(content)

    assert result is not None
    assert len(result.scenarios) == 1
    assert result.scenarios[0].examples is not None
    assert len(result.scenarios[0].examples) == 3  # Header + 2 rows


def test_parse_gherkin_invalid():
    """Test parsing invalid Gherkin returns None"""
    content = """Not valid Gherkin syntax at all"""
    result = parse_gherkin(content)

    assert result is None


def test_parse_gherkin_empty():
    """Test parsing empty content returns None"""
    result = parse_gherkin("")

    assert result is None
