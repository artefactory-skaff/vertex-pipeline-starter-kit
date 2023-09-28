# How to set up a GPU Docker container that runs

While training Deep Learning algorithms, you might need GPUs to speed up the process.
This tutorial will show you how to:

- Create a Docker Image with GPU support
- Set up Vertex AI to run the Docker Image on a GPU
- Make sure the Vertex training component step access the GPU

## Create a Docker Image with GPU support

Please refer to this excellent [tutorial](https://towardsdatascience.com/a-complete-guide-to-building-a-docker-image-serving-a-machine-learning-system-in-production-d8b5b0533bde#:~:text=3.%20Building%20a%20Docker%20image%20for%20any%20Python%20Project%20(GPU)%3A) to create a Docker Image with GPU support.

### 1. Identify the CUDA version of your local environment

This take-away from the article is important:

> [!IMPORTANT]
> Always use the same CUDA and cuDNN version in Docker image as present in the underlying host machine

So the first step is to identify which CUDA version and PyTorch version you are using in your local environment.

To identify the CUDA version of your local environment, run:

```bash
$ pip freeze | grep cu

nvidia-cudnn-cu11==8.5.0.96
```

Means I have CUDA 11 installed, and CuDNN 8.

### 2. Select a Docker image that matches your CUDA version

> Docker hub of Nvidia has a lot of images, so understanding their tags and selecting the correct image is the most important building block.

Prefers `nvidia/cuda` Docker images compared to `pytorch/` and  `vertex-ai/training`.

You need to select a Docker image that matches this version. Check out the [Docker Hub](https://hub.docker.com/r/nvidia/cuda/tags) to find a compatible version. In my case, I found [this one](https://hub.docker.com/layers/nvidia/cuda/11.7.1-cudnn8-runtime-ubuntu20.04/images/sha256-352a7039e533fb22d24de831d09aa3791431c2e5809c279a336fe0aeef72b7fb?context=explore): `nvidia/cuda:11.7.0-cudnn8-runtime-ubuntu20.04`

so I would start my dockerfile with:

```Dockerfile
FROM nvidia/cuda:11.7.0-cudnn8-runtime-ubuntu20.04
```

### 3. Install Python

You need to install the same Python version as the one you are using in your local environment.

In my case, I am using Python 3.9, so I would add this line to my Dockerfile:

```Dockerfile hl_lines="2-21"
FROM nvidia/cuda:11.7.0-cudnn8-runtime-ubuntu20.04
ENV PYTHON_VERSION=3.9
ENV CONTAINER_TIMEZONE=Europe/Paris

# Set the timezone to prevent tzdata asking for user input
RUN ln -snf /usr/share/zoneinfo/$CONTAINER_TIMEZONE /etc/localtime && echo $CONTAINER_TIMEZONE > /etc/timezone

RUN apt update \
    && apt install --no-install-recommends -y build-essential \
    tzdata \
    python${PYTHON_VERSION} \
    python${PYTHON_VERSION}-venv \
    python3-pip \
    python3-setuptools \
    python3-distutils \ 
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s -f /usr/bin/python${PYTHON_VERSION} /usr/bin/python3 && \
    ln -s -f /usr/bin/python${PYTHON_VERSION} /usr/bin/python && \
    ln -s -f /usr/bin/pip3 /usr/bin/pip
```

### 4. Install the PyTorch or Tensorflow version that is compatible with your CUDA version

> [!WARNING]
> Don’t blindly install latest tensorflow/pytorch library from PyPi. It is absolutely incorrect that any version of this both package will work with any version of CUDA, cuDNN. In fact, the combination of the latest version of both, tensorflow/pytorch with CUDA/cuDNN may not be compatible

For PyTorch for example, go to the [Install Section](https://pytorch.org/#:~:text=Aid%20to%20Ukraine.-,INSTALL%20PYTORCH,-Select%20your%20preferences) to find a compatible version. You can also browse the previous versions [here](https://pytorch.org/get-started/previous-versions/).

You need to install a GPU version.
In my case, I found this one: `torch==2.0.0+cu117` in the website, with the install instruction:

```bash
pip install torch==2.0.0+cu117 --index-url https://download.pytorch.org/whl/cu117
```

So I would add this line to my Dockerfile, with the `--no-cache-dir` option to avoid caching the wheel file, which can crash the build.

Then, I also install the requirements.txt file of my project, and copy the source code.

```Dockerfile hl_lines="21-26"
FROM nvidia/cuda:11.7.0-cudnn8-runtime-ubuntu20.04

ARG PROJECT_ID
ENV PROJECT_ID=${PROJECT_ID}
ENV PYTHON_VERSION=3.9
ENV CONTAINER_TIMEZONE=Europe/Paris

# Set the timezone to prevent tzdata asking for user input
RUN ln -snf /usr/share/zoneinfo/$CONTAINER_TIMEZONE /etc/localtime && echo $CONTAINER_TIMEZONE > /etc/timezone

# export DEBIAN_FRONTEND=noninteractive \
RUN apt update \
    && apt install --no-install-recommends -y build-essential \
    tzdata \
    python${PYTHON_VERSION} \
    python${PYTHON_VERSION}-venv \
    python3-pip \
    python3-setuptools \
    python3-distutils \ 
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s -f /usr/bin/python${PYTHON_VERSION} /usr/bin/python3 && \
    ln -s -f /usr/bin/python${PYTHON_VERSION} /usr/bin/python && \
    ln -s -f /usr/bin/pip3 /usr/bin/pip

RUN python3 -m pip install --no-cache-dir torch==2.0.0+cu117 --index-url https://download.pytorch.org/whl/cu117
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .
```

## Ask for a GPU in your Vertex pipeline, for your training step

In your `pipeline.py`, add `set_gpu_limit` and `add_node_selector_constraint` to your training component, then select a GPU type:

```python
@kfp.dsl.pipeline(name="training-pipeline")
def pipeline(
    project_id: str,
):
    split_data_task = load_and_split_data_component(
        project_id=project_id,
    )
    train_model_task = (
        (
            train_model_component(
                project_id=project_id,
                train=split_data_task.outputs["train_dataset"],
                val=split_data_task.outputs["val_dataset"],
                test=split_data_task.outputs["test_dataset"],
            )
        )
        .set_gpu_limit(1)
        .add_node_selector_constraint(
            label_name="cloud.google.com/gke-accelerator",
            value="NVIDIA_TESLA_P100",
        )
    )
```

**Troubleshooting errors**

- Make sure the Quotas allows you to query the GPU type you want. You might have to request a quota increase.
- Also, you must select a GPU type that is available in the region you are using.


## Run your pipeline and make sure the Vertex training component step access the GPU

In the code of my component/ workflow, I log the GPU availability with:

```python

import torch

def train_model_workflow(
    some_parameters: int,
):
    logger.info(f"GPU:{torch.cuda.is_available()}")
```

This allows me to check is the GPU is available in the logs of the Vertex training component step.

If the GPU is available, you will see this in the logs:

```bash
GPU:True
```

If the GPU is not available, it means your Docker image is not configured properly, or you did not select a GPU type in your Vertex pipeline.
Iterate on the previous steps to fix the issue.
