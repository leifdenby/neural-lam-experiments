# neural-lam-experiments

The aim of the tool (`neural-lam-experiments`) in this repo is to define a process for running a study of experiments with [neural-lam](https://github.com/mllam/neural-lam) against a set of predefined baseline experiments. The tool is designed to make it easy to run a study of training experiments with `neural-lam` and to compare the results of these experiments in a consistent way.

Specifically, `neural-lam-experiments` aims to define a process which allows you to **make reproducable experiments**. This means that the tool aims to enable you to detail 1) what software you used (including versions), 2) what data was used both in training and inference of the models you used, 3) what model architecture was used, 4) the training hyper parameters, 5) evaluation metrics and 6) how to recreate your plots.

Once you have made a study that you wish to share you would create a branch, commit your changes and push your work to your fork of this repo. You can then share your experimental setup by sending a link to your branch to your colleagues 🚀.

## Nomenclature

To be clear about the process for doing scientific process that this repo details, here are some definitions:

- **an experiment**: a single training and evaluation run using a specific dataset of a model architecture in neural-lam
- **a study**: a collection of experiments that are all related to a single research question or hypothesis
- **baseline experiment**: a predefined experiment that has been chosen as a baseline of comparison for capturing a specific aspect of model skill. These will enable use to compare the results of different studies. Over time we will expand the number of baselines and their content.

## Repo layout

```bash
├── baseline-X-v0.1.0         # baseline experiment that is used for baselining your study
│   ├── config.yaml           # config file for the baseline experiment
│   ├── danra.datastore.yaml  # datastore file for the baseline experiment
│   └── run.sh                # run file for the baseline experiment
├── experiments               # directory containing all the experiments in the study
│   ├── experiment_0000
│   ├── experiment_0001
│   └── ...
└── templates                 # directory containing the templates for files needed for each experiment
    ├── run.sh.tpl            # template for the run.sh file
    ├── config.yaml.tpl       # template for the config.yaml file
    ├── danra.datastore.yaml  # file that will be copied to the experiment directory
    └── ...
```

Once a given experiment has been run (baseline or study) then the directory will of course contain anything that `neural-lam` writes out (e.g. `saved_models/`, `wandb/`, `logs/` etc).

### Baseline experiment(s)

The folders with baseline experiments should follow the following naming convention:

```bash
              ┌─── semantic version
            ┌─┴─┐
baseline-X-v0.1.0
         │  └── number denotes the version of the baseline experiment
         └-── letter denotes what kind of baseline this is, the "X"-series
              is just for getting to know the neural-lam-experiments tool
```

Over time we will develop more baseline experiments that capture different aspects of the model. And we will increment the version number as we improve the baseline experiment.

**Exisiting baseline experiments**:

- X-series: These are only used to allow people to become familiar with the `neural-lam-experiments` tool for running studies of experiments with `neural-lam`. The results are probably rubbish, but at least it runs quickly 😆.

## How to use this tool

1. Clone this repo
2. Install the dependencies with `pdm install`.

   If you need a specific version of `neural-lam` `add`/`remove` that dependency. Add any other dependencies you need to `pyproject.toml` and run `pdm install` again:
    ```bash
    pdm remove neural-lam
    # use the following to refer to a specific commit
    pdm add git+https://github.com/mllam/neural-lam@c1f706c29542d770ed49e910f8b9bd5caff1fdec#egg=neural-lam
    # add your own special depenency here (for example hvplot if you need it)
    pdm add hvplot
    ```
    The same environment will be used for all experiments in your study
2. Delete any baseline experiments (e.g. `baseline-X-v0.1.0`) that are not relevant to your study
3. Copy all the files from the baseline experiment (e.g. `baseline-X-v0.1.0`) that you will base the experiments in your study on to the `templates/` directory.
4. Rename any file to add the `.tpl` suffix (e.g. `run.sh` would become `run.sh.tpl`) that you wish to modify in a given experiment (e.g. the CLI run command `run.sh` or config file for neural-lam `config.yaml`) from the baseline experiment to the `templates/` directory.
5. Modify `study_parameters.yaml` to define the experiments in your study. The first level of the yaml file refers to the file to modify (e.g. `run.sh` will use `run.sh.tpl` file in the `templates/` directory). Lists of values are used to define the different experiments in the study.
6. Run `pdm run python generate_experiments.py` to create the experiments in the root directory. These will be generated from the parameters you set in `study_parameters.yaml` and files you put into `templates/`.
7. Run `./runall.sh` to run all the experiments in the study.
8. Run `pdm run python generate_plots.py` to generate plots comparing the results of the experiments in the study.
9. Before you share the results it would be a good idea to create a branch with your study push this to your fork of the `neural-lam-experiments` repo.

## Design constraints

The approach in this tool was developed trying to satisfy the following requirements:

- you should **always** run the baseline experiment including training and evaluation
   - why: rerunning the baseline ensures that changes to the codebase or environment (e.g. changed defaults) have not affected the baseline results
- you should run the **same evaluation** for your experiments as the baseline experiment. This means 1) a dataset that contains the same evaluation period in time and features as the baseline experiment (although you may of course have included more features in the training), and b) same evaluation metrics (same data in and out of the model during evaluation)
   - why: by using the same evaluation dataset and metrics this ensures that we can compare the results of the experiments to the baseline in a meaningful way
- all experiments (study and baseline) should be run in the same environment
   - why: this greatly simplifies the process of running experiments

Non-goals:

- commits to this repo should generally not include large binary content, e.g. no pytorch tensors, zarr datasets, images, etc. Only files that define how to reproduce your experiment should be committed. The result of your experiment will by default only exist on the machine where you trained (unless of course you move the data 😄).

## Possible improvements

- currently all experiments are isolated which means the transformed dataset is created for each, which is unecessary duplication in cases where different experiments use the same dataset. This could maybe be improved by changing neural-lam so that we can specify where the transformed dataset should reside, and we could then also use dvc to handle where processed datasets are actually stored

- create variant of the `./runall.sh` script (say `./runall-slurm-gefion.sh`) where individual experiments are launched using a job scheduler (e.g. slurm) to run experiments in parallel

- replace `./run.sh` run-script for each experiment and `./runall.sh` script with a [dvc](https://dvc.org/) pipeline (these are defined as `yaml`-files) that runs the experiments. This might be easier to understand and maintain than the current approach using bash scripts.
