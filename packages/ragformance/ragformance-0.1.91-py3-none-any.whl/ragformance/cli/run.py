"""
RAGformance End-to-End Runner

This module allows you to run the full pipeline for question generation, upload, evaluation, metrics computation, and visualization
for RAG datasets, either from the command line or as a Python library.
Each step is controlled by flags in the JSON configuration file.

CLI usage:
    ragformance --config config.json
"""

import os
import json
import logging
import argparse
from typing import List, Dict, Any
import importlib
from ragformance.models.corpus import DocModel
from ragformance.models.answer import AnnotatedQueryModel
from pydantic import TypeAdapter, ValidationError

# Import RAG config models
from ragformance.rag.config import (
    NaiveRagConfig,
    OpenWebUIRagConfig,
    HaystackRagConfig,
    MultiEmbeddingLLMRagConfig,
)


# load config file
def load_config(config_path):
    with open(config_path) as f:
        config = json.load(f)
    return config


# set up logging
def setup_logging(log_path):
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logging.info("Logging setup complete.")


def run_pipeline(config_path="config.json"):
    """
    Run the full or partial pipeline according to the steps enabled in the config.
    """
    config = load_config(config_path)
    log_path = config["log_path"]
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    setup_logging(log_path + "/ragformance.log")

    steps = config.get("steps", {})
    model_path = config["model_path"]
    log_path = config["log_path"]

    corpus: List[DocModel] = []
    queries: List[AnnotatedQueryModel] = []
    # answers: List[AnswerModel] = []

    ta = TypeAdapter(List[DocModel])
    taq = TypeAdapter(List[AnnotatedQueryModel])

    # TODO : optionaly start a local LLM server, update config

    # Question generation
    if steps.get("generation", True):
        logging.info("[STEP] Question generation.")
        generator = config.get("generation", {})
        generator_type = generator.get("type", None)
        data_path = generator.get("source", {}).get("path", None)
        output_path = generator.get("output", {}).get("path", None)

        llms = config.get("LLMs", None)
        if llms is None:  # This llms block is for default API key, model, url
            logging.warning(
                "LLMs section not found in config. Some generators might require it."
            )
            default_api_key = None
            default_model_name = None
            default_base_url = None
        else:
            default_api_key = llms[0].get("api_key", None)
            default_model_name = llms[0].get("model", None)
            default_base_url = llms[0].get("base_url", None)

        generator_class_map = {
            "alpha": "ragformance.generators.alpha.AlphaGenerator",
            "aida": "ragformance.generators.aida.AidaGenerator",
            "based_llm_and_summary": "ragformance.generators.based_llm_and_summary.BasedLLMSummaryGenerator",
            "error_code": "ragformance.generators.error_code.ErrorCodeGenerator",
            "llm_prompt": "ragformance.generators.llm_prompt.LLMPromptGenerator",
            "mic": "ragformance.generators.mic.MicGenerator",
            "ragas": "ragformance.generators.ragas.RagasGenerator",
            "structural_generator": "ragformance.generators.structural_generator.StructuralGenerator",
            "tokenburner": "ragformance.generators.tokenburner.TokenBurnerGenerator",
            "tokenburner_gpt_2": "ragformance.generators.tokenburner_gpt_2.TokenBurnerGPT2Generator",
        }

        gen_run_config: Dict[str, Any] = {
            "data_path": data_path,  # For generators that take a single data_path
            "output_path": output_path,
            "llm_api_key": default_api_key,
            "llm_base_url": default_base_url,
            "llm_model_name": default_model_name,
        }

        # Update with general params from config.generation.params
        # These might override some defaults set above if keys are the same
        # (e.g. if llm_api_key is also in params)
        if "params" in generator:  # generator here is config.get("generation", {})
            gen_run_config.update(generator.get("params", {}))

        # Handle specific configurations
        if generator_type == "aida":
            # AIDA specific config can be under a top-level "aida_generator_config"
            # or directly within generation.params if preferred.
            # Assuming aida_generator_config for clarity as per plan.
            aida_specific_params = config.get("aida_generator_config", {})
            gen_run_config.update(
                aida_specific_params
            )  # Merge/override with AIDA specific params

            # Ensure required AIDA params are set, potentially from other parts of the main config
            # These names must match what AidaGenerator expects in its config dict.
            if (
                "seed_questions_path" not in gen_run_config
            ):  # Example if it's not in aida_specific_params
                gen_run_config["seed_questions_path"] = os.path.join(
                    data_path, "seed_questions.json"
                )  # Default logic
            if (
                "data_dir" not in gen_run_config
            ):  # AIDA's run method expects 'data_dir' for PDFs
                gen_run_config["data_dir"] = data_path
            if (
                "capella_xml_path" not in gen_run_config
            ):  # AIDA expects 'capella_xml_path'
                gen_run_config["capella_xml_path"] = os.path.join(
                    data_path, "data.capella"
                )  # Default logic

            if len(llms) > 1 and "entity_model_name" not in gen_run_config:
                gen_run_config["entity_model_name"] = llms[1].get(
                    "model", default_model_name
                )
            else:  # Fallback if not enough LLMs or already set
                gen_run_config.setdefault("entity_model_name", default_model_name)

            # qa_model_name for AIDA will use the primary default_model_name unless overridden by aida_specific_params
            gen_run_config.setdefault("qa_model_name", default_model_name)

            embeddings_list = config.get("embeddings", [{}])
            if embeddings_list and "hf_embed_model" not in gen_run_config:
                gen_run_config["hf_embed_model"] = embeddings_list[0].get("model")

        elif generator_type == "ragas":
            ragas_specific_params = config.get("ragas_generator_config", {})
            gen_run_config.update(ragas_specific_params)

            if (
                "llm_config" not in gen_run_config
            ):  # RagasGenerator expects "llm_config"
                gen_run_config["llm_config"] = llms[0] if llms else {}

            if (
                "embedding_config" not in gen_run_config
            ):  # RagasGenerator expects "embedding_config"
                gen_run_config["embedding_config"] = (
                    config.get("embeddings", [{}])[0]
                    if config.get("embeddings")
                    else {}
                )

            critique_llm_index = ragas_specific_params.get("critique_llm_index")
            if (
                critique_llm_index is not None
                and llms
                and 0 <= critique_llm_index < len(llms)
            ):
                gen_run_config["critique_llm_config"] = llms[critique_llm_index]
            elif (
                "critique_llm_config" not in gen_run_config
            ):  # Default to primary LLM if no index or invalid
                gen_run_config["critique_llm_config"] = gen_run_config["llm_config"]

            # "question_distribution" should be part of ragas_generator_config or general params
            # "n_questions" should be part of ragas_generator_config or general params

        if generator_type in generator_class_map:
            module_path, class_name = generator_class_map[generator_type].rsplit(".", 1)
            try:
                module = importlib.import_module(module_path)
                GeneratorClass = getattr(module, class_name)
                generator_instance = GeneratorClass()

                # Ensure all paths needed by specific generators are correctly mapped
                # Example: some generators expect 'data_file_name' or 'data_folder_path'
                # These should be set in config.generation.params or handled here.
                # For structural_generator:
                if (
                    generator_type == "structural_generator"
                    and "data_folder_path" not in gen_run_config
                ):
                    gen_run_config["data_folder_path"] = (
                        data_path  # Assuming data_path is the folder
                    )
                    # "data_file_name" should be in params for structural_generator

                # For tokenburner_gpt_2:
                if (
                    generator_type == "tokenburner_gpt_2"
                    and "pdf_path" not in gen_run_config
                ):
                    # Assuming data_path from config.generation.source.path IS the pdf_path for this one.
                    # Or it needs to be specified in params for this generator.
                    gen_run_config["pdf_path"] = data_path

                corpus, queries = generator_instance.run(gen_run_config)
                logging.info(f"Data generation complete using {generator_type}.")
            except Exception as e:
                logging.error(f"Error during generation with {generator_type}: {e}")
                raise
        else:
            logging.error(f"Unknown or unsupported generator type: {generator_type}")
            raise ValueError(f"Unknown or unsupported generator type: {generator_type}")

    # Upload to HuggingFace
    if steps.get("upload_hf", False):
        logging.info("[STEP] HuggingFace upload.")
        from ragformance.dataloaders import push_to_hub

        hf_path = config.get("hf", {}).get("hf_path", None)
        data_path = config.get("generation", {}).get("output", {}).get("path", None)
        hf_token = config.get("hf", {}).get("hf_token", None)
        if hf_path and data_path:
            push_to_hub(
                hf_path, data_path, hf_token
            )  # Note : we could wrap other parameters from config, but we focus on the main ones to have uniform pipelines
            logging.info("[UPLOAD] Upload complete.")
        else:
            logging.info("[UPLOAD] hf.hf_path or generation.output.path not set.")

    # Load dataset from source
    if steps.get("load_dataset", False):
        logging.info("[STEP] Loading dataset from source enabled.")
        if len(corpus) > 0 or len(queries) > 0:
            logging.warning(
                "[Warning] Dataset already loaded from generation. Loading will replace the current dataset."
            )

        source_type = config.get("dataset", {}).get("source_type", "jsonl")
        source_path = config.get("dataset", {}).get("path", "")

        if source_type == "jsonl":
            with open(os.path.join(source_path, "corpus.jsonl")) as f:
                corpus = ta.validate_python([json.loads(line) for line in f])
            with open(os.path.join(source_path, "queries.jsonl")) as f:
                queries = taq.validate_python([json.loads(line) for line in f])

        elif source_type == "huggingface":
            from datasets import load_dataset

            corpus = ta.validate_python(
                load_dataset(source_path, "corpus", split="train")
            )
            queries = taq.validate_python(
                load_dataset(source_path, "queries", split="train")
            )
        elif source_type == "beir":
            from ragformance.dataloaders import load_beir_dataset

            corpus, queries = load_beir_dataset(dataset=source_path)

    # RAG evaluation
    if steps.get("evaluation", True):
        logging.info("[STEP] RAG evaluation enabled.")
        run_pipeline_evaluation(config)

    # Metrics computation
    if steps.get("metrics", True):
        logging.info("[STEP] Metrics computation enabled.")
        compute_metrics(config)

    # Visualization
    if steps.get("visualization", True):
        logging.info("[STEP] Visualization enabled.")
        run_visualization(config)

    # Save status
    results_path = os.path.join(model_path, "results.json")
    with open(results_path, "w") as f:
        json.dump({"status": "success"}, f)
    logging.info("Results saved.")


