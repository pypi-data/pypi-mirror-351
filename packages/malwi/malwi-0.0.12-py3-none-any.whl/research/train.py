import torch
import shutil
import pathlib
import argparse
import numpy as np
import pandas as pd
import os
import json

from typing import Set
from pathlib import Path
from tokenizers import ByteLevelBPETokenizer, Tokenizer
from tokenizers.models import BPE
from tokenizers.normalizers import NFKC, Sequence, Lowercase
from tokenizers.pre_tokenizers import ByteLevel
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

from transformers import (
    DistilBertConfig,
    DistilBertForSequenceClassification,
    PreTrainedTokenizerFast,
    Trainer,
    TrainingArguments,
)

from datasets import Dataset, DatasetDict
from datasets.utils.logging import disable_progress_bar

from common.files import read_json_from_file

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent

SPECIAL_TOKENS: Set[str] = read_json_from_file(
    SCRIPT_DIR / "syntax_mapping" / "special_tokens.json"
)

DEFAULT_MODEL_NAME = "distilbert-base-uncased"
DEFAULT_TOKENIZER_CLI_PATH = Path("malwi_models")
DEFAULT_MODEL_OUTPUT_CLI_PATH = Path("malwi_models")
DEFAULT_MAX_LENGTH = 512
DEFAULT_EPOCHS = 3
DEFAULT_BATCH_SIZE = 16
DEFAULT_VOCAB_SIZE = 30522
DEFAULT_SAVE_STEPS = 0
DEFAULT_BENIGN_TO_MALICIOUS_RATIO = 7.0
DEFAULT_NUM_PROC = (
    os.cpu_count() if os.cpu_count() is not None and os.cpu_count() > 1 else 2
)


def load_asts_from_csv(
    csv_file_path: str, ast_column_name: str = "tokens"
) -> list[str]:
    asts = []
    try:
        df = pd.read_csv(csv_file_path)
        if ast_column_name not in df.columns:
            print(
                f"Warning: Column '{ast_column_name}' not found in {csv_file_path}. Returning empty list."
            )
            return []

        for idx, row in df.iterrows():
            ast_data = row[ast_column_name]
            if (
                pd.isna(ast_data)
                or not isinstance(ast_data, str)
                or not ast_data.strip()
            ):
                continue
            asts.append(ast_data.strip())
        print(f"Loaded {len(asts)} AST strings from {csv_file_path}")
    except FileNotFoundError:
        print(f"Error: File not found at {csv_file_path}. Returning empty list.")
        return []
    except Exception as e:
        print(f"Error reading CSV {csv_file_path}: {e}. Returning empty list.")
        return []
    return asts


def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, average="binary", zero_division=0
    )
    acc = accuracy_score(labels, preds)
    return {"accuracy": acc, "f1": f1, "precision": precision, "recall": recall}


