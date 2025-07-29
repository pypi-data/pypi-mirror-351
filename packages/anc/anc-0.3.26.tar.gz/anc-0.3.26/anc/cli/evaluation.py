import click
import sys
import os
import json
from pathlib import Path
from anc.cli.util import click_group, console
from .util import ConfigManager
import uuid
import datetime
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import Console
from rich import box
from .operators.eval_operator import trigger_eval_job, display_evaluation_status

@click_group()
def eval():
    pass

@eval.command()
@click.argument('model_name', required=True, type=click.Choice(['ds_v2', 'ds_v2_lite', 'qwen25_7b', 'qwen25_14b', 'qwen25_32b']))
@click.option(
    '--dataset_paths',
    type=str,
    required=True,
    help='the eval dataset path of list/single of dataset'
)
@click.option(
    '--ckpt_paths',
    type=str,
    required=True,
    help='the eval ckpt path of list of ckpt'
)
@click.option(
    '--tp',
    type=int,
    required=False,
    default=8,
    help='the evaltensor parallel size'
)
@click.option(
    '--pp',
    type=int,
    required=False,
    default=1,
    help='the eval pipeline parallel size'
)
@click.option(
    '--ep',
    type=int,
    required=False,
    default=1,
    help='the eval expert parallel size'
)
@click.option(
    '--seq_len',
    type=int,
    required=True,
    help='the eval sequence length'
)
@click.option(
    '--batch_size',
    type=int,
    required=True,
    help='the eval batch size'
)
@click.option(
    '--tokenizer_path',
    type=str,
    required=False,
    default="/mnt/project/llm/ckpt/tokenizer/ocean_deepseek_v2",
    help='the project name'
)
@click.option(
    '--project_name',
    type=str,
    required=False,
    default="my_test",
    help='the project name'
)
@click.pass_context
def model(ctx, model_name, ckpt_paths, dataset_paths, tp, pp, ep, seq_len, batch_size, tokenizer_path, project_name):
    """command like: anc eval ds_v2 --ckpt_paths  --ckpt_paths ckpt_paths --dataset_paths dataset_paths"""
    print("args:", model_name, ckpt_paths, dataset_paths)
    if  not ckpt_paths.startswith("/mnt/project") and not ckpt_paths.startswith("/mnt/share"):
        print("ckpt path is invalid, must be start with /mnt/project or /mnt/share")
        sys.exit(0)
    
    if  not dataset_paths.startswith("/mnt/project") and not dataset_paths.startswith("/mnt/share"):
        print("dataset path is invalid, must be start with /mnt/project or /mnt/share")
        sys.exit(0)
        
    # the recipt of the eval
    run_id = str(uuid.uuid4())
    
    # Create a rich Table for configuration details
    config_table = Table(box=box.ROUNDED, expand=True, show_header=False, border_style="blue")
    config_table.add_column("Parameter", style="cyan", no_wrap=True)
    config_table.add_column("Value", style="green")
    
    # Add basic info
    config_table.add_row("Model Name", model_name)
    config_table.add_row("Checkpoint Path", ckpt_paths)
    config_table.add_row("Dataset Path", dataset_paths)
    config_table.add_row("Tokenizer Path", tokenizer_path)
    config_table.add_row("Project Name", project_name)
    # Add parallelism config
    config_table.add_section()
    config_table.add_row("Tensor Parallel", str(tp))
    config_table.add_row("Pipeline Parallel", str(pp))
    config_table.add_row("Expert Parallel", str(ep))
    
    # Add run parameters
    config_table.add_section()
    config_table.add_row("Batch Size", str(batch_size))
    config_table.add_row("Sequence Length", str(seq_len))

    # Create title with run ID
    title = Text(f"✨ EVALUATION RECEIPT [ID: {run_id}] ✨", style="bold magenta")
    
    # Wrap the table in a panel
    panel = Panel(
        config_table,
        title=title,
        subtitle="Your evaluation receipt!",
        border_style="blue",
        expand=False
    )
    
    # Print the panel using the console
    console.print("\n")
    console.print(panel)
    console.print("\n")
    # TODO: Implement need the user confirm the evaluation receipt
    user_confirm = input("Do you want to start the evaluation? (y/n): ")
    if user_confirm.lower() != 'y':
        print("Evaluation cancelled.")
        sys.exit(0)
    
    eval_ckpt_paths_list = []
    if os.path.isdir(ckpt_paths):
        for ckpt_path in os.listdir(ckpt_paths):
            eval_ckpt_paths_list.append(os.path.join(ckpt_paths, ckpt_path))
    else:
        raise ValueError("ckpt_paths is not a directory")
    
    if not os.path.isdir(dataset_paths):
        raise ValueError("dataset_paths is not a directory")
    trigger_eval_job(run_id, model_name, project_name, eval_ckpt_paths_list, dataset_paths, tp, pp, ep, seq_len, batch_size, tokenizer_path)
    
    
    

@eval.command(name='status')
@click.argument('eval_id', required=True, type=str)
def status(eval_id):
   """check eval job: anc eval status xxx """
   display_evaluation_status(eval_id)

def add_command(cli_group):
    cli_group.add_command(eval)