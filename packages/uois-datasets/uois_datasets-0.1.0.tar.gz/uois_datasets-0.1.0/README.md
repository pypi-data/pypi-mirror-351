```shell
conda create -n uois-datasets python=3.10
conda activate uois-datasets
export CUDA_HOME=/usr/local/cuda-12.6 # (use your cuda version)
python -m pip install build twine
```
