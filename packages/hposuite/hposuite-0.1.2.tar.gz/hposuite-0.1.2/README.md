[![image](https://img.shields.io/pypi/v/hposuite.svg)](https://pypi.python.org/pypi/hposuite)
[![image](https://img.shields.io/pypi/l/hposuite)](https://pypi.python.org/pypi/hposuite)
[![image](https://img.shields.io/pypi/pyversions/hposuite.svg)](https://pypi.python.org/pypi/hposuite)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![GitHub](https://img.shields.io/badge/GitHub-hpoglue-rgb(50,50,200)?logo=github&logoColor=white)](https://github.com/automl/hpoglue)

# hposuite
A lightweight framework for benchmarking HPO algorithms, providing wrappers for HPO benchmarks and optimizers. Provides a simple API for large-scale HPO experimentation.

## Minimal Example to run hposuite

```python
from hposuite import create_study

study = create_study(
    name="hposuite_demo",
    output_dir="./hposuite-output",
    optimizers=[...],   # Eg: "RandomSearch"
    benchmarks=[...],   # Eg: "ackley"
    num_seeds=5,
    budget=100,         # Number of iterations
)

study.optimize()
```

> [!TIP]
> * See below for an example of [Running multiple Optimizers on multiple Benchmarks](#Simple-example-to-run-multiple-Optimizers-on-multiple-benchmarks)
> * Check this example [notebook](https://github.com/automl/hposuite/blob/main/examples/hposuite_demo.ipynb) for more demo examples
> * This [notebook](https://github.com/automl/hposuite/blob/main/examples/opt_bench_usage_examples.ipynb) contains usage examples for Optimizer and Benchmark combinations
> * This [notebook](https://github.com/automl/hposuite/blob/main/examples/study_usage_examples.ipynb) demonstrates some of the features of hposuite's Study
> * This [notebook](https://github.com/automl/hposuite/blob/main/examples/plots_and_comparisons.ipynb) shows how to plot results for comparison
> * Check out [hpoglue](https://github.com/automl/hpoglue) for core HPO API for interfacing an Optimizer and Benchmark

## Installation

### Create a Virtual Environment using Venv
```bash
python -m venv hposuite_env
source hposuite_env/bin/activate
```
### Installing from PyPI

```bash
pip install hposuite
```

> [!TIP]
> * `pip install hposuite["notebook"]` - For usage in a notebook
> * `pip install hposuite["all"]` - To install hposuite with all available optimizers and benchmarks
> * `pip install hposuite["optimizers"]` - To install hposuite with all available optimizers only
> * `pip install hposuite["benchmarks"]` - To install hposuite with all available benchmarks only


> [!NOTE]
> * We **recommend** doing `pip install hposuite["all"]` to install all available benchmarks and optimizers, along with `ipykernel` for running the notebook examples

### Installation from source

```bash
git clone https://github.com/automl/hposuite.git
cd hposuite

pip install -e . # -e for editable install
```


### Simple example to run multiple Optimizers on multiple benchmarks

```python
from hposuite.benchmarks import BENCHMARKS
from hposuite.optimizers import OPTIMIZERS

from hposuite import create_study

study = create_study(
    name="smachb_dehb_mfh3good_pd1",
    output_dir="./hposuite-output",
    optimizers=[
        OPTIMIZERS["SMAC_Hyperband"],
        OPTIMIZERS["DEHB_Optimizer"]
    ],
    benchmarks=[
        BENCHMARKS["mfh3_good"],
        BENCHMARKS["pd1-imagenet-resnet-512"]
    ],
    num_seeds=5,
    budget=100,
)

study.optimize()

```

### Command-Line usage

```bash
python -m hposuite \
    --optimizer RandomSearch Scikit_Optimize \
    --benchmark ackley \
    --num_seeds 3 \
    --budget 50 \
    --study_name test_study
```

### View all available Optimizers and Benchmarks


```python 
from hposuite.optimizers import OPTIMIZERS
from hposuite.benchmarks import BENCHMARKS
print(OPTIMIZERS.keys())
print(BENCHMARKS.keys())
```



### Results

hposuite saves the `Study` by default to `../hposuite-output/` (relative to the current working directory).
Results are saved in the `Run` subdirectories within the main `Study` directory as `.parquet` files. \
The `Study` directory and the individual `Run` directory paths are logged when running `Study.optimize()`

To view the result dataframe, use the following code snippet:
```python
import pandas as pd
df = pd.read_parquet("<full path to the result .parquet file>")
print(df)
print(df.columns)
```

### Plotting

```bash
python -m hposuite.plotting.incumbent_trace \
    --study_dir <study directory name> \
    --output_dir <abspath of dir where study dir is stored> \
    --save_dir <path relative to study_dir to store the plots> \ # optional
    --plot_file_name <file_name for saving the plot> \ # optional
```

`--save_dir` is set by default to `study_dir/plots`
`--output_dir` by default is `../hposuite-output`



### Overview of available Optimizers

For a more detailed overview, check [here](https://github.com/automl/hposuite/blob/main/hposuite/optimizers/README.md)

| Optimizer Package                                                     | Blackbox | Multi-Fidelity (MF) | Multi-Objective (MO) | Expert Priors |
|-----------------------------------------------------------------------|----------|---------------------|----------------------|---------------|
| RandomSearch                                                          | ✓        |                     | ✓                    |               |
| RandomSearch with priors                                              | ✓        |                     | ✓                    | ✓             |
| [NePS][https://github.com/automl/neps]                                | ✓        | ✓                   | ✓                    | ✓             |
| [SMAC](https://github.com/automl/SMAC3)                               | ✓        | ✓                   | ✓                    | ✓             |
| [DEHB](https://github.com/automl/DEHB)                                |          | ✓                   |                      |               |
| [HEBO](https://github.com/huawei-noah/HEBO)                           | ✓        |                     |                      |               |
| [Nevergrad](https://github.com/facebookresearch/nevergrad)            | ✓        |                     | ✓                    |               |
| [Optuna](https://github.com/optuna/optuna)                            | ✓        |                     | ✓                    |               |
| [Scikit-Optimize](https://github.com/scikit-optimize/scikit-optimize) | ✓        |                     |                      |               |






### Overview of available Benchmarks

For a more detailed overview, check [here](https://github.com/automl/hposuite/blob/main/hposuite/benchmarks/README.md)

| Benchmark Package                            | Type       | Multi-Fidelity | Multi-Objective |
|----------------------------------------------|------------|----------------|-----------------|
| Ackley                                       | Synthetic  |    |    |
| Branin                                       | Synthetic  |    |    |
| [mf-prior-bench](https://github.com/automl/mf-prior-bench)          | Synthetic, Surrogate  | ✓  |  ✓  |
| MF-Hartmann Tabular                          | Tabular    | ✓  |    | 
| [LCBench-Tabular](https://github.com/automl/LCBench)              | Tabular    | ✓  | ✓  |
| [Pymoo](https://pymoo.org/)                  | Synthetic  |    |    | 
| [IOH](https://iohprofiler.github.io/) ([BBOB](https://numbbo.github.io/coco/testsuites/bbob))                | Synthetic  |    |    |
| BBOB Tabular                                 | Tabular    |    |    |

