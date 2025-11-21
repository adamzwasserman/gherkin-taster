"""
Unit Tests: Gherkin Validation
Tests for backend/gherkin/validation.py
"""

import pytest
from backend.gherkin.validation import (
    validate_gherkin,
    validate_business_rules,
    ValidationResult,
)


def test_validate_gherkin_valid(sample_gherkin_valid):
    """Test validation of valid Gherkin syntax"""
    result = validate_gherkin(sample_gherkin_valid)

    assert result.is_valid is True
    assert len(result.errors) == 0
    assert result.scenario_count == 1
    assert result.step_count == 5


def test_validate_gherkin_invalid(sample_gherkin_invalid):
    """Test validation of invalid Gherkin syntax"""
    result = validate_gherkin(sample_gherkin_invalid)

    assert result.is_valid is False
    assert len(result.errors) > 0
    assert result.scenario_count == 0
    assert result.step_count == 0


def test_validate_gherkin_empty():
    """Test validation of empty content"""
    result = validate_gherkin("")

    assert result.is_valid is False
    assert len(result.errors) > 0


def test_validate_business_rules_no_description():
    """Test business rule: feature must have description"""
    content = """Feature: Login
  Scenario: User logs in
    Given I am on the login page
"""
    violations = validate_business_rules(content)

    assert len(violations) > 0
    assert any("description" in v.lower() for v in violations)


def test_validate_business_rules_no_given():
    """Test business rule: scenario must have Given step"""
    content = """Feature: Login
  As a user
  I want to login

  Scenario: User logs in
    When I click login
    Then I see dashboard
"""
    violations = validate_business_rules(content)

    assert len(violations) > 0
    assert any("given" in v.lower() for v in violations)


def test_validate_business_rules_commented_scenario():
    """Test business rule: no commented scenarios"""
    content = """Feature: Login
  As a user
  I want to login

  Scenario: User logs in
    Given I am on login page
    When I click login
    Then I see dashboard

  #Scenario: Incomplete scenario
  #  Given something
"""
    violations = validate_business_rules(content)

    assert len(violations) > 0
    assert any("commented" in v.lower() for v in violations)


def test_validate_business_rules_valid():
    """Test business rules with valid Gherkin"""
    content = """Feature: User Login
  As a registered user
  I want to log into the system

  Scenario: Successful login
    Given I am on the login page
    When I enter valid credentials
    Then I should be logged in
"""
    violations = validate_business_rules(content)

    assert len(violations) == 0
