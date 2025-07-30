from enum import Enum
import os
import subprocess


class JupyterLabEnvironment(Enum):
    SAGEMAKER_STUDIO = "SageMakerStudio"
    SAGEMAKER_JUPYTERLAB = "SageMakerJupyterLab"
    VANILLA_JUPYTERLAB = "VanillaJupyterLab"


class JupyterLabEnvironmentDetector:
    SAGEMAKER_JUPYTERLAB_APP_TYPE_ENVIRON = "JupyterLab"
    SAGEMAKER_STUDIO_UI_EXTENSION_NAME = "@amzn/sagemaker-ui"

    def __init__(self):
        self.current_environment = self._detect_environment()

    def _get_installed_extensions(self):
        try:
            result = subprocess.run(
                ["jupyter", "labextension", "list"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            if result.returncode != 0:
                # TODO: Add a logger to publish logs to Jupyter Server
                # self.log.error(
                #     f"An error occurred while fetching JupyterLab extensions: {result.stderr}"
                # )
                return ""
            else:
                return result.stderr
        except subprocess.CalledProcessError as e:
            # TODO: Add a logger to publish logs to Jupyter Server
            # self.log.error(
            #     f"An error occurred while fetching JupyterLab extensions: {str(e)}"
            # )
            return ""

    def _detect_environment(self):
        if (
            os.environ.get("SAGEMAKER_APP_TYPE", None)
            == self.SAGEMAKER_JUPYTERLAB_APP_TYPE_ENVIRON
        ):
            return JupyterLabEnvironment.SAGEMAKER_JUPYTERLAB
        if self.SAGEMAKER_STUDIO_UI_EXTENSION_NAME in self._get_installed_extensions():
            return JupyterLabEnvironment.SAGEMAKER_STUDIO
        else:
            return JupyterLabEnvironment.VANILLA_JUPYTERLAB
