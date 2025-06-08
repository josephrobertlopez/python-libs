Feature: Comprehensive Mock Testing Framework
  As a test developer
  I want a unified mocking framework with runtime configuration, AST analysis, and automated migration
  So that I can write maintainable tests with minimal boilerplate

  Background:
    Given the comprehensive mocking framework is available
    And I have access to runtime annotations, config factories, and AST analysis

  @runtime_configuration
  Scenario Outline: Runtime mock configuration with presets and templates
    Given I want to test with <config_type> configuration
    When I apply the configuration using <decorator_syntax>
    Then the mocks should be applied as <expected_behavior>
    And cleanup should happen automatically
    
    Examples:
      | config_type | decorator_syntax                                    | expected_behavior                    |
      | preset      | @runtime_mock("standard")                          | sys, os, builtins mocked with defaults |
      | custom      | @runtime_mock({"sys": {"argv": ["app", "--debug"]}}) | custom sys.argv configuration        |
      | template    | @runtime_mock("api_testing", endpoint="test")      | templated API mocks with variables   |
      | file-based  | @runtime_mock("configs/test_setup.json")           | configuration loaded from file       |

  @config_driven_factories
  Scenario: Config-driven mock factories with inheritance and composition
    Given I have a base configuration "web_app_base":
      """
      {
        "modules": {
          "sys": {"argv": ["webapp"], "stdout": "StringIO()"},
          "os": {"environ": {"FLASK_ENV": "testing"}}
        }
      }
      """
    And I have specialized configurations that extend the base
    When I create a factory with inheritance:
      """
      {
        "extends": "web_app_base",
        "modules": {
          "requests": {"get": {"return_value": {"status_code": 200}}},
          "sqlalchemy": {"create_engine": "Mock()"}
        }
      }
      """
    Then both base and specialized mocks should be active
    And inheritance order should be preserved
    And I can override base configurations in specialized ones

  @dynamic_context_management
  Scenario: Dynamic mock updates and nested context composition
    Given I start with a minimal mock configuration
    When I use runtime context managers:
      """
      with runtime_context("minimal") as ctx:
          # Test with minimal mocks
          ctx.update("sys", "argv", ["updated", "args"])
          ctx.add_module("requests", {"get": Mock()})
          
          with ctx.compose("logging_context") as inner_ctx:
              # Additional logging mocks
              inner_ctx.update("logging", "level", "DEBUG")
              # Test with both contexts active
      """
    Then each context should maintain its own scope
    And updates should be immediately available
    And cleanup should happen in reverse order

  @ast_analysis_and_code_quality  
  Scenario: AST analysis for code quality monitoring and optimization
    Given I have test files with various patterns:
      | file_type    | patterns                                              |
      | traditional  | unittest.mock.patch decorators, manual setUp/tearDown |
      | mixed        | some smart annotations, some manual patches           |
      | modern       | smart_config_mock, template_mock decorators          |
    When I run AST analysis on the test suite
    Then I should get detailed metrics:
      | metric_type          | information_provided                           |
      | complexity_scores    | per-file complexity based on pattern usage    |
      | optimization_opportunities | files with improvement potential      |
      | template_suggestions | reusable patterns detected across files       |
      | framework_health     | adoption rate and consistency metrics         |
    And the system should provide code quality recommendations

  @template_system
  Scenario: Template creation and reuse across test suites
    Given I have common mocking patterns repeated across multiple files
    When I analyze for template opportunities:
      | pattern_name     | modules_involved              | usage_count |
      | api_integration  | requests, json, os.environ    | 15          |
      | database_testing | sqlalchemy, psycopg2, os      | 8           |
      | file_processing  | pathlib, os.path, builtins    | 12          |
    Then the system should generate reusable templates:
      """
      api_integration:
        modules:
          requests:
            get: ${get_mock}
            post: ${post_mock}
          json:
            loads: ${json_loads_mock}
          os:
            environ: ${env_config}
      """
    And provide implementation instructions for each template

  @framework_health_monitoring
  Scenario: Continuous framework health monitoring and quality gates
    Given I have a test suite with mixed patterns
    When I run comprehensive health analysis
    Then I should get a health report with:
      | health_aspect           | metrics_tracked                                    |
      | adoption_rate          | percentage of files using modern patterns          |
      | complexity_distribution| breakdown of files by complexity level             |
      | optimization_opportunities| specific files needing attention                   |
      | performance_impact     | test execution speed improvements                  |
      | quality_gates          | pass/fail status for defined thresholds           |
    And the system should enforce quality gates:
      | gate_name               | threshold | enforcement_action              |
      | framework_adoption_rate | 75%       | block_merge_if_below           |
      | legacy_pattern_count    | <10       | require_migration_plan         |
      | test_complexity_avg     | medium    | flag_for_review                |

  @integration_and_composition
  Scenario: Complex integration scenarios with multiple mocking approaches
    Given I need to test a complex system with multiple dependencies:
      | dependency_type | mocking_approach                              |
      | external_apis   | template_mock("api_testing")                 |
      | database        | smart_config_mock with SQLAlchemy mocks     |
      | file_system     | @file_system_test decorator                  |
      | environment     | runtime_context with env variable updates   |
    When I compose all mocking approaches in a single test:
      """
      @template_mock("api_testing", endpoint="http://test.api")
      @smart_config_mock("database_testing")
      @file_system_test(files_exist={"config.json": True})
      def test_complex_integration(self):
          with runtime_context() as ctx:
              ctx.update("os", "environ", {"DEBUG": "1"})
              # Test complex system integration
      """
    Then all mocks should work together without conflicts
    And each mocking layer should maintain its own scope
    And cleanup should happen correctly for all layers

  @performance_and_optimization
  Scenario: Framework performance monitoring and optimization
    Given I want to ensure the mocking framework doesn't impact test performance
    When I run performance benchmarks comparing:
      | approach_type    | setup_time | execution_time | memory_usage |
      | manual_patching  | 2.5s       | 45s           | 150MB        |
      | smart_annotations| 1.8s       | 38s           | 120MB        |
      | config_factories | 1.6s       | 35s           | 110MB        |
    Then the modern approaches should show performance improvements
    And the framework should provide optimization recommendations
    And performance regressions should be detected automatically