def main():
    parser = argparse.ArgumentParser(description="RAGformance End-to-End Runner")
    parser.add_argument(
        "--config", type=str, required=True, help="Path to config JSON file"
    )
    args = parser.parse_args()

    run_pipeline(args.config)


def get_rag_class(
    main_config: Dict[str, Any],
):  # Renamed config to main_config for clarity
    rag_type = main_config.get("rag_type", "naive")
    # rag_specific_config_dict = main_config.get(
    #    f"{rag_type}_rag_config", {}
    # )  # e.g., naive_rag_config

    rag_params_key = f"{rag_type}_rag_params"  # e.g. "naive_rag_params"

    # Fallback to a general "rag_params" if specific not found, then to root of main_config
    if rag_params_key in main_config:
        params_for_rag_config = main_config[rag_params_key]
    elif "rag_params" in main_config:
        params_for_rag_config = main_config["rag_params"]
    else:  # Try to use top-level keys from main_config.
        params_for_rag_config = main_config

    # Ensure all keys in params_for_rag_config are UPPER_CASE
    # Pydantic model_validate expects a dict.
    upper_case_params = {k.upper(): v for k, v in params_for_rag_config.items()}

    try:
        if rag_type == "naive":
            from ragformance.rag.naive_rag import NaiveRag

            # Ensure all required fields for NaiveRagConfig are in upper_case_params
            # or have defaults.
            pydantic_config = NaiveRagConfig(**upper_case_params)
            return NaiveRag(config=pydantic_config)
        elif rag_type == "openwebui":
            from ragformance.rag.openwebui_rag import OpenwebuiRag

            pydantic_config = OpenWebUIRagConfig(**upper_case_params)
            return OpenwebuiRag(config=pydantic_config)
        elif rag_type == "haystack":  # Added Haystack
            from ragformance.rag.haystack_rag import HaystackRAG

            pydantic_config = HaystackRagConfig(**upper_case_params)
            return HaystackRAG(config=pydantic_config)
        elif rag_type == "multi_embedding_llm":  # Added MultiEmbeddingLLM
            from ragformance.rag.multi_embedding_llm import MultiEmbeddingLLM

            # MultiEmbeddingLLM typically loads from its own JSON.
            # If multi_rag_configuration_path is in main_config:
            multi_config_path = main_config.get(
                "multi_embedding_llm_config_path",
                "ragformance/rag/config/multi_rag_configuration.json",
            )
            if os.path.exists(multi_config_path):
                with open(multi_config_path) as f:
                    json_data = json.load(f)
                # Transform keys to UPPER_CASE for Pydantic model
                upper_case_json_data = {k.upper(): v for k, v in json_data.items()}
                pydantic_config = MultiEmbeddingLLMRagConfig(**upper_case_json_data)
            else:
                # Fallback to params from main config if file not found or path not specified
                logging.warning(
                    f"MultiEmbeddingLLM config file not found at {multi_config_path}. Trying to use params from main config."
                )
                pydantic_config = MultiEmbeddingLLMRagConfig(
                    **upper_case_params
                )  # Uses general params
            return MultiEmbeddingLLM(config=pydantic_config)
        else:
            raise ValueError(f"Unknown rag_type: {rag_type}")
    except ValidationError as e:
        logging.error(f"Configuration validation error for {rag_type}: {e}")
        raise  # Re-raise the validation error to stop execution if config is bad


