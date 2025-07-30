"""Tmp saving and loading.
"""

import os
import pickle
from pathlib import Path
from pathlib import PurePath
from typing import Tuple
from typing import Union

import torch

from .common import get_str_time


def load_dict(filename_):
    with open(filename_, "rb") as f:
        ret_di = pickle.load(f)
    return ret_di


def save_dict(di_, filename_):
    # Get the directory path from the filename
    dir_path = os.path.dirname(filename_)

    # Create the directory if it does not exist
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    with open(filename_, "wb") as f:
        pickle.dump(di_, f)


def get_modelfile_path(model_filename: str) -> PurePath:
    model_path: PurePath = Path(f".checkpoints/{model_filename}.pt")
    if not model_path.parent.exists():
        model_path.parent.mkdir(parents=True, exist_ok=True)
    return model_path


def check_modelfile_exists(model_filename: str) -> bool:
    if get_modelfile_path(model_filename).exists():
        return True
    return False


def save_model(
    model_filename: str,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    current_epoch: int,
    loss: float,
) -> None:
    """Save model, optimizer, current_epoch, loss to ``.checkpoints/${model_filename}.pt``.

    Args:
        model_filename (str): filename to save model.
        model (torch.nn.Module): model.
        optimizer (torch.optim.Optimizer): optimizer.
        current_epoch (int): current epoch.
        loss (float): loss.
    """
    model_path = get_modelfile_path(model_filename)
    torch.save(
        {
            "epoch": current_epoch,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "loss": loss,
        },
        model_path,
    )


def load_model(
    model_filename: str,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer = None,
    device: torch.device = torch.device("cpu"),
) -> Tuple[torch.nn.Module, torch.optim.Optimizer, int, float]:
    """Load model from ``.checkpoints/${model_filename}.pt``.

    Args:
        model_filename (str): filename to load model.
        model (torch.nn.Module): model.
        optimizer (torch.optim.Optimizer): optimizer.

    Returns:
        Tuple[torch.nn.Module, torch.optim.Optimizer, int, float]:
            [model, optimizer, epoch, loss]
    """

    model_path = get_modelfile_path(model_filename)
    checkpoint = torch.load(model_path, map_location=device)

    model.load_state_dict(checkpoint["model_state_dict"])
    if optimizer is not None:
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
    epoch = checkpoint["epoch"]
    loss = checkpoint["loss"]

    return model, optimizer, epoch, loss


def save_embedding(
    node_embeddings: torch.tensor,
    dataset_name: str,
    model_name: str,
    params: dict,
    save_dir: str = "./save",
    verbose: Union[bool, int] = True,
):
    """Save embeddings.

    Args:
        node_embeddings (torch.tensor): node embeddings.
        dataset_name (str): dataset name.
        model_name (str): model name.
        params (dict): parameter dict.
        save_dir (str, optional): save dir. Defaults to "./save".
        verbose (Union[bool, int], optional): whether to print debug info. Defaults to True.
    """
    dataset_name = dataset_name.replace("_", "-")
    timestamp = get_str_time()
    file_name = f"{dataset_name.lower()}_{model_name.lower()}_embeds_{timestamp}.pth"
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    file_path = os.path.join(save_dir, file_name)

    result = {
        "node_embeddings": node_embeddings.cpu().detach(),
        "hyperparameters": params,
    }

    torch.save(result, file_path)

    if verbose:
        print(f"Embeddings and hyperparameters saved to {file_path}")
