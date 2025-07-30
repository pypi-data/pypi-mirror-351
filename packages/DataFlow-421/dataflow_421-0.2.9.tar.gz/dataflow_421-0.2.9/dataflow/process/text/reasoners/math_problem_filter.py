"""
A filter class for evaluating mathematical problems using an API.
This class constructs prompts for mathematical problem evaluation,
sends them to the API, and returns a list of 0s and 1s indicating
whether each problem is correctly formatted and solvable.

Features:
- Constructs evaluation prompts with four progressive checks
- Handles API call failures gracefully
- Processes datasets in parallel for efficiency
- Returns results as a list of 0s and 1s

Usage:
1. Initialize the filter with appropriate parameters
2. Call filter_func with a dataset (list of JSONL lines)
3. Get results as a list of 0s and 1s
"""

from dataflow.utils.api_utils import api_chat
from dataflow.data import TextDataset
import json
import time
import re
from dataflow.core import ReasonerFilter
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from dataflow.utils.registry import PROCESSOR_REGISTRY
import logging
from datasets import Dataset
from dataflow.utils.utils import get_logger

@PROCESSOR_REGISTRY.register()
class MathProblemFilter(ReasonerFilter):
    def __init__(self, args_dict: dict):
        super().__init__(args_dict)
        self.system_prompt = args_dict.get("system_prompt", 
            "You are an expert in evaluating mathematical problems. Follow the user's instructions strictly and output your final judgment in the required JSON format."
        )
        # need to set api_key first
        self.model = self.model_name
        self.api_key = args_dict.get("api_key", "")
        self.api_url = args_dict.get("api_url", "")
        self.filter_name = 'MathProblemFilter'
        self.logger = get_logger()
        self.eval_stage = args_dict.get("eval_stage",0)
        self.dataset = self._load_input()
        
    def _load_input(self):
        self.logger.info(f"self.input_key={self.input_key}")
        if self.storage is not None:
            value_list = self.storage.read_code_json(
                [self.input_key], stage=self.eval_stage, format='SFT_Single', syn='syn_q'
            )
            value_list = [        
                {**item['data'], 'id': str(item['id'])}
                for item in value_list
            ]
            self.logger.info(f"===value_list={value_list}")
            
            dataset = Dataset.from_list(value_list)
            self.logger.info(f"===dataset={dataset}")
            
            return TextDataset(
                dataset=dataset,
                keys=value_list[0].keys(),
                metadata=None 
            )
        else:
            raise ValueError("No storage or input file provided")
        
    def _write_output(self, labels, ids):
        if self.storage is not None:
            output_rows = []
            for _, label in zip(ids, labels):
                output_rows.append({
                    self.result_key: label,
                    'id': _
                })
            self.storage.write_eval(output_rows, algo_name=self.filter_name, score_key=self.result_key)
        else:
            raise ValueError("No storage or output file provided")
    



    def build_prompt(self, question):
        """Constructs an evaluation prompt with four progressive checks"""
        prompt = f"""You are given a mathematical problem. Follow these four steps in order and stop at the first failure:
0. Firstly check if it is only a math problem, if it has other instruction confused the model such as "rewrite" or has answer or other strange instruction, then judged as failure. If it is not a math problem, then the judgement_test is false.
1. Check only for spelling, grammar, and LaTeX formatting correctness. Do not interpret semantic meaning.
2. For each minimal condition stated in the problem (that cannot be further decomposed), check if it violates the mathematical domain or objective facts (for example, 'half a person' is incorrect). Note: Magical operations are acceptable if the necessary assumption is explicitly stated. Average values (e.g., 15.5 items per minute) are acceptable.
3. Check whether the problem-solving process contains any contradictions. This includes any two minimal conditions contradicting each other or if the final solution would be unreasonable (including unsolvable).
4. If the steps above pass, check if there are enough conditions provided in the problem to answer the target question. Redundant conditions that do not affect the problem - solving process are considered reasonable. Both analytical and numerical solutions are considered valid unless otherwise specified.
    
After performing these steps in sequence, output your final judgment in JSON format with exactly the following keys:
{{
    "judgement_test": true/false,
    "error_type": "<error description or null>"
}}
You may include your chain-of-thought, but the final answer must be the JSON object above.
    
Here is the problem to evaluate:
-------------------------------
{question}
-------------------------------
"""
        return prompt

    def process_problem(self, problem):
        """Processes a single problem by calling the API"""
        full_prompt = self.build_prompt(problem)
        try:
            response = api_chat(
                system_info=self.system_prompt,
                messages=full_prompt,
                model=self.model,
                api_url=self.api_url,
                api_key=self.api_key
            )
        except Exception as e:
            # API call failed, return 0
            self.logger.error(f"API call failed for problem: {problem}. Error: {e}")
            return 0
        else:
            try:
                if response is None:
                    self.logger.error(f"Empty response for problem: {problem}")
                    return 0
                pattern = re.compile(r'"judgement_test"\s*:\s*(true|false)', re.IGNORECASE)
                match = pattern.search(response)
                test_value = None

                if match:
                    test_value = match.group(1).lower()
                else:
                    if "true" in response.lower():
                        test_value = "true"
                return 1 if test_value == 'true' else 0
            except Exception as e:
                # Response format error, return 0
                self.logger.error(f"Response format error for problem: {problem}. Error: {e}")
                return 0

    def filter_func(self, dataset):
        """Main filtering function that processes the entire dataset and returns a list of 0s and 1s"""
        max_workers = self.max_worker  # Adjust based on your needs

        dataset = dataset.to_list()

        results = [None] * len(dataset)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {}
            for idx, record in enumerate(dataset):
                try:
                    problem = record.get(self.input_question_key, "")
                    if not isinstance(problem, str) or not problem.strip():
                        self.logger.info(f"Empty problem found in record at index {idx}: {record}")
                        results[idx] = 0
                        continue
                    future = executor.submit(self.process_problem, problem)
                    future_to_index[future] = idx
                except json.JSONDecodeError:
                    self.logger.error(f"Invalid JSON format in record at index {idx}: {record}")
                    results[idx] = 0

            for future in tqdm(as_completed(future_to_index), total=len(future_to_index), desc="Processing"):
                idx = future_to_index[future]
                try:
                    result = future.result()
                except Exception as e:
                    self.logger.error(f"Error processing problem at index {idx}: {e}")
                    result = 0
                results[idx] = result
                time.sleep(0.1)

        return results

    def handle_api_error(self, error_message):
        """Handles API errors and provides guidance"""
        self.logger.error(f"API Error: {error_message}")
        self.logger.error("Possible reasons:")
        self.logger.error("1. Network connection issue. Please check your internet connection.")
        self.logger.error("2. Invalid API URL. Please verify the URL format and accessibility.")
        self.logger.error("3. API service unavailable. Please check if the service is running properly.")
        self.logger.error("4. API key issue. Please ensure your API key is valid and has proper permissions.")
        self.logger.error("Suggestion: Try again after checking the above issues.")