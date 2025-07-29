from __future__ import annotations

import logging
import warnings
from collections.abc import Iterator
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from hpoglue import BenchmarkDescription, Measure, TabularBenchmark
from hpoglue.env import Env
from hpoglue.fidelity import RangeFidelity

from hposuite.constants import DATA_DIR
from hposuite.utils import is_package_installed

if TYPE_CHECKING:
    from hpoglue import Config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)


url: str = "https://figshare.com/ndownloader/files/21188607"


def _download_lcbench_tabular(datadir: Path) -> None:
    import shutil
    import urllib.request
    import zipfile

    datadir.mkdir(parents=True, exist_ok=True)
    zippath = datadir / "data_2k.zip"
    if not zippath.exists():
        _urlopen = urllib.request.urlopen
        print("Downloading from {url}")     # noqa: T201
        with _urlopen(url) as response, zippath.open("wb") as f:
            shutil.copyfileobj(response, f)

    with zipfile.ZipFile(zippath, "r") as zip_ref:
        zip_ref.extractall(datadir)

    print("Downloaded lcbench_tabular data to {datadir.resolve()}")     # noqa: T201


def _process(data_dir: Path) -> None:
    import json

    filepath = data_dir / "data_2k.json"
    print("Processing lcbench_tabular ...")     # noqa: T201
    with filepath.open("r") as f:
        all_data = json.load(f)

    for dataset_name, data in all_data.items():
        logger.info(f"Processing {dataset_name}")
        config_frames_for_dataset = []
        for config_id, config_data in data.items():
            config: dict = config_data["config"]

            log_data: dict = config_data["log"]
            loss: list[str] = log_data["Train/loss"]  # Name of the loss
            val_ce: list[float] = log_data["Train/val_cross_entropy"]
            val_acc: list[float] = log_data["Train/val_accuracy"]
            val_bal_acc: list[float] = log_data["Train/val_balanced_accuracy"]

            test_ce: list[float] = log_data["Train/test_cross_entropy"]
            test_bal_acc: list[float] = log_data["Train/test_balanced_accuracy"]

            # NOTE: Due to there being a lack of "Test/val_accuracy" in the
            # data but a "Train/test_result" we use the latter as the test accuracy
            test_acc: list[float] = log_data["Train/test_result"]

            time = log_data["time"]
            epoch = log_data["epoch"]

            _df = pd.DataFrame(
                {
                    "time": time,
                    "epoch": epoch,
                    "loss": loss,
                    "val_accuracy": val_acc,
                    "val_cross_entropy": val_ce,
                    "val_balanced_accuracy": val_bal_acc,
                    "test_accuracy": test_acc,
                    "test_cross_entropy": test_ce,
                    "test_balanced_accuracy": test_bal_acc,
                },
            )
            # These are single valued but this will make them as a list into
            # the dataframe
            _df = _df.assign(**{"id": config_id, **config})

            config_frames_for_dataset.append(_df)

        #                     | **metrics, **config_params
        # (config_id, epoch)  |

        df_for_dataset = (
            pd.concat(config_frames_for_dataset, ignore_index=True)
            .convert_dtypes()
            .set_index(["id", "epoch"])
            .sort_index()
        )
        table_path = data_dir / f"{dataset_name}.parquet"
        df_for_dataset.to_parquet(table_path)
        logger.info(f"Processed {dataset_name} to {table_path}")


def _setup_lcbench_tabular(datadir: Path) -> None:
    datadir = datadir / "lcbench_tabular"
    if datadir.exists():
        print(f"Data directory {datadir.resolve()} already exists")     # noqa: T201
        return
    _download_lcbench_tabular(datadir)
    _process(datadir)


lcbench_config_keys = [
    "batch_size",
    "max_dropout",
    "max_units",
    "num_layers",
    "learning_rate",
    "momentum",
    "weight_decay",

    # Optional keys
    # "loss",
    # "imputation_strategy",
    # "learning_rate_scheduler",
    # "network",
    # "normalization_strategy",
    # "optimizer",
    # "cosine_annealing",
    # "cosine_annealing_eta_min",
    # "activation",
    # "mlp_shape",
]


def _get_lcbench_space(task_id: str, datadir: Path) -> list[Config]:
    table = _load_lcbench_table(task_id, datadir)
    return TabularBenchmark.get_tabular_config_space(table, lcbench_config_keys)


def _load_lcbench_table(task_id: str, datadir: Path) -> pd.DataFrame:
    return pd.read_parquet(datadir / f"{task_id}.parquet")