def create_or_load_tokenizer(
    tokenizer_output_path: Path,
    texts_for_training: list[str],
    vocab_size: int,
    global_special_tokens: Set[str],
    max_length: int,
    force_retrain: bool,
):
    huggingface_tokenizer_config_file = tokenizer_output_path / "tokenizer.json"

    if not force_retrain and huggingface_tokenizer_config_file.exists():
        print(
            f"\nLoading existing PreTrainedTokenizerFast from {tokenizer_output_path} (found tokenizer.json)."
        )
        tokenizer = PreTrainedTokenizerFast.from_pretrained(
            str(tokenizer_output_path), model_max_length=max_length
        )
    else:
        print("\nTraining or re-training custom BPE tokenizer...")
        if force_retrain and tokenizer_output_path.exists():
            print(
                f"Force retraining: Deleting existing tokenizer directory: {tokenizer_output_path}"
            )
            try:
                shutil.rmtree(tokenizer_output_path)
            except OSError as e:
                print(
                    f"Error deleting directory {tokenizer_output_path}: {e}. Please delete manually and retry."
                )
                raise

        tokenizer_output_path.mkdir(parents=True, exist_ok=True)

        vocab_file_path = tokenizer_output_path / "vocab.json"
        merges_file_path = tokenizer_output_path / "merges.txt"

        if not texts_for_training:
            print("Error: No texts provided for training BPE tokenizer.")
            raise ValueError("Cannot train tokenizer with no data.")

        bpe_trainer_obj = ByteLevelBPETokenizer()

        bpe_default_special_tokens = [
            "[PAD]",
            "[UNK]",
            "[CLS]",
            "[SEP]",
            "[MASK]",
        ]
        # Combine default BPE special tokens with user-defined ones from the global set
        combined_special_tokens = list(
            set(bpe_default_special_tokens + list(global_special_tokens))
        )

        bpe_trainer_obj.train_from_iterator(
            texts_for_training,
            vocab_size=vocab_size,
            min_frequency=2,
            special_tokens=combined_special_tokens,
        )
        bpe_trainer_obj.save_model(str(tokenizer_output_path))
        print(
            f"BPE components (vocab.json, merges.txt) saved to {tokenizer_output_path}"
        )

        bpe_model = BPE.from_file(
            str(vocab_file_path), str(merges_file_path), unk_token="[UNK]"
        )
        tk = Tokenizer(bpe_model)
        tk.normalizer = Sequence([NFKC(), Lowercase()])
        tk.pre_tokenizer = ByteLevel()

        tokenizer = PreTrainedTokenizerFast(
            tokenizer_object=tk,
            unk_token="[UNK]",
            pad_token="[PAD]",
            cls_token="[CLS]",
            sep_token="[SEP]",
            mask_token="[MASK]",
            bos_token="[CLS]",
            eos_token="[SEP]",
            model_max_length=max_length,
        )
        tokenizer.save_pretrained(str(tokenizer_output_path))
        print(
            f"PreTrainedTokenizerFast fully saved to {tokenizer_output_path} (tokenizer.json created)."
        )

    return tokenizer


def run_training(args):
    if args.disable_hf_datasets_progress_bar:
        disable_progress_bar()

    print("--- Starting New Model Training ---")

    benign_asts = load_asts_from_csv(args.benign, args.ast_column)
    malicious_asts = load_asts_from_csv(args.malicious, args.ast_column)

    print(f"Original benign ASTs count: {len(benign_asts)}")
    print(f"Original malicious ASTs count: {len(malicious_asts)}")

    if not malicious_asts:
        print("Error: No malicious ASTs loaded. Cannot proceed with training.")
        return

    if (
        benign_asts
        and args.benign_to_malicious_ratio > 0
        and len(benign_asts) > len(malicious_asts) * args.benign_to_malicious_ratio
    ):
        target_benign_count = int(len(malicious_asts) * args.benign_to_malicious_ratio)
        if target_benign_count < len(
            benign_asts
        ):  # Ensure we are actually downsampling
            print(
                f"Downsampling benign ASTs from {len(benign_asts)} to {target_benign_count}"
            )
            rng = np.random.RandomState(42)
            benign_indices = rng.choice(
                len(benign_asts), size=target_benign_count, replace=False
            )
            benign_asts = [benign_asts[i] for i in benign_indices]
    elif not benign_asts:
        print("Warning: No benign ASTs loaded.")

    print(f"Processed benign ASTs for training lookup: {len(benign_asts)}")
    print(f"Malicious ASTs for training: {len(malicious_asts)}")

    all_texts_for_training = benign_asts + malicious_asts
    all_labels_for_training = [0] * len(benign_asts) + [1] * len(malicious_asts)

    if not all_texts_for_training:
        print("Error: No data available for training after filtering or downsampling.")
        return

    print(f"Total AST strings for model training: {len(all_texts_for_training)}")

    (
        distilbert_train_texts,
        distilbert_val_texts,
        distilbert_train_labels,
        distilbert_val_labels,
    ) = train_test_split(
        all_texts_for_training,
        all_labels_for_training,
        test_size=0.2,
        random_state=42,
        stratify=all_labels_for_training if all_labels_for_training else None,
    )

    if not distilbert_train_texts:
        print(
            "Error: No training data available after train/test split. Cannot proceed."
        )
        return

    try:
        tokenizer = create_or_load_tokenizer(
            tokenizer_output_path=Path(args.tokenizer_path),
            texts_for_training=distilbert_train_texts,
            vocab_size=args.vocab_size,
            global_special_tokens=SPECIAL_TOKENS,  # Pass the globally loaded SPECIAL_TOKENS
            max_length=args.max_length,
            force_retrain=args.force_retrain_tokenizer,
        )
    except Exception as e:
        print(f"Failed to create or load tokenizer: {e}")
        return

    print("\nConverting data to Hugging Face Dataset format...")
    train_data_dict = {"text": distilbert_train_texts, "label": distilbert_train_labels}
    val_data_dict = {"text": distilbert_val_texts, "label": distilbert_val_labels}

    train_hf_dataset = Dataset.from_dict(train_data_dict)
    val_hf_dataset = Dataset.from_dict(val_data_dict)

    raw_datasets = DatasetDict(
        {"train": train_hf_dataset, "validation": val_hf_dataset}
    )

    print("Tokenizing datasets using .map()...")

    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            padding="max_length",
            max_length=args.max_length,
        )

    num_proc = args.num_proc if args.num_proc > 0 else None

    tokenized_datasets = raw_datasets.map(
        tokenize_function, batched=True, num_proc=num_proc, remove_columns=["text"]
    )
    print("Tokenization complete.")

    train_dataset_for_trainer = tokenized_datasets["train"]
    val_dataset_for_trainer = tokenized_datasets["validation"]

    model_output_path = Path(args.model_output_path)
    results_path = model_output_path / "results"
    logs_path = model_output_path / "logs"

    print(f"\nSetting up DistilBERT model for fine-tuning from {args.model_name}...")
    config = DistilBertConfig.from_pretrained(args.model_name, num_labels=2)
    config.pad_token_id = tokenizer.pad_token_id
    config.cls_token_id = tokenizer.cls_token_id
    config.sep_token_id = tokenizer.sep_token_id

    model = DistilBertForSequenceClassification.from_pretrained(
        args.model_name, config=config
    )

    if len(tokenizer) != model.config.vocab_size:
        print(
            f"Resizing model token embeddings from {model.config.vocab_size} to {len(tokenizer)}"
        )
        model.resize_token_embeddings(len(tokenizer))

    training_arguments = TrainingArguments(
        output_dir=str(results_path),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir=str(logs_path),
        logging_steps=10,
        eval_strategy="epoch",
        save_strategy="epoch" if args.save_steps == 0 else "steps",
        save_steps=args.save_steps if args.save_steps > 0 else None,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        save_total_limit=5 if args.save_steps > 0 else None,
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_arguments,
        train_dataset=train_dataset_for_trainer,
        eval_dataset=val_dataset_for_trainer,
        compute_metrics=compute_metrics,
        tokenizer=tokenizer,
    )

    print("\nStarting model training...")
    trainer.train()


