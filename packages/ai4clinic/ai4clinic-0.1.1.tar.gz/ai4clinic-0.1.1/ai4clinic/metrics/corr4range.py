import torch
from torch import Tensor
from torchmetrics.functional import pearson_corrcoef, spearman_corrcoef

def corr4range(predictions,
               real_results,
               threshold: float,
               sensitive_area: str = "bottom",
               corr_type: str = "spearman") -> Tensor:
    """
    Calculate the correlation between predictions and real_results within a sensitive area.

    The sensitive area is defined by a threshold on the real_results:
      - If sensitive_area is "bottom", only data points with real_results < threshold are used.
      - If sensitive_area is "top", only data points with real_results > threshold are used.

    Parameters
    ----------
    predictions : array-like, shape (n_samples,)
        Predicted drug response values.
    real_results : array-like, shape (n_samples,)
        Actual (true) response values for each sample.
    threshold : float
        The threshold value to define the sensitive area.
    sensitive_area : str, optional
        Indicates whether the sensitive area is at the "bottom" (real_results < threshold) or
        "top" (real_results > threshold) of the label distribution. Default is "bottom".
    corr_type : str, optional
        The type of correlation to compute. Options are "pearson" or "spearman".
        Default is "spearman".

    Returns
    -------
    torch.Tensor
        A scalar tensor representing the computed correlation. If no data points fall within
        the specified sensitive area, returns NaN.
    """
    # Convert inputs to tensors if they aren't already
    if not isinstance(predictions, Tensor):
        predictions = torch.tensor(predictions, dtype=torch.float32)
    if not isinstance(real_results, Tensor):
        real_results = torch.tensor(real_results, dtype=torch.float32)

    # Select indices based on the specified sensitive area.
    if sensitive_area.lower() == "bottom":
        indices = (real_results < threshold).nonzero(as_tuple=True)[0]
    elif sensitive_area.lower() == "top":
        indices = (real_results > threshold).nonzero(as_tuple=True)[0]
    else:
        raise ValueError("sensitive_area must be either 'bottom' or 'top'.")

    if indices.numel() == 0:
        return torch.tensor(float('nan'))

    sensitive_predictions = predictions[indices]
    sensitive_real_results = real_results[indices]

    # Compute the requested correlation using torchmetrics functions.
    if corr_type.lower() == "pearson":
        return pearson_corrcoef(sensitive_predictions, sensitive_real_results)
    elif corr_type.lower() == "spearman":
        return spearman_corrcoef(sensitive_predictions, sensitive_real_results)
    else:
        raise ValueError("corr_type must be either 'pearson' or 'spearman'.")

