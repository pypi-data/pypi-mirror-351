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
        self.filter_name = 'MathProblemFilter'
        self.logger = get_logger()
        self.eval_stage = args_dict.get("eval_stage",0)
        self.dataset = self._load_input()
        
    def _load_input(self):
        self.logger.info(f"1.=========+++++======self.input_key={self.input_key}")
        if self.storage is not None:
            value_list = self.storage.read_code_json(
                [self.input_key], stage=self.eval_stage, format='SFT_Single', syn='syn_q'
            )
            self.logger.info(f"2.=========+++++======value_list={value_list}")
            value_list = [        
                {**item['data'], 'id': str(item['id'])}
                for item in value_list
            ]
            
            self.logger.info(f"3.=========+++++======value_list={value_list}")
            
            dataset = Dataset.from_list(value_list)
            self.logger.info(f"4.=========+++++======dataset={dataset}")
            
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
1. Check only for spelling, grammar, and LaTeX formatting correctness. Do not interpret semantic meaning.
2. For each minimal condition stated in the problem (that cannot be further decomposed), check if it violates the mathematical domain or objective facts (for example, 'half a person' is incorrect). Note: Magical operations are acceptable if the necessary assumption is explicitly stated. Average values (e.g., 15.5 items per minute) are acceptable.
3. Check whether the problem-solving process contains any contradictions. This includes any two minimal conditions contradicting each other or if the final solution would be unreasonable (including unsolvable).
4. If steps 1-3 pass, check whether the problem is fully solvable by verifying that all necessary conditions to answer the question are provided. This check should be based solely on the question.
    
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
            self.logger.info(f"math_problem_filter ----> self.api_url = {self.api_url}")
            self.logger.info(f"math_problem_filter ----> self.api_key = {self.api_key}")
            response = api_chat(
                system_info=self.system_prompt,
                messages=full_prompt,
                model=self.model,
                api_url=self.api_url,
                api_key=self.api_key
            )
            self.logger.info(f"math_problem_filter ----> response: {response}")
        except Exception as e:
            # API call failed, return 0
            self.logger.error(f"API call failed for problem: {problem}. Error: {e}")
            return 0
        else:
            try:
                pattern = re.compile(r'"judgement_test"\s*:\s*(true|false)', re.IGNORECASE)
                match = pattern.search(response)
                # print("---match---",match)
                test_value = None
                if match:
                    test_value = match.group(1).lower()
                return 1 if test_value == 'true' else 0
            except Exception as e:
                # Response format error, return 0
                self.logger.error(f"Response format error for problem: {problem}. Error: {e}")
                return 0

    def filter_func(self, dataset):
        """Main filtering function that processes the entire dataset and returns a list of 0s and 1s"""
        results = []
        max_workers = self.max_worker  # Adjust based on your needs

        # 处理不同类型的数据集输入
        if hasattr(dataset, 'to_list'):
            dataset = dataset.to_list()
        elif isinstance(dataset, dict):
            # 如果是字典类型，直接使用
            dataset = [dataset]
        elif not isinstance(dataset, list):
            # 如果既不是可调用to_list的对象，也不是字典或列表，则转换为列表
            dataset = list(dataset)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for record in dataset:
                try:
                    problem = record.get(self.input_question_key, "")
                    if problem:
                        futures.append(executor.submit(self.process_problem, problem))
                except json.JSONDecodeError:
                    self.logger.error(f"Invalid JSON format in record")
                    results.append(0)
                except Exception as e:
                    self.logger.error(f"Error processing record: {e}")
                    results.append(0)

            for future in tqdm(as_completed(futures), total=len(futures), desc="Processing"):
                result = future.result()
                results.append(result)
                # Add slight delay
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