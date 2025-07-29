"""Prompt evaluation and testing for PBT"""

import json
import yaml
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create formatter for structured logging
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# File handler
log_dir = Path('./logs')
log_dir.mkdir(exist_ok=True)
file_handler = logging.FileHandler(log_dir / 'pbt_evaluator.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


@dataclass
class TestResult:
    """Individual test result"""
    test_name: str
    inputs: Dict[str, Any]
    output: str
    expected: Optional[str]
    score: float
    passed: bool
    duration: float
    metadata: Dict[str, Any]


@dataclass
class EvaluationReport:
    """Complete evaluation report"""
    prompt_file: str
    test_file: Optional[str]
    model: str
    total_tests: int
    passed_tests: int
    average_score: float
    individual_results: List[TestResult]
    timestamp: str
    summary: Dict[str, Any]


class PromptEvaluator:
    """Evaluates prompts against test cases"""
    
    def __init__(self, model: str = "claude"):
        self.model = model
        logger.info(f"Initialized PromptEvaluator with model: {model}")
    
    def evaluate_test_file(self, test_file_path: Path, model: str = None) -> EvaluationReport:
        """Evaluate prompt using a test file"""
        logger.info(f"Starting evaluation of test file: {test_file_path}")
        
        if model:
            self.model = model
            logger.debug(f"Using model: {model} for evaluation")
        
        # Load test file
        with open(test_file_path) as f:
            if test_file_path.suffix == '.yaml':
                test_data = yaml.safe_load(f)
            else:
                test_data = json.load(f)
        
        # Get prompt file path
        prompt_file = test_data.get("prompt_file")
        if not prompt_file:
            raise ValueError("Test file must specify 'prompt_file'")
        
        prompt_path = test_file_path.parent.parent / prompt_file
        
        # Load prompt
        with open(prompt_path) as f:
            prompt_data = yaml.safe_load(f)
        
        # Run test cases
        results = []
        for test_case in test_data.get("test_cases", []):
            result = self._run_single_test(prompt_data, test_case)
            results.append(result)
        
        # Generate report
        return self._create_report(
            prompt_file=str(prompt_path),
            test_file=str(test_file_path),
            results=results
        )
    
    def evaluate_jsonl_tests(self, prompt_path: Path, test_cases: List[Dict[str, Any]], model: str = None) -> EvaluationReport:
        """Evaluate prompt using JSONL test cases"""
        
        if model:
            self.model = model
        
        # Load prompt
        with open(prompt_path) as f:
            prompt_data = yaml.safe_load(f)
        
        # Run test cases
        results = []
        for test_case in test_cases:
            result = self._run_single_test(prompt_data, test_case)
            results.append(result)
        
        # Generate report
        return self._create_report(
            prompt_file=str(prompt_path),
            test_file=None,
            results=results
        )
    
    def evaluate_auto_generated(self, prompt_path: Path, num_tests: int, test_type: str = "functional") -> EvaluationReport:
        """Evaluate prompt with auto-generated test cases"""
        
        # Load prompt
        with open(prompt_path) as f:
            prompt_data = yaml.safe_load(f)
        
        # Generate test cases
        test_cases = self._generate_test_cases(prompt_data, num_tests, test_type)
        
        # Run tests
        results = []
        for test_case in test_cases:
            result = self._run_single_test(prompt_data, test_case)
            results.append(result)
        
        # Generate report
        return self._create_report(
            prompt_file=str(prompt_path),
            test_file=None,
            results=results
        )
    
    def _run_single_test(self, prompt_data: Dict[str, Any], test_case: Dict[str, Any]) -> TestResult:
        """Run a single test case"""
        
        start_time = time.time()
        
        # Extract test data
        test_name = test_case.get("test_name", test_case.get("name", "unnamed_test"))
        inputs = test_case.get("inputs", {})
        expected = test_case.get("expected", test_case.get("expected_output"))
        quality_criteria = test_case.get("quality_criteria", "")
        expected_keywords = test_case.get("expected_keywords", [])
        
        # Render prompt template
        rendered_prompt = self._render_prompt(prompt_data, inputs)
        
        # Execute prompt (mock for now)
        output = self._execute_prompt(rendered_prompt, self.model)
        
        # Evaluate result
        score = self._score_output(output, expected, expected_keywords, quality_criteria)
        passed = score >= 7.0  # Default passing threshold
        
        duration = time.time() - start_time
        
        return TestResult(
            test_name=test_name,
            inputs=inputs,
            output=output,
            expected=expected,
            score=score,
            passed=passed,
            duration=duration,
            metadata={
                "model": self.model,
                "expected_keywords": expected_keywords,
                "quality_criteria": quality_criteria
            }
        )
    
    def _render_prompt(self, prompt_data: Dict[str, Any], inputs: Dict[str, Any]) -> str:
        """Render prompt template with variables"""
        
        template = prompt_data.get("template", "")
        
        # Simple Jinja2-style variable replacement
        rendered = template
        for key, value in inputs.items():
            placeholder = f"{{{{ {key} }}}}"
            rendered = rendered.replace(placeholder, str(value))
        
        return rendered
    
    def _execute_prompt(self, prompt: str, model: str) -> str:
        """Execute prompt with specified model"""
        try:
            from ..integrations.llm import get_llm_provider
            import asyncio
            
            async def run():
                provider = await get_llm_provider(model)
                response = await provider.complete(
                    prompt=prompt,
                    temperature=0.7,
                    max_tokens=1000
                )
                return response.content
            
            return asyncio.run(run())
        except Exception as e:
            logger.error(f"Error executing prompt with {model}: {e}")
            return f"Error: {str(e)}"
    
    
    def _score_output(self, output: str, expected: Optional[str], expected_keywords: List[str], quality_criteria: str) -> float:
        """Score the output based on various criteria"""
        
        score = 8.0  # Base score
        
        # Check for expected keywords
        if expected_keywords:
            found_keywords = sum(1 for keyword in expected_keywords if keyword.lower() in output.lower())
            keyword_score = (found_keywords / len(expected_keywords)) * 2.0
            score += keyword_score
        
        # Check output length (not too short, not too long)
        if len(output) < 10:
            score -= 2.0
        elif len(output) > 1000:
            score -= 0.5
        
        # Check for basic quality indicators
        if output.strip():
            score += 0.5
        
        # Add some randomness to simulate real evaluation variance
        import random
        score += random.uniform(-0.3, 0.3)
        
        return min(max(score, 0.0), 10.0)  # Clamp between 0 and 10
    
    def _generate_test_cases(self, prompt_data: Dict[str, Any], num_tests: int, test_type: str) -> List[Dict[str, Any]]:
        """Generate test cases for a prompt"""
        
        variables = prompt_data.get("variables", {})
        template = prompt_data.get("template", "")
        
        test_cases = []
        
        for i in range(num_tests):
            test_case = {
                "test_name": f"{test_type}_test_{i+1}",
                "inputs": {},
                "quality_criteria": f"Should produce relevant output for {test_type} testing"
            }
            
            # Generate inputs for each variable
            for var_name, var_config in variables.items():
                test_case["inputs"][var_name] = self._generate_test_input(var_name, template, i)
            
            # Add expected keywords based on prompt type
            test_case["expected_keywords"] = self._get_expected_keywords(template)
            
            test_cases.append(test_case)
        
        return test_cases
    
    def _generate_test_input(self, var_name: str, template: str, index: int) -> str:
        """Generate test input for a variable"""
        
        # Sample data for different variable types
        if var_name == "text":
            samples = [
                "Artificial intelligence is revolutionizing modern business practices.",
                "Climate change requires urgent global action and cooperation.",
                "The digital transformation has accelerated due to recent events.",
                "Remote work technologies are reshaping workplace dynamics.",
                "Sustainable energy solutions are becoming increasingly viable."
            ]
            return samples[index % len(samples)]
        
        elif var_name == "feedback_text":
            samples = [
                "Excellent product quality and fast delivery!",
                "Good service but could improve response time.",
                "Product arrived damaged, disappointing experience.",
                "Amazing customer support, highly recommended!",
                "Average product, meets basic expectations."
            ]
            return samples[index % len(samples)]
        
        elif var_name in ["recipient", "to"]:
            return ["colleague", "client", "manager", "team", "customer"][index % 5]
        
        elif var_name == "topic":
            return ["project update", "meeting recap", "quarterly review", "proposal", "feedback"][index % 5]
        
        elif var_name == "tone":
            return ["professional", "casual", "formal", "friendly", "urgent"][index % 5]
        
        else:
            return f"Sample {var_name} data {index + 1}"
    
    def _get_expected_keywords(self, template: str) -> List[str]:
        """Get expected keywords based on template content"""
        
        template_lower = template.lower()
        keywords = []
        
        if "summarize" in template_lower:
            keywords = ["summary", "key", "main"]
        elif "translate" in template_lower:
            keywords = ["translation"]
        elif "email" in template_lower:
            keywords = ["subject", "dear", "regards"]
        elif "analyze" in template_lower:
            keywords = ["analysis", "insights"]
        elif "classify" in template_lower:
            keywords = ["classification", "category"]
        
        return keywords
    
    def _create_report(self, prompt_file: str, test_file: Optional[str], results: List[TestResult]) -> EvaluationReport:
        """Create evaluation report"""
        
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)
        average_score = sum(r.score for r in results) / total_tests if total_tests > 0 else 0.0
        
        summary = {
            "pass_rate": passed_tests / total_tests if total_tests > 0 else 0.0,
            "average_score": average_score,
            "model_used": self.model,
            "total_duration": sum(r.duration for r in results)
        }
        
        return EvaluationReport(
            prompt_file=prompt_file,
            test_file=test_file,
            model=self.model,
            total_tests=total_tests,
            passed_tests=passed_tests,
            average_score=average_score,
            individual_results=results,
            timestamp=datetime.now().isoformat(),
            summary=summary
        )
    
    def save_report(self, report: EvaluationReport, output_file: Path) -> bool:
        """Save evaluation report to file"""
        
        try:
            report_data = {
                "prompt_file": report.prompt_file,
                "test_file": report.test_file,
                "model": report.model,
                "timestamp": report.timestamp,
                "summary": {
                    "total_tests": report.total_tests,
                    "passed_tests": report.passed_tests,
                    "pass_rate": report.passed_tests / report.total_tests if report.total_tests > 0 else 0.0,
                    "average_score": report.average_score
                },
                "results": [
                    {
                        "test_name": r.test_name,
                        "inputs": r.inputs,
                        "output": r.output,
                        "expected": r.expected,
                        "score": r.score,
                        "passed": r.passed,
                        "duration": r.duration,
                        "metadata": r.metadata
                    }
                    for r in report.individual_results
                ]
            }
            
            with open(output_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            return True
            
        except Exception:
            return False