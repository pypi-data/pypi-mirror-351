import torch
from torchmetrics.functional import pearson_corrcoef, spearman_corrcoef
from typing import Union
import numpy as np

def corr4drug(predictions: Union[torch.Tensor, list, np.ndarray],
              real_results: Union[torch.Tensor, list, np.ndarray],
              drugs: Union[torch.Tensor, list, np.ndarray],
              corr_type: str = "spearman") -> float:
    """
    Calculate the correlation per unique drug and return the average correlation.

    This function groups predictions and real results by drug name, computes the correlation for each group
    using the specified correlation method (Pearson or Spearman), and returns the average correlation
    across all drug groups that have at least two data points.

    Parameters
    ----------
    predictions : array-like, shape (n_samples,)
        Predicted drug response values.
    real_results : array-like, shape (n_samples,)
        Actual (true) response values for each sample.
    drugs : array-like, shape (n_samples,)
        Drug ID/name for each sample.
    corr_type : str, optional
        The type of correlation to compute. Options are "pearson" or "spearman".
        Default is "spearman".

    Returns
    -------
    float
        The average correlation across all unique drugs. If no valid drug groups exist,
        returns NaN.
    """
    # Convert inputs to torch.Tensor if they aren't already.
    if not isinstance(predictions, torch.Tensor):
        predictions = torch.tensor(predictions, dtype=torch.float32)
    if not isinstance(real_results, torch.Tensor):
        real_results = torch.tensor(real_results, dtype=torch.float32)
    
    # Ensure drugs is a list or numpy array for string handling
    if isinstance(drugs, torch.Tensor):
        drugs = drugs.tolist()
    elif isinstance(drugs, np.ndarray):
        drugs = drugs.tolist()

    # Use a set to find unique drug names, then convert back to a list for iteration
    unique_drugs = list(set(drugs))
    
    total_corr = 0.0
    valid_drug_count = 0
    
    for drug_name in unique_drugs:
        # Get indices for the current drug name.
        indices = [i for i, d in enumerate(drugs) if d == drug_name]
        grouped_predictions = predictions[indices]
        grouped_real_results = real_results[indices]
        
        # Skip drug groups with fewer than 2 data points (correlation is undefined).
        if grouped_predictions.numel() < 2:
            continue

        # Compute the chosen correlation.
        if corr_type.lower() == "pearson":
            corr_value = pearson_corrcoef(grouped_predictions, grouped_real_results)
        elif corr_type.lower() == "spearman":
            corr_value = spearman_corrcoef(grouped_predictions, grouped_real_results)
        else:
            raise ValueError("corr_type must be either 'pearson' or 'spearman'.")

        # Replace any NaN values with 0.
        corr_value = torch.nan_to_num(corr_value, nan=0.0)
        
        # Optionally print the drug name if the correlation is nonzero.
        if corr_value != 0:
            print(f"Drug Name {drug_name} has correlation {corr_value.item():.4f}")
        
        total_corr += float(corr_value)
        valid_drug_count += 1

    if valid_drug_count == 0:
        return float('nan')
    return total_corr / valid_drug_count
