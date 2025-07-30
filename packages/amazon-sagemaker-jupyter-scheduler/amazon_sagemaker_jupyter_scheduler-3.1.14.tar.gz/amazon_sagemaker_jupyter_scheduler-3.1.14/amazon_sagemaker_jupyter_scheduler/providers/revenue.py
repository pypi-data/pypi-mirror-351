from amazon_sagemaker_jupyter_scheduler.app_metadata import get_sagemaker_environment
from amazon_sagemaker_jupyter_scheduler.environment_detector import (
    JupyterLabEnvironment,
)


def get_revenue_attribution_string():
    # This can be used to identify training jobs submitted by different libraries
    revenue_string = "sagemaker_headless_execution_vanilla"
    if get_sagemaker_environment() == JupyterLabEnvironment.SAGEMAKER_STUDIO:
        revenue_string = "sagemaker_headless_execution"
    elif get_sagemaker_environment() == JupyterLabEnvironment.SAGEMAKER_JUPYTERLAB:
        revenue_string = "sagemaker_headless_execution_jupyterlab"

    return revenue_string
