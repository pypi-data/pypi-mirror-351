import random
import os
import pandas as pd
try:
    from utils import  APIGenerator_aisuite, APIGenerator_request
    from utils.Prompts import QuestionSynthesisPrompt
except ImportError:
    from dataflow.generator.utils import  APIGenerator_aisuite, APIGenerator_request
    from dataflow.generator.utils.Prompts import QuestionSynthesisPrompt
from dataflow.utils.registry import GENERATOR_REGISTRY
import logging
from dataflow.utils.utils import get_logger
from dataflow.data import MyScaleStorage, DatabaseConfig

@GENERATOR_REGISTRY.register()
class QuestionGenerator():
    def __init__(self, args):
        """
        Initialize the QuestionGenerator with the provided configuration.
        """
        self.config = args
        self.prompts = QuestionSynthesisPrompt()
        self.logger = get_logger()

        # Determine if database storage is used
        use_db = args.get("use_db", False) or os.environ.get("USE_DB", "").lower() == "true"
        self.use_db = use_db # Store the use_db flag
        self.logger.info(f"+++self.use_db: {self.use_db}")

        if self.use_db:
            # Ensure the necessary configuration keys are provided
            db_config = DatabaseConfig(
                host=os.environ.get('MYSCALE_HOST', 'localhost'),
                port=int(os.environ.get('MYSCALE_PORT', '9000')),
                db_name=os.environ.get('MYSCALE_DATABASE', 'dataflow'),
                table_name=os.environ.get('MYSCALE_TABLE_NAME', ''),
                username=os.environ.get('MYSCALE_USER', ''),
                password=os.environ.get('MYSCALE_PASSWORD', '')
            )
            self.logger.info(f"+++db_config: {db_config}")
            self.storage = MyScaleStorage(db_config)
            self.input_file = None # Explicitly set to None
            self.output_file = None # Explicitly set to None
            self.stage = args.get("stage",0)
            self.pipeline_id = args.get("pipeline_id","")
        else:
            self.storage = None # Explicitly set to None
            self.input_file = args.get("input_file")
            self.output_file = args.get("output_file")

        self.input_key = self.config.get("input_key", "data")
        self.read_key = self.config.get("read_key", "question")  # default key for question input
        self.num_prompts = self.config.get("num_prompts", 1)  # default number of prompts to use for generation
        self.read_min_score = self.config.get('read_min_score', 0.9)
        self.read_max_score = self.config.get('read_max_score', 2.0)
        self.eval_stage = self.config.get('eval_stage',1)
        # check if num_prompts is a valid number
        if self.num_prompts not in [0,1,2,3,4,5]:
            raise ValueError("num_prompts must be 0, 1, 2, 3, 4, or 5")

        # Validate that input_file and output_file are provided ONLY if not using DB
        if not self.use_db and (not self.input_file or not self.output_file):
            raise ValueError("When not using the database, both input_file and output_file must be specified in the config.")

        # Provide default api_key and api_url for API generators if not provided
        if not self.config.get("api_key"):
            self.config["api_key"] = "sk-4ozjn4y65yweedak"
            self.logger.info("Using default api_key")
        if not self.config.get("api_url"):
            self.config["api_url"] = "https://cloud.infini-ai.com/AIStudio/inference/api/if-dbbaas222qv6yiwm/v1/chat/completions"
            self.logger.info("Using default api_url")
        if not self.config.get("max_workers"):
            self.config["max_workers"] = 3
            self.logger.info("Using default max_workers = 3")

        self.model = self.__init_model__()

    @staticmethod
    def get_desc(lang):
        return "基于现有的问题数据，每个问题合成1-5个新问题" if lang == "zh" else "en"

    def __init_model__(self):
        """
        Initialize the model generator based on the configuration.
        """
        # generator_type = self.config.get("generator_type", "local").lower()
        generator_type = "request"

        # if generator_type == "local":
        #     return LocalModelGenerator(self.config)
        if generator_type == "aisuite":
            return APIGenerator_aisuite(self.config)
        elif generator_type == "request":
            return APIGenerator_request(self.config)
        else:
            raise ValueError(f"Invalid generator type: {generator_type}")

    def _reformat_prompt(self, dataframe):
        """
        Reformat the prompts in the dataframe to generate questions based on num_prompts.
        """
        # Check if read_key is in the dataframe
        if self.read_key not in dataframe.columns:
            key_list = dataframe.columns.tolist()
            raise ValueError(f"read_key: {self.read_key} not found in the dataframe. Available keys: {key_list}")

        # Predefined transformation options for diversity
        diversity_mode = [
            "1, 2, 3",
            "1, 2, 4",
            "1, 2, 5",
            "1, 4, 5",
            "1, 2, 3, 4, 5"
        ]

        formatted_prompts = []
        for question in dataframe[self.read_key]:
            if self.num_prompts == 0:
                formatted_prompts.append("")  # Skip generating for this question
            else:
                # Randomly choose the required number of transformations from diversity_mode
                selected_items = random.sample(diversity_mode, self.num_prompts)
                for selected_item in selected_items:
                    used_prompt = self.prompts.question_synthesis_prompt(selected_item, question)
                    formatted_prompts.append(used_prompt.strip())

        return formatted_prompts

    def _load_input(self):
        if hasattr(self, 'storage'):
            value_list = self.storage.read_json(
                [self.input_key], eval_stage=self.eval_stage, format='SFT_Single', syn='syn_q', maxmin_scores=[{'min_score': self.read_min_score, 'max_score': self.read_max_score},], stage=self.stage, pipeline_id=self.pipeline_id, category="reasoning"
            )
            # print(value_list)
            return pd.DataFrame([
                {**item['data'], 'id': str(item['id'])}
                for item in value_list
            ])
            # return pd.DataFrame([item['data'] for item in value_list])
        else:
            return pd.read_json(self.input_file, lines=True)

    def _write_output(self, save_path, dataframe, extractions):
        if hasattr(self, 'storage'):
            output_rows = dataframe.where(pd.notnull(dataframe), None).to_dict(orient="records")
            formatted_rows = [
                {
                    "id": row["id"],
                    "data": {k: v for k, v in row.items() if k != "id"}
                }
                for row in output_rows
            ]
            self.storage.write_json(formatted_rows, format="SFT_Single", syn="syn_q", stage=self.stage+1, pipeline_id=self.pipeline_id, category="reasoning")
        else:
            output_dir = os.path.dirname(self.output_file)
            os.makedirs(output_dir, exist_ok=True)
            dataframe.to_json(save_path, orient="records", lines=True)

    def run(self):
        """
        Run the question generation process.
        """
        try:
            
            # Read the input file (jsonl format only)
            # dataframe = pd.read_json(self.input_file, lines=True)
            dataframe = self._load_input()
            if self.read_key not in dataframe.columns:
                raise ValueError(f"read_key: {self.read_key} not found in the dataframe. Available keys: {dataframe.columns.tolist()}")
            if "Synth_or_Input" in dataframe.columns:
                raise ValueError(f"Synth_or_Input is a reserved column name to show if the question is generated or not, please rename it")
            
            if self.num_prompts == 0:
                raise ValueError(f"num_prompts should not be 0.")
                # self.logger.info(f"num_prompts is 0, skip generation")
                # # dataframe.to_json(self.output_file, orient="records", lines=True, force_ascii=False)
                # if hasattr(self, 'storage'):
                #     self._write_output(self.output_file, dataframe, None)
                # self.logger.info(f"Generated questions saved to {self.output_file}")
                # return

            # Reformat the prompts for question generation
            formatted_prompts = self._reformat_prompt(dataframe)

            # Generate responses using the model
            responses = self.model.generate_text_from_input(formatted_prompts)

            # 将新生成的问题作为新的行添加到dataframe中，仍然填写到read_key中,这些行的其他列全部为空
            # new_rows = pd.DataFrame(columns=dataframe.columns)
            # new_rows[self.read_key] = responses
            repeat_count = self.num_prompts  # 每个seed生成几个
            expected_total = len(dataframe) * repeat_count

            if len(responses) != expected_total:
                raise ValueError(f"Expected {expected_total} responses (len(dataframe)={len(dataframe)} * {repeat_count}), but got {len(responses)}")

            # 展开原始id
            expanded_ids = [id_ for id_ in dataframe["id"].tolist() for _ in range(repeat_count)]

            # 构建新生成的行
            new_rows = pd.DataFrame({
                "id": expanded_ids,
                self.read_key: responses,
            })
            
            # if hasattr(self, 'storage'):
            #     self._write_output(self.output_file, new_rows, None)
            #     return 0
            
            new_rows["Synth_or_Input"] = "synth"
            dataframe["Synth_or_Input"] = "input"
            
            dataframe = pd.concat([dataframe, new_rows], ignore_index=True) # ignore_index=True 表示忽略原来的索引
        
            # Ensure output directory exists
            # output_dir = os.path.dirname(self.output_file)
            # os.makedirs(output_dir, exist_ok=True)

            # Save DataFrame to JSON file
            # 过滤self.read_key为空的数据
            dataframe = dataframe[dataframe[self.read_key].notna()]
            dataframe = dataframe[dataframe[self.read_key] != ""]
            # dataframe.to_json(self.output_file, orient="records", lines=True, force_ascii=False)
            self._write_output(self.output_file, dataframe, None)

            self.logger.info(f"Generated questions saved to {self.output_file}")

        except Exception as e:
            self.logger.error(f"[错误] 处理过程中发生异常: {e}")

    @staticmethod
    def get_desc(lang):
        if lang == "zh":
            return (
                "该算子用于基于种子问题生成多样化的问题变体。"
                "通过多种语义转换方式扩展问题数据集。\n\n"
                "输入参数：\n"
                "- num_prompts：生成变体数量（0-5）\n"
                "- input_key：输入数据键名\n"
                "- 其他存储/模型参数同前\n\n"
                "输出参数：\n"
                "- Synth_or_Input：标识生成或原始问题\n"
                "- 生成的问题存储于指定字段"
            )
        elif lang == "en":
            return (
                "Generates diverse question variations from seed questions "
                "using multiple semantic transformation methods.\n\n"
                "Input Parameters:\n"
                "- num_prompts: Number of variations to generate (0-5)\n"
                "- input_key: Key for input data\n"
                "- Other storage/model params as previous\n\n"
                "Output Parameters:\n"
                "- Synth_or_Input: Marks generated vs original questions\n"
                "- Generated questions in specified field"
            )
