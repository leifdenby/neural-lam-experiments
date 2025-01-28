from pathlib import Path

import matplotlib.pyplot as plt
import neural_lam.config as nl_config
import pandas as pd
import xarray as xr
from loguru import logger

from generate_experiments import EXPERIMENTS_PATH, EXPERIMENTS_PREFIX

BASELINES_PREFIX = "baseline-"


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
        prefix = BASELINES_PREFIX
        fp_cwd = Path(__file__).parent
        fps = sorted(list(fp_cwd.glob(f"{prefix}*")))
    elif experiment_kind == "study":
        prefix = EXPERIMENTS_PREFIX
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
        fp_rmse = _find_experiment_filepath(fp_experiment, "test_rmse.csv")

        # the CSV files don't include the row and column names
        # neural_lam.models.ar_model.ARmodel.create_metric_log_dict states that
        # the `metric_tensor` that is written to CSV is:
        # > metric_tensor: (pred_steps, d_f), metric values per time
        # so for now we'll just read in the training dataset to get the state
        # feature names
        exp_config, exp_datastore = nl_config.load_config_and_datastore(
            fp_experiment / "config.yaml"
        )
        state_feature_names = exp_datastore.get_vars_names(category="state")

        pd_rmse = pd.read_csv(fp_rmse, names=state_feature_names)

        # the row index is the ar-step, so set that name and make the first index value 1
        pd_rmse.index.name = "ar-step"
        pd_rmse.index = pd_rmse.index + 1
        print(pd_rmse)

        # melt the dataframe so that the state feature names are in a column
        pd_rmse = pd_rmse.reset_index().melt(
            id_vars="ar-step", var_name="feature", value_name="rmse"
        )

        ds_rmse = pd_rmse.to_xarray()
        # turn into 2D dataset with ar-step and feature as dimensions
        ds_rmse = ds_rmse.set_index(index=("ar-step", "feature")).unstack("index")
        ds_rmse["experiment_name"] = fp_experiment_name

        datasets.append(ds_rmse)

    ds_all = xr.concat(datasets, dim="experiment_name")

    return ds_all


def plot_experiment_results():
    ds_rmse = load_experiment_results()
    fig, ax = plt.subplots()
    print(ds_rmse)
    ds_rmse["rmse"].plot.line(
        ax=ax, x="time", hue="experiment_name", col="feature", col_wrap=4
    )
    fig.savefig("rmse.png")


def main():
    plot_experiment_results()


if __name__ == "__main__":
    main()
