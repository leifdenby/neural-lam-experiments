# This script handles launching each of the experiments in the repository (both
# study and baseline) in a serial manner (i.e. one-by-one).


cwd=$(pwd)

# exit the script on ctrl-c
trap "exit" INT
# exit the script on any error
set -e

run_experiment() {
    experiment_runscript="$1"

    echo "Executing $experiment_runscript"
    # chdir to the experiment directory
    cd $(dirname $experiment_runscript)
    bash $(basename $experiment_runscript)
    # chdir back to the root directory
    cd $cwd
}

run_experiments_of_kind() {
    experiment_kind="$1"
    if [ "$experiment_kind" == "baseline" ]; then
        # run the baseline experiment(s), find the scripts to run first, they
        # have the path ./reference-*/run.sh
        runscripts=(reference-*/run.sh)
    elif [ "$experiment_kind" == "non-baseline" ]; then
        # run experiments where we vary the parameters, they follow the path
        # ./experiments/*/run.sh
        runscripts=(experiments/*/run.sh)
    else
        echo "Unknown experiment kind: $experiment_kind"
        exit 1
    fi
    # print all the runscripts we found

    # check that we have at least one experiment runscript
    if [ ${#runscripts[@]} -eq 0 ]; then
        echo "No $experiment_kind experiments found"
        exit 1
    else
        echo "Found ${#runscripts[@]} $experiment_kind experiments to run"
    fi

    # run the experiments
    for experiment in "${runscripts[@]}"; do
        run_experiment $runscripts
    done
}

# check cli arguments, if first argument is either "baseline" or "study" we
# only want to run that kind of experiments
if [ $# -eq 1 ]; then
    kinds_to_run=("$1")
else
    # by default we run both baseline and study experiments
    kinds_to_run=("baseline" "non-baseline")
fi

for kind in "${kinds_to_run[@]}"; do
    run_experiments_of_kind $kind
done
