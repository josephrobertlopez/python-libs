#!/usr/bin/env python3
"""
Test cleanup utility for consolidating test patterns using the new smart annotation framework.

This script analyzes test files and applies the consolidated mock framework patterns
to reduce boilerplate and improve maintainability.
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Set
from dataclasses import dataclass


@dataclass
class TestCleanupReport:
    """Report of cleanup operations performed."""

    files_processed: int = 0
    lines_removed: int = 0
    patterns_replaced: int = 0
    decorators_added: int = 0
    imports_consolidated: int = 0
    redundancy_eliminated: List[str] = None

    def __post_init__(self):
        if self.redundancy_eliminated is None:
            self.redundancy_eliminated = []


class TestCleaner:
    """Main class for cleaning up test files using consolidated patterns."""

    def __init__(self, test_dir: Path):
        self.test_dir = test_dir
        self.report = TestCleanupReport()

    def analyze_redundancy(self) -> Dict[str, List[Path]]:
        """Analyze test files for redundant patterns."""
        patterns = {}

        for test_file in self.test_dir.glob("test_*.py"):
            content = test_file.read_text()

            # Find common mock patterns
            if "smart_mock(" in content:
                patterns.setdefault("smart_mock_usage", []).append(test_file)

            if "Mock()" in content and content.count("Mock()") > 3:
                patterns.setdefault("excessive_mock_instances", []).append(test_file)

            if "with smart_mock" in content and content.count("with smart_mock") > 2:
                patterns.setdefault("nested_context_candidates", []).append(test_file)

            if "@patch" in content:
                patterns.setdefault("legacy_patch_decorators", []).append(test_file)

            if "class Test" in content and "unittest.TestCase" not in content:
                patterns.setdefault("pytest_style_classes", []).append(test_file)

        return patterns

    def suggest_cleanup_actions(self, patterns: Dict[str, List[Path]]) -> List[str]:
        """Suggest specific cleanup actions based on patterns found."""
        suggestions = []

        if "excessive_mock_instances" in patterns:
            suggestions.append(
                "🔄 Replace repeated Mock() instances with reusable fixtures in StandardTestCase"
            )

        if "nested_context_candidates" in patterns:
            suggestions.append(
                "📦 Replace nested smart_mock contexts with config_mock decorators"
            )

        if "legacy_patch_decorators" in patterns:
            suggestions.append(
                "🚀 Migrate @patch decorators to smart annotation decorators"
            )

        if "pytest_style_classes" in patterns:
            suggestions.append("🏗️ Extend StandardTestCase for shared mock utilities")

        return suggestions

    def count_boilerplate_lines(self, file_path: Path) -> int:
        """Count lines that could be considered boilerplate."""
        content = file_path.read_text()
        boilerplate_patterns = [
            r"mock = Mock\(\)",
            r"with smart_mock\(",
            r"from unittest\.mock import Mock",
            r"import pytest",
            r"class Test\w+:",
            r"def test_\w+\(self\):",
            r'\s+""".*"""',  # Single line docstrings
        ]

        boilerplate_count = 0
        for line in content.split("\n"):
            for pattern in boilerplate_patterns:
                if re.search(pattern, line.strip()):
                    boilerplate_count += 1
                    break

        return boilerplate_count

    def generate_consolidated_patterns(self) -> Dict[str, str]:
        """Generate consolidated patterns that can replace common test setups."""
        return {
            "basic_mock_setup": """
# BEFORE: Manual mock setup (5-8 lines)
def test_old_way(self):
    mock_obj = Mock()
    with smart_mock("module", attr=mock_obj):
        # test code
        pass

# AFTER: Decorator pattern (2 lines)
@smart_config_mock({"modules": {"module": {"attr": Mock()}}})
def test_new_way(self):
    # test code only
    pass
""",
            "nested_contexts": """
# BEFORE: Nested contexts (10+ lines)
def test_old_way(self):
    with smart_mock("sys", argv=["test"]):
        with smart_mock("os", getcwd="/test"):
            with smart_mock("time", sleep=Mock()):
                # test code
                pass

# AFTER: Single config (3 lines)
@config_mock({
    "modules": {
        "sys": {"argv": ["test"]},
        "os": {"getcwd": "/test"}, 
        "time": {"sleep": Mock()}
    }
})
def test_new_way(self):
    # test code only
    pass
""",
            "test_class_inheritance": """