if __name__ == "__main__":
    # Define DEFAULT_BENIGN_TO_MALICIOUS_RATIO if it's not already defined globally
    # For example: DEFAULT_BENIGN_TO_MALICIOUS_RATIO = 1.0

    parser = argparse.ArgumentParser()
    parser.add_argument("--benign", "-b", required=True, help="Path to benign CSV")
    parser.add_argument(
        "--malicious", "-m", required=True, help="Path to malicious CSV"
    )
    parser.add_argument("--model-name", default=DEFAULT_MODEL_NAME)
    parser.add_argument(
        "--tokenizer-path", type=Path, default=DEFAULT_TOKENIZER_CLI_PATH
    )
    parser.add_argument(
        "--model-output-path", type=Path, default=DEFAULT_MODEL_OUTPUT_CLI_PATH
    )
    parser.add_argument("--max-length", type=int, default=DEFAULT_MAX_LENGTH)
    parser.add_argument("--epochs", type=int, default=DEFAULT_EPOCHS)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--vocab-size", type=int, default=DEFAULT_VOCAB_SIZE)
    parser.add_argument("--save-steps", type=int, default=DEFAULT_SAVE_STEPS)
    parser.add_argument("--num-proc", type=int, default=DEFAULT_NUM_PROC)
    parser.add_argument("--force-retrain-tokenizer", action="store_true")
    # Removed --resume-from-checkpoint
    parser.add_argument("--disable-hf-datasets-progress-bar", action="store_true")
    parser.add_argument(
        "--ast-column",
        type=str,
        default="tokens",
        help="Name of column to use from CSV",
    )
    parser.add_argument(
        "--benign-to-malicious-ratio",
        type=float,
        default=DEFAULT_BENIGN_TO_MALICIOUS_RATIO,  # Ensure this default is defined
        help="Ratio of benign to malicious samples to use for training (e.g., 1.0 for 1:1). Set to 0 or negative to disable downsampling.",
    )

    args = parser.parse_args()

    run_training(args)
