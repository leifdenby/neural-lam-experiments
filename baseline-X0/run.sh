# 1. Prepare the dataset
pdm run python -m mllam_data_prep danra.datastore.yaml

# 2. Generate the graph
pdm run python -m neural_lam.create_graph \
    --config_path config.yaml \
    --name multiscale

# 2. Train model
WANDB_DISABLED=1 pdm run python -m neural_lam.train_model \
    --config_path config.yaml \
    --hidden_dim 2 \
    --ar_steps_train 1 --ar_steps_eval 1 \
    --epochs 1

# find path to the saved model
# e.g. saved_models/train-graph_lam-4x2-11_25_15-9215/min_val_loss.ckpt
saved_models_paths=$(find saved_models -name "*.ckpt" | sort)
saved_model_path=$(echo $saved_models_paths | cut -d' ' -f1)

# 3. Run evaluation
WANDB_DISABLED=1 pdm run python -m neural_lam.train_model \
    --config_path config.yaml \
    --hidden_dim 2 \
    --ar_steps_eval 1 \
    --eval val --load $saved_model_path --val_steps_to_log 1

# Experiment metrics will be put in
# wandb/offline-run-.../files/...
# e.g. RMSE in wandb/offline-run-.../files/test_rmse.csv