# BEFORE: Plain pytest class
class TestMyFeature:
    def test_something(self):
        mock = Mock()
        # test code
        
# AFTER: StandardTestCase inheritance
class TestMyFeature(StandardTestCase):
    def test_something(self):
        # self.create_mock() and other utilities available
        # test code
""",
        }

    def run_cleanup_analysis(self) -> TestCleanupReport:
        """Run comprehensive cleanup analysis."""
        print("🧹 ANALYZING TEST FILES FOR CLEANUP OPPORTUNITIES")
        print("=" * 60)

        # Find all test files
        test_files = list(self.test_dir.glob("test_*.py"))
        self.report.files_processed = len(test_files)

        # Analyze redundancy patterns
        patterns = self.analyze_redundancy()

        print(f"\n📊 Analysis Results:")
        print(f"   Files analyzed: {len(test_files)}")
        print(f"   Pattern categories found: {len(patterns)}")

        # Count total boilerplate
        total_boilerplate = 0
        for file_path in test_files:
            boilerplate = self.count_boilerplate_lines(file_path)
            total_boilerplate += boilerplate

        self.report.lines_removed = total_boilerplate

        print(f"   Potential boilerplate lines: {total_boilerplate}")

        # Report by category
        for pattern_name, files in patterns.items():
            print(f"\n🔍 {pattern_name.replace('_', ' ').title()}:")
            for file_path in files[:5]:  # Limit to first 5 files
                rel_path = file_path.relative_to(self.test_dir)
                print(f"   - {rel_path}")
            if len(files) > 5:
                print(f"   ... and {len(files) - 5} more files")

        # Generate suggestions
        suggestions = self.suggest_cleanup_actions(patterns)

        print(f"\n💡 CLEANUP RECOMMENDATIONS:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"   {i}. {suggestion}")

        # Show consolidation examples
        consolidated_patterns = self.generate_consolidated_patterns()

        print(f"\n🎯 CONSOLIDATION EXAMPLES:")
        for pattern_name, example in consolidated_patterns.items():
            print(f"\n📋 {pattern_name.replace('_', ' ').title()}:")
            print(example)

        # Calculate potential savings
        estimated_reduction = int(total_boilerplate * 0.6)  # Estimate 60% reduction
        print(f"\n📈 ESTIMATED IMPROVEMENTS:")
        print(
            f"   Potential line reduction: ~{estimated_reduction} lines ({estimated_reduction/total_boilerplate*100:.1f}%)"
        )
        print(
            f"   Decorator patterns to add: ~{len(patterns.get('nested_context_candidates', []))}"
        )
        print(
            f"   Base class migrations: ~{len(patterns.get('pytest_style_classes', []))}"
        )

        self.report.patterns_replaced = len(patterns)
        self.report.decorators_added = len(
            patterns.get("nested_context_candidates", [])
        )
        self.report.redundancy_eliminated = list(patterns.keys())

        return self.report

    def generate_migration_plan(self) -> List[str]:
        """Generate step-by-step migration plan."""
        return [
            "1. 🏗️  Migrate test classes to extend StandardTestCase",
            "2. 🔄  Replace nested smart_mock contexts with @config_mock decorators",
            "3. 📦  Consolidate repeated Mock() instances using shared fixtures",
            "4. 🚀  Convert @patch decorators to smart annotation decorators",
            "5. 📋  Use test_configs.json for common patterns",
            "6. 🧪  Apply template_mock decorators for reusable scenarios",
            "7. ✅  Run test suite to verify all tests still pass",
            "8. 📚  Update documentation with new patterns",
        ]


def main():
    """Main function to run test cleanup analysis."""
    test_dir = Path("tests/utils/test")

    if not test_dir.exists():
        print(f"❌ Test directory {test_dir} not found")
        return

    cleaner = TestCleaner(test_dir)
    report = cleaner.run_cleanup_analysis()

    print(f"\n🚀 MIGRATION PLAN:")
    migration_steps = cleaner.generate_migration_plan()
    for step in migration_steps:
        print(f"   {step}")

    print(f"\n✅ CLEANUP ANALYSIS COMPLETE")
    print(f"   Ready to reduce ~{report.lines_removed * 0.6:.0f} lines of boilerplate")
    print(f"   Ready to add ~{report.decorators_added} smart decorators")
    print(f"   Ready to consolidate {report.patterns_replaced} pattern categories")


if __name__ == "__main__":
    main()
