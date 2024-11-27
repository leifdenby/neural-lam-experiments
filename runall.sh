# This script handles launching each of the experiments in the repository (both
# study and baseline) in a serial manner (i.e. one-by-one).


cwd=$(pwd)

# exit the script on ctrl-c
trap "exit" INT
# exit the script on any error
set -e

run_experiments() {
    experiment_runscripts="$1"
    experiment_kind="$2"
    # check that we have at least one experiment runscript
    if [ ${#experiment_runscripts[@]} -eq 0 ]; then
        echo "No $experiment_kind experiments found"
        exit 1
    fi

    # run the experiments
    for experiment in "${experiment_runscripts[@]}"; do
        echo "Running $experiment"
        # chdir to the experiment directory
        cd $(dirname $experiment)
        bash $(basename $experiment)
        # chdir back to the root directory
        cd $cwd
    done
}

run_experiments_of_kind() {
    experiment_kind="$1"
    if [ "$experiment_kind" == "baseline" ]; then
        # run the baseline experiment(s), find the scripts to run first, they
        # have the path ./reference-*/run.sh
        runscripts=(reference-*/run.sh)
    elif [ "$experiment_kind" == "parameter-experiment" ]; then
        # run experiments where we vary the parameters, they follow the path
        # ./experiments/*/run.sh
        runscripts=(experiments/*/run.sh)
    else
        echo "Unknown experiment kind: $experiment_kind"
        exit 1
    fi

    run_experiments $runscripts $experiment_kind
}

# check cli arguments, if first argument is either "baseline" or "study" we
# only want to run that kind of experiments
if [ $# -eq 1 ]; then
    kinds_to_run=("$1")
else
    # by default we run both baseline and study experiments
    kinds_to_run=("baseline" "parameter-experiments")
fi

for kind in "${kinds_to_run[@]}"; do
    run_experiments_of_kind $kind
done
