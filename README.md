# llm-fine-tune-recipes
A collections of recipes for fine tuning LLMs

## OpenAI gpt-oss
Built on [Hugging Face GPT-OSS recipes](https://github.com/huggingface/gpt-oss-recipes) and [SkyPilot examples](https://github.com/skypilot-org/skypilot/tree/master/llm/gpt-oss-finetuning).

While fine-tuning GPT-OSS-20B works seamlessly with existing scripts, GPT-OSS-120B presents significant memory challenges, frequently encountering out-of-memory (OOM) errors during model loading and training. This repository provides memory-optimized configurations that have been tested on A100 and H100 GPUs with 80GB VRAM, and the Docker file was provided as well for easy deployments.

```bash
cd gpt-oss-finetuning && chmod +x run.sh && model=120b ./run.sh
```

