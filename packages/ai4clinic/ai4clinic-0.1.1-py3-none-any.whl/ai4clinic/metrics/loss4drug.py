import torch
from torch import Tensor
from typing import Callable, Union
import numpy as np
from typing import Callable, Union, List

def loss4drug(criterion: Union[Callable[[Tensor, Tensor], Tensor], str],
              drugs: Union[Tensor, List, np.ndarray],
              predictions: Union[Tensor, List, np.ndarray],
              real_results: Union[Tensor, List, np.ndarray]) -> Tensor:
    """
    Calculate the loss per unique drug and return the average loss.

    Parameters
    ----------
    criterion : callable or str
        Loss function or string specifying loss type ('mse' or 'l1').
    predictions : array-like, shape (n_samples,)
        Predicted drug response values.
    real_results : array-like, shape (n_samples,)
        Actual (true) response values for each sample.
    drugs : array-like, shape (n_samples,)
        Drug ID/name for each sample.

    Returns
    -------
    torch.Tensor
        Average loss across unique drugs.
    """
    # Convert inputs to torch.Tensor
    drugs = torch.as_tensor(drugs)
    predictions = torch.as_tensor(predictions, dtype=torch.float32)
    real_results = torch.as_tensor(real_results, dtype=torch.float32)

    # Initialize loss function
    if isinstance(criterion, str):
        criterion_name = criterion.lower()
        if criterion_name in ("mse", "mse_loss", "mean_squared_error"):
            criterion = torch.nn.MSELoss(reduction='mean')
        elif criterion_name in ("l1", "l1_loss", "mean_absolute_error"):
            criterion = torch.nn.L1Loss(reduction='mean')
        else:
            raise ValueError(f"Unsupported loss type: {criterion}")

    # Calculate loss per drug
    total_loss = 0.0
    unique_drugs = torch.unique(drugs)

    for drug_id in unique_drugs:
        mask = (drugs == drug_id)
        drug_preds = predictions[mask]
        drug_reals = real_results[mask]
        total_loss += criterion(drug_preds, drug_reals)

    return total_loss / len(unique_drugs)
