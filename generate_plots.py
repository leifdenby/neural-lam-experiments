from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import xarray as xr
from loguru import logger

from generate_experiments import EXPERIMENTS_PATH


def _find_experiment_filepath(experiment_fp_root, filename: str):
    experiment_name = experiment_fp_root.name
    fps = sorted(list(experiment_fp_root.glob(f"**/{filename}")))
    if len(fps) == 0:
        raise FileNotFoundError(
            f"No files found for experiment {experiment_name} and filename {filename}"
        )
    # return the last (most recent) file
    return fps[0]


def _find_experiments(experiment_kind: str):
    if experiment_kind == "baseline":
        prefix = "reference-"
        fp_cwd = Path(__file__).parent
        fps = sorted(list(fp_cwd.glob(f"{prefix}*")))
    elif experiment_kind == "study":
        prefix = "experiment-"
        logger.debug(f"Looking for experiments in {EXPERIMENTS_PATH}")
        fps = sorted(list(EXPERIMENTS_PATH.glob(f"{prefix}*")))
    else:
        raise ValueError(f"Unexpected experiment kind {experiment_kind}")

    if len(fps) == 0:
        raise FileNotFoundError(f"No experiments found for {experiment_kind}")

    return fps


def load_experiment_results():
    fps_experiments = _find_experiments(experiment_kind="baseline") + _find_experiments(
        experiment_kind="study"
    )
    datasets = []

    for fp_experiment in fps_experiments:
        fp_experiment_name = fp_experiment.name
        fp_rmse = _find_experiment_filepath(fp_experiment, "rmse.csv")
        pd_rmse = pd.read_csv(fp_rmse)

        ds = xr.Dataset()
        ds["rmse"] = xr.DataArray(pd_rmse["rmse"], dims=["time"])
        ds["experiment_name"] = fp_experiment_name
        datasets.append(ds)

    ds_all = xr.concat(datasets, dim="experiment_name")

    return ds_all


def plot_experiment_results():
    ds_all = load_experiment_results()
    fig, ax = plt.subplots()
    ds_all["rmse"].plot.line(ax=ax, x="time", hue="experiment_name")
    fig.savefig("rmse.png")


def main():
    plot_experiment_results()


if __name__ == "__main__":
    main()
