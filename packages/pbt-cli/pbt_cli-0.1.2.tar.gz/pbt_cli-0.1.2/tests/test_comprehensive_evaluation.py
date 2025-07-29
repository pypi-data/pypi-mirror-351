"""Example of how to implement comprehensive prompt testing"""

import json
from typing import Dict, List, Any


class ComprehensivePromptTester:
    """Enhanced prompt tester that evaluates multiple aspects"""
    
    def __init__(self, prompt_file: str, model: str = "claude"):
        self.prompt_file = prompt_file
        self.model = model
        self.evaluation_aspects = {
            "correctness": "Is the output sensible and accurate for the given input?",
            "faithfulness": "Does the output preserve the original meaning and intent?",
            "style_tone": "Is the output appropriately concise or verbose for the use case?",
            "safety": "Does the output avoid harmful, biased, or inappropriate content?",
            "stability": "Would similar inputs produce consistent outputs?",
            "model_quality": "How does this model's output compare to others?"
        }
    
    def evaluate_test_case(self, test_case: Dict) -> Dict[str, Any]:
        """Evaluate a single test case across all aspects"""
        input_data = test_case.get("input", {})
        expected = test_case.get("expected", "")
        
        # Run the prompt with input
        output = self.run_prompt(input_data)
        
        # Evaluate each aspect
        evaluations = {}
        for aspect, question in self.evaluation_aspects.items():
            score = self.evaluate_aspect(
                aspect=aspect,
                question=question,
                input_data=input_data,
                output=output,
                expected=expected
            )
            evaluations[aspect] = score
        
        return {
            "test_case": test_case,
            "output": output,
            "evaluations": evaluations,
            "overall_score": sum(evaluations.values()) / len(evaluations),
            "passed": all(score >= 7 for score in evaluations.values())
        }
    
    def evaluate_aspect(self, aspect: str, question: str, 
                       input_data: Dict, output: str, expected: str) -> float:
        """Evaluate a specific aspect using an LLM judge"""
        
        evaluation_prompt = f"""
        Evaluate the following output for {aspect}.
        
        Question: {question}
        
        Input: {json.dumps(input_data)}
        Output: {output}
        Expected (if any): {expected}
        
        Score from 1-10 where:
        1-3: Poor
        4-6: Acceptable
        7-8: Good
        9-10: Excellent
        
        Provide only a numeric score.
        """
        
        # In real implementation, this would call an LLM
        # For now, return a mock score
        mock_scores = {
            "correctness": 8.5,
            "faithfulness": 9.0,
            "style_tone": 7.5,
            "safety": 9.5,
            "stability": 8.0,
            "model_quality": 8.0
        }
        return mock_scores.get(aspect, 7.0)
    
    def run_prompt(self, input_data: Dict) -> str:
        """Run the prompt with given inputs"""
        # In real implementation, this would:
        # 1. Load the prompt template
        # 2. Substitute variables
        # 3. Call the LLM
        # 4. Return the response
        return "Cats are curious and independent creatures who love to explore."
    
    def run_stability_test(self, test_case: Dict, num_runs: int = 5) -> Dict:
        """Test output consistency across multiple runs"""
        outputs = []
        for _ in range(num_runs):
            output = self.run_prompt(test_case.get("input", {}))
            outputs.append(output)
        
        # Calculate consistency score
        # In real implementation, would use semantic similarity
        consistency_score = 0.85  # Mock score
        
        return {
            "outputs": outputs,
            "consistency_score": consistency_score,
            "is_stable": consistency_score >= 0.8
        }
    
    def compare_models(self, test_case: Dict, models: List[str]) -> Dict:
        """Compare outputs across different models"""
        results = {}
        for model in models:
            self.model = model
            output = self.run_prompt(test_case.get("input", {}))
            evaluation = self.evaluate_test_case(test_case)
            results[model] = {
                "output": output,
                "score": evaluation["overall_score"]
            }
        
        # Rank models
        ranked = sorted(results.items(), key=lambda x: x[1]["score"], reverse=True)
        
        return {
            "results": results,
            "ranking": [model for model, _ in ranked],
            "best_model": ranked[0][0]
        }


# Example enhanced test file format
ENHANCED_TEST_FORMAT = {
    "prompt_file": "summarizer.prompt.yaml",
    "test_cases": [
        {
            "name": "cat_curiosity_test",
            "input": {"text": "Cats are curious creatures who like to explore."},
            "expected": "Cats like to explore and are curious.",
            "evaluate": {
                "correctness": True,
                "faithfulness": True,
                "style_tone": "concise",
                "safety": True,
                "stability": True,
                "model_quality": ["gpt-4", "claude"]
            }
        }
    ],
    "evaluation_config": {
        "min_scores": {
            "correctness": 7,
            "faithfulness": 8,
            "style_tone": 6,
            "safety": 9,
            "stability": 7
        },
        "stability_runs": 5,
        "comparison_models": ["gpt-4", "claude", "gpt-3.5-turbo"]
    }
}


def enhanced_test_runner(test_file: str):
    """Run enhanced tests with comprehensive evaluation"""
    
    # Load test configuration
    with open(test_file, 'r') as f:
        config = json.load(f)
    
    prompt_file = config["prompt_file"]
    tester = ComprehensivePromptTester(prompt_file)
    
    results = []
    for test_case in config["test_cases"]:
        print(f"\n🧪 Running test: {test_case['name']}")
        
        # Basic evaluation
        result = tester.evaluate_test_case(test_case)
        
        # Stability test if requested
        if test_case.get("evaluate", {}).get("stability"):
            stability = tester.run_stability_test(test_case)
            result["stability"] = stability
        
        # Model comparison if requested
        if "model_quality" in test_case.get("evaluate", {}):
            models = test_case["evaluate"]["model_quality"]
            comparison = tester.compare_models(test_case, models)
            result["model_comparison"] = comparison
        
        results.append(result)
        
        # Print results
        print(f"\n📊 Results for {test_case['name']}:")
        print(f"Overall Score: {result['overall_score']:.1f}/10")
        print("\nAspect Scores:")
        for aspect, score in result["evaluations"].items():
            print(f"  {aspect}: {score:.1f}/10")
        
        if "stability" in result:
            print(f"\nStability: {result['stability']['consistency_score']:.2f}")
        
        if "model_comparison" in result:
            print(f"\nBest Model: {result['model_comparison']['best_model']}")
    
    return results


# Example usage in a test
def test_comprehensive_evaluation():
    """Test showing how comprehensive evaluation would work"""
    
    # Create test case
    test_case = {
        "input": {"text": "Cats are curious creatures who like to explore."},
        "expected": "Cats like to explore and are curious."
    }
    
    # Run comprehensive test
    tester = ComprehensivePromptTester("summarizer.prompt.yaml")
    result = tester.evaluate_test_case(test_case)
    
    # Check all aspects were evaluated
    assert "correctness" in result["evaluations"]
    assert "faithfulness" in result["evaluations"]
    assert "style_tone" in result["evaluations"]
    assert "safety" in result["evaluations"]
    assert "stability" in result["evaluations"]
    assert "model_quality" in result["evaluations"]
    
    # Check scores are reasonable
    assert all(0 <= score <= 10 for score in result["evaluations"].values())
    assert result["overall_score"] > 0
    
    print("\n✅ Comprehensive evaluation test passed!")


if __name__ == "__main__":
    test_comprehensive_evaluation()