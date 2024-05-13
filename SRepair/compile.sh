#!/bin/bash

mkdir buggy
mkdir d4j

cd DatasetExtractor
./gradlew shadowJar
cd ..

pip3 install psutil tqdm tiktoken openai
pip3 install torch torchvision torchaudio
pip3 install git+https://github.com/huggingface/transformers.git@main

python3 pull_models.py