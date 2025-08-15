#!/bin/bash
set -xe

DOCKER_TAG=gpt-oss-finetuning:latest

echo "build docker image $DOCKER_TAG"
rm -rf .build
mkdir -p .build
docker build --pull --platform linux/amd64 -t $DOCKER_TAG .

if [[ $model == '120b' ]]
then
    echo "run 120b model"
    docker run --rm --gpus all -v $(pwd):/home/work \
        $DOCKER_TAG \
        bash -c "cd /home/work && accelerate launch --config_file configs/120b-fsdp.yaml sft-120b.py --config configs/120b-sft-lora.yaml --run_name 120b-full-eager --attn_implementation kernels-community/vllm-flash-attn3 --output_dir ./models/openai/gpt-oss-120b-multilingual-reasoner"
else
    echo "run 20b model"
        docker run --rm --gpus all -v $(pwd):/home/work \
        $DOCKER_TAG \
        bash -c "cd /home/work && accelerate launch --config_file configs/20b-zero3.yaml sft-20b.py --config configs/20b-sft-full.yaml --run_name 20b-full-eager --attn_implementation kernels-community/vllm-flash-attn3 --output_dir ./models/openai/gpt-oss-20b-multilingual-reasoner"
fi 