# Copyright 2020-2025 The HuggingFace Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
accelerate launch \
    --config_file configs/20b-zero3.yaml \
    sft.py \
    --config configs/20b-sft-full.yaml \
    --model_name_or_path openai/gpt-oss-20b \
    --packing true packing_strategy wrapped \
    --run_name 20b-full-eager \
    --attn_implementation kernels-community/vllm-flash-attn3
"""

from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, Mxfp4Config

from trl import (
    ModelConfig,
    ScriptArguments,
    SFTConfig,
    SFTTrainer,
    TrlParser,
    get_peft_config,
)


def generate_responses(
    model, tokenizer, user_message, system_message=None, max_new_tokens=100
):
    """Generate responses from the model given a user message."""
    # Format chat using tokenizer's chat template
    messages = []
    messages.append({"role": "system", "content": "reasoning language: Chinese"})

    # We assume the data are all single-turn conversation
    messages.append({"role": "user", "content": user_message})

    inputs = tokenizer.apply_chat_template(
        messages,
    ).to(model.device)

    generated = model.generate(**inputs, max_new_tokens=1024)
    response = tokenizer.decode(generated[0][inputs["input_ids"].shape[-1] :])
    return response


def test_model_with_questions(
    model, tokenizer, questions, system_message=None, title="Model Output"
):
    """Test the model with a set of questions and print responses."""
    print(f"\n=== {title} ===")
    for i, question in enumerate(questions, 1):
        response = generate_responses(model, tokenizer, question, system_message)
        print(f"\nModel Input {i}:\n{question}\nModel Output {i}:\n{response}\n")


def main(script_args, training_args, model_args):
    # ------------------------
    # Load model & tokenizer
    # ------------------------
    quantization_config = Mxfp4Config(dequantize=True)
    model_kwargs = dict(
        revision=model_args.model_revision,
        trust_remote_code=model_args.trust_remote_code,
        attn_implementation=model_args.attn_implementation,
        torch_dtype=model_args.torch_dtype,
        use_cache=False if training_args.gradient_checkpointing else True,
        quantization_config=quantization_config,
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_args.model_name_or_path, **model_kwargs
    )

    tokenizer = AutoTokenizer.from_pretrained(
        model_args.model_name_or_path,
    )

    # --------------
    # Load dataset
    # --------------
    dataset = load_dataset(script_args.dataset_name, name=script_args.dataset_config)

    # -------------
    # Train model
    # -------------
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset[script_args.dataset_train_split],
        eval_dataset=(
            dataset[script_args.dataset_test_split]
            if training_args.eval_strategy != "no"
            else None
        ),
        processing_class=tokenizer,
        peft_config=get_peft_config(model_args),
    )

    trainer.train()
    print(f"Saving model to {training_args.output_dir}")
    trainer.save_model(training_args.output_dir)
    if training_args.push_to_hub:
        trainer.push_to_hub(dataset_name=script_args.dataset_name)
        print("Pushed model to hub")


if __name__ == "__main__":
    parser = TrlParser((ScriptArguments, SFTConfig, ModelConfig))
    script_args, training_args, model_args, _ = parser.parse_args_and_config(
        return_remaining_strings=True
    )
    main(script_args, training_args, model_args)