def _get_lcbench_tabular_bench(
    description: BenchmarkDescription,
    *,
    task_id: str,
    datadir: Path,
) -> TabularBenchmark:
    table = _load_lcbench_table(task_id, datadir)

    return TabularBenchmark(
        desc=description,
        table=table,
        id_key="id",  # Key in the table to uniquely identify configs
        config_keys=lcbench_config_keys,  # Keys in the table that correspond to configs
    )


def lcbench_tabular(datadir: Path) -> Iterator[BenchmarkDescription]:
    """Generates benchmark descriptions for the LCBench tabular Benchmark.

    Args:
        datadir (Path | None): The directory where the data is stored.
        If None, the default directory is used.

    Yields:
        Iterator[BenchmarkDescription]: An iterator over BenchmarkDescription objects
        for each task in the LCBench tabular Benchmark.
    """
    task_ids = (
        "adult",
        "airlines",
        "albert",
        "Amazon_employee_access",
        "APSFailure",
        "Australian",
        "bank-marketing",
        "blood-transfusion-service-center",
        "car",
        "christine",
        "cnae-9",
        "connect-4",
        "covertype",
        "credit-g",
        "dionis",
        "fabert",
        "Fashion-MNIST",
        "helena",
        "higgs",
        "jannis",
        "jasmine",
        "jungle_chess_2pcs_raw_endgame_complete",
        "kc1",
        "KDDCup09_appetency",
        "kr-vs-kp",
        "mfeat-factors",
        "MiniBooNE",
        "nomao",
        "numerai28.6",
        "phoneme",
        "segment",
        "shuttle",
        "sylvine",
        "vehicle",
        "volkert",
    )

    env = Env(
        name="py310-lcbench-tabular",
        python_version="3.10",
        requirements=(
            "pandas",
            "pyarrow"
        ),
        post_install=_setup_cmd(datadir),
    )
    for req in env.requirements:
        if not is_package_installed(req):
            logger.warning(
                f"Please install the required package for lcbench_tabular: {req}",
                stacklevel=2
            )
            return
    for task_id in task_ids:
        try:
            space = _get_lcbench_space(
                task_id=task_id,
                datadir=datadir
            )
        except FileNotFoundError:
            logger.error(
                f"lcbench_tabular data not found in Data directory {datadir.resolve()}. "
                "Run `python -m hposuite.benchmarks.lcbench_tabular setup` "
                "to download and process the benchmark data."
            )
            return
        yield BenchmarkDescription(
            name=f"lcbench_tabular-{task_id}",
            config_space=space,
            load=partial(_get_lcbench_tabular_bench, task_id=task_id, datadir=datadir),
            is_tabular=True,
            fidelities={
                "epoch": RangeFidelity.from_tuple((1, 51, 1), supports_continuation=True),
            },
            costs={
                "time": Measure.cost((0.0, np.inf), minimize=True),
            },
            metrics={
                "val_accuracy": Measure.metric((0.0, 100.0), minimize=False),
                "val_cross_entropy": Measure.metric((0.0, np.inf), minimize=True),
                "val_balanced_accuracy": Measure.metric((0.0, 1.0), minimize=False),
            },
            test_metrics={
                "test_accuracy": Measure.metric((0.0, 100.0), minimize=False),
                "test_balanced_accuracy": Measure.test_metric((0.0, 1.0), minimize=False),
                "test_cross_entropy": Measure.test_metric(bounds=(0.0, np.inf), minimize=True),
            },
            env=env,
            mem_req_mb=4096,
        )


def _setup_cmd(datadir: Path) -> tuple[str, ...]:
    install_cmd = f"python -m hposuite.benchmarks.lcbench_tabular setup --data_dir {datadir}"
    if datadir is not None:
        install_cmd += f" --data-dir {datadir.resolve()}"
    return tuple(install_cmd.split(" "))


def lcbench_tabular_benchmarks(datadir: Path | None = None) -> Iterator[BenchmarkDescription]:
    """Generator function that yields benchmark descriptions from the lcbench_tabular benchmark."""
    if isinstance(datadir, str):
        datadir = Path(datadir).resolve() / "lcbench_tabular"
    elif datadir is None:
        datadir = DATA_DIR / "lcbench_tabular"
    yield from lcbench_tabular(datadir=datadir)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Setup LCBench Tabular Benchmark data")
    subparsers = parser.add_subparsers(dest="command")
    setup_parser = subparsers.add_parser(
        "setup",
        help="Download and process the LCBench Tabular Benchmark data",
    )
    setup_parser.add_argument(
        "--datadir",
        type=str,
        default=DATA_DIR,
        help="Absolute path of the directory to store the lcbench_tabular data",
    )

    args = parser.parse_args()
    if isinstance(args.datadir, str):
        args.datadir = Path(args.datadir).absolute().resolve()
    _setup_lcbench_tabular(args.datadir)