from raymon.types import load_jcr


def class_error_type(pred, gt, pos=1):
    """[summary]
    This function takes a model prediction, a ground truth value and a pointer to what should be considered the positive class and determines the classification error type: a True Positive, True Negative, False Positice or False Negative.
    :param pred: The prediction you want to score. This is the model output.
    :type pred: dict, JSON compatible representation of rt.Native
    :param gt: the ground truth of the prediction you want to score.
    :type gt: dict, JSON compatible representation of rt.Native
    :param pos: The value that should be considered a positive value, defaults to 1
    :type pos: int, str
    :return: TP, TN, FP or FN
    :rtype: str
    """
    pred = load_jcr(pred).data
    gt = load_jcr(gt).data
    if gt == pos and pred == pos:
        err = "TP"
    elif gt == pos and pred != pos:
        err = "FN"
    elif gt != pos and pred == pos:
        err = "FP"
    else:
        err = "TN"
    return err


def abs_err(pred, gt):
    """Take a regression prediction and a ground truth value and determine the absolute error.

    :param pred: The predicted value
    :type pred: dict, JSON compatible representation of rt.Native
    :param gt: The ground truth value
    :type gt: dict, JSON compatible representation of rt.Native
    :return: Absolute error
    :rtype: float
    """
    pred = load_jcr(pred).data
    gt = load_jcr(gt).data
    return abs(pred - gt)


def sq_err(pred, gt):
    """Take a regression prediction and a ground truth value and determine the absolute error.

    :param pred: The predicted value
    :type pred: dict, JSON compatible representation of rt.Native
    :param gt: The ground truth value
    :type gt: dict, JSON compatible representation of rt.Native
    :return: Squared error
    :rtype: float
    """
    pred = load_jcr(pred).data
    gt = load_jcr(gt).data
    return pow(pred - gt, 2)
