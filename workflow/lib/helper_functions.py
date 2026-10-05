def get_difftype(
    metric: str,
) -> str:
    """
    Converts the name of the metric to a difference type.

    Parameters
    ----------
    metric : str
        Name of the metric

    Returns
    -------
    str
        Inferred difference type
    """

    if 'median' in metric:
        return 'median'
    else:
        return 'mean'


def get_x_thresh(
    metric: str,
    modality: str,
) -> float:
    """
    Provides a threshold for the difference significance based
    on the name of the metric and the modality.

    Parameters
    ----------
    metric : str
        Name of the metric
    modality : str
        Modality of the data

    Returns
    -------
    float
        Threshold for the difference
    """

    if metric == 'meandiff':
        return 1.5
    elif metric == 'mediandiff':
        if modality == 'expression':
            return 0.5
        elif modality == 'indegree':
            return 5
        elif modality == 'outdegree':
            return 100
    # "Sensible" default
    return 2