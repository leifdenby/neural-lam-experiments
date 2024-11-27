from pathlib import Path
from typing import Any, Dict, Iterator

import jinja2
import jinja2.meta
import yaml
from loguru import logger

TEMPLATES_DIR = Path("templates")
PARAMETERS_FILEPATH = Path("study_parameters.yaml")
EXPERIMENTS_PATH = Path("experiments")
EXPERIMENT_NAME_FORMAT = "experiment-{:04d}"


def generate_parameters_for_all_experiments() -> Iterator[Dict[str, Any]]:
    """
    Generate all possible combinations of parameters for the experiments. Each
    experiment is defined by a dictionary of parameters, the first level of
    which is the filename of the template to be used to generate the
    experiment. The subsequent levels are the parameters that will be passed to
    the Jinja2 template.

    Parameters
    ----------
    None

    Returns
    -------
    Iterator[Dict[str, Any]]
        An iterator that yields a dictionary of parameters for each experiment.
    """
    # Load the study parameters
    with open(PARAMETERS_FILEPATH) as f:
        study_parameters = yaml.safe_load(f)

    # The keys in the first level of `study_parameters` are the filenames of the templates
    # that will be used to generate the experiments.
    # Any subsequent levels are the parameters that will be passed to the
    # Jinja2 template. Where they values are a list of values, the template
    # will be rendered for each value. To facilitate the generation of the experiments,
    # we therefore need to generate all possible combinations of parameters.
    # This can be done using the `itertools.product` function.

    def _visit_subtree(subtree):
        if isinstance(subtree, dict):
            # just return the dict as is, but with the values replaced by
            # the result of the recursive call
            for key, value in subtree.items():
                for subtree_value in _visit_subtree(value):
                    yield {key: subtree_value}
        elif isinstance(subtree, list):
            # for each value in the list we yield the result of the recursive call
            for value in subtree:
                yield value
        else:
            raise NotImplementedError(f"Unexpected type {type(subtree)}")

    for experiment_parameters in _visit_subtree(study_parameters):
        yield experiment_parameters


def _find_all_variables_in_template(template_source: str):
    env = jinja2.Environment()
    ast = env.parse(template_source)
    variables_in_template = jinja2.meta.find_undeclared_variables(ast)
    return variables_in_template


def generate_experiments():
    # keep a dictionary with the loaded templates so we only read them once
    # from disk
    templates = {}
    templates_variables = {}

    for i, experiment_parameters in enumerate(
        generate_parameters_for_all_experiments()
    ):
        experiment_path = EXPERIMENTS_PATH / EXPERIMENT_NAME_FORMAT.format(i)
        experiment_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Generating experiment {i:<4d} in {experiment_path}")

        written_files = []

        for fn, file_parameters in experiment_parameters.items():
            # Create the experiment directory
            fp_experiment_file = experiment_path / fn

            if fn not in templates:
                # Load the Jinja2 template matching the experiment file to be modified
                with open(TEMPLATES_DIR / f"{fn}.tpl") as f:
                    template_source = f.read()
                    templates[fn] = jinja2.Template(template_source)
                    templates_variables[fn] = set(
                        _find_all_variables_in_template(template_source)
                    )

            template = templates[fn]
            variables_in_template = templates_variables[fn]

            # find all the variables used in the template
            variables_in_study = set(file_parameters.keys())
            missing_in_template = variables_in_study - variables_in_template
            missing_in_study = variables_in_template - variables_in_study
            if missing_in_template:
                raise ValueError(
                    f"Variables {missing_in_template} are missing in the template. "
                    "Maybe you forgot to add them to the template?"
                )
            if missing_in_study:
                raise ValueError(
                    f"Variables {missing_in_study} are missing in the study parameters. "
                    "Maybe you forgot to add them to the study parameters?"
                )

            with open(fp_experiment_file, "w") as f:
                logger.debug(
                    f"Writing {fp_experiment_file} with parameters {file_parameters}"
                )
                f.write(template.render(file_parameters))

            written_files.append(fp_experiment_file.name)

        # copy all files that don't end in .tpl
        for fp_template in TEMPLATES_DIR.glob("*"):
            if fp_template.name.endswith(".tpl"):
                continue
            if fp_template.name in written_files:
                continue
            fp_experiment_file = experiment_path / fp_template.name
            logger.debug(f"Copying {fp_template} to {fp_experiment_file}")
            fp_experiment_file.write_text(fp_template.read_text())


def main():
    generate_experiments()


if __name__ == "__main__":
    main()
