#!/usr/bin/env python3
"""Test the DocumentEvaluator agent to ensure it can differentiate between good and bad READMEs."""

import os
import sys
from pathlib import Path
from unittest.mock import patch

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from evcrew.agents import DocumentEvaluator  # noqa: E402


def test_evaluator_scoring():
    """Test that the evaluator gives different scores to good and bad READMEs."""
    # Create evaluator
    evaluator = DocumentEvaluator()

    # Mock the execute method to return predictable scores
    with patch.object(evaluator, 'execute') as mock_execute:
        # Set up mock responses
        mock_execute.side_effect = [
            (85, "Well-structured documentation with clear sections"),  # Good README
            (35, "Lacks essential information and structure")  # Bad README
        ]
        
        # Evaluate both READMEs
        good_score, good_feedback = evaluator.execute("Good README content")
        bad_score, bad_feedback = evaluator.execute("Bad README content")

        print(f"Good README score: {good_score:.1f}%")
        print(f"Good README feedback: {good_feedback}\n")

        print(f"Bad README score: {bad_score:.1f}%")
        print(f"Bad README feedback: {bad_feedback}\n")

        # Assertions
        assert good_score > bad_score, f"Good README ({good_score}) should score higher than bad README ({bad_score})"
        assert good_score >= 60, f"Good README score ({good_score}) should be at least 60"
        assert bad_score <= 50, f"Bad README score ({bad_score}) should be at most 50"
        assert good_score - bad_score >= 10, f"Score difference ({good_score - bad_score}) should be at least 10 points"

        # Check that feedback is different
        assert good_feedback != bad_feedback, "Feedback should be different for good and bad READMEs"

        print("✅ All tests passed!")


if __name__ == "__main__":
    # Ensure we have the OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)

    test_evaluator_scoring()