def run_pipeline_evaluation(main_config: Dict[str, Any]):
    logging.info("[EVALUATION] Starting RAG evaluation...")
    rag = get_rag_class(main_config)
    from ragformance.models.corpus import DocModel
    from ragformance.models.answer import AnnotatedQueryModel
    import pandas as pd

    # data_path should ideally be part of a general section in main_config
    data_path = main_config.get("data_path", "data/")  # Default if not specified
    corpus_path = os.path.join(data_path, "corpus.jsonl")
    queries_path = os.path.join(data_path, "queries.jsonl")

    if not os.path.exists(corpus_path) or not os.path.exists(queries_path):
        logging.error(
            f"Corpus or queries file not found in {data_path}. Skipping evaluation."
        )
        return

    corpus = [
        DocModel(**d)
        for d in pd.read_json(corpus_path, lines=True).to_dict(orient="records")
    ]
    queries = [
        AnnotatedQueryModel(**q)
        for q in pd.read_json(queries_path, lines=True).to_dict(orient="records")
    ]

    rag.upload_corpus(corpus)
    rag.ask_queries(queries)
    logging.info("[EVALUATION] RAG evaluation complete.")


def compute_metrics(config):
    logging.info("[METRICS] Computing metrics...")
    from ragformance.eval.metrics import evaluate

    data_path = config["data_path"]
    model_path = config["model_path"]
    evaluate(data_path, model_path)
    logging.info("[METRICS] Metrics computation complete.")


def run_visualization(config):
    logging.info("[VISUALIZATION] Generating visualizations...")

    logging.info("[VISUALIZATION] Visualization complete.")


if __name__ == "__main__":
    main()
