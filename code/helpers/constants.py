from pathlib import Path

environment = 'local'  # or colab
print(f'Environment is {environment}')
batch_size = 2
maskrcnn_batch_size = 12 if environment == 'colab' else 6  # 16 for google colab, 6 for local
slow_pathway_size = 1
fast_pathway_size = 1
use_proposals = True
use_rpn_proposals = True
continue_training = False
random_seed = 42
model_name = f'model_maskrcnn_slowfast_sp_{slow_pathway_size}fp_{fast_pathway_size}_pred_boxes_{use_proposals}_rpn_{use_rpn_proposals}'
root_dir_path = Path('/content/gdrive/My Drive/Python Projects/adl4cv_root') if environment == 'colab' else Path('')
writer_dir = (root_dir_path / 'runs') / model_name
root_dir_path.mkdir(parents=True, exist_ok=True)
models_dir_path = root_dir_path / Path('models')
models_dir_path.mkdir(parents=True, exist_ok=True)
best_model_path = models_dir_path / (f'{model_name}_best.pth')
model_path = models_dir_path / (f'{model_name}.pth')
checkpoint_path = models_dir_path / (f'{model_name}_checkpoint.pth')
data_output_path = root_dir_path / Path('data/output')
data_output_path.mkdir(parents=True, exist_ok=True)
eval_output_path = (data_output_path / 'eval_output')
eval_output_path.mkdir(parents=True, exist_ok=True)
pred_output_path = (data_output_path / 'pred_output')
pred_output_path.mkdir(parents=True, exist_ok=True)
