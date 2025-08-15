# Use the same base image as your working docker run command
FROM huggingface/transformers-pytorch-gpu:latest

# Set working directory
WORKDIR /home/work

# Copy requirements file first (for better Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install specific version of triton from git
RUN pip install --no-cache-dir git+https://github.com/triton-lang/triton.git@v3.4.0#subdirectory=python/triton_kernels

# Copy application code and configs
COPY *.py ./
COPY configs/ ./configs/

# Create models directory (to be mounted as volume)
RUN rm -rf models && mkdir -p models
