from jupyter_scheduler.exceptions import SchedulerError
from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.extension.handler import ExtensionHandlerMixin
import os
import tornado
import json
import time
import urllib
import botocore
from async_timeout import timeout

from amazon_sagemaker_jupyter_scheduler.advanced_environments.sagemaker_advanced_environments import (
    SageMakerAdvancedEnvironments,
)
from amazon_sagemaker_jupyter_scheduler.advanced_environments.sagemaker_studio_advanced_environment import (
    SageMakerStudioAdvancedEnvironments,
)
from amazon_sagemaker_jupyter_scheduler.environment_detector import (
    JupyterLabEnvironmentDetector,
    JupyterLabEnvironment,
)
from amazon_sagemaker_jupyter_scheduler.app_metadata import (
    get_region_name,
    get_sagemaker_environment,
)

from amazon_sagemaker_jupyter_scheduler.providers.jupyterlab_image_metadata import (
    get_image_metadata_jupyterlab
)

from amazon_sagemaker_jupyter_scheduler.error_util import NoCredentialsSchedulerError, BotoClientSchedulerError, BotoEndpointConnectionSchedulerError

WEBAPP_SETTINGS_URL = "https://studiolab.sagemaker.aws/settings.json"
MAX_WAIT_TIME_FOR_API_CALL_SECS = 8.0


class AdvancedEnvironmentsHandler(ExtensionHandlerMixin, JupyterHandler):
    @tornado.web.authenticated
    async def get(self):
        try:
            async with timeout(MAX_WAIT_TIME_FOR_API_CALL_SECS):
                if (
                    get_sagemaker_environment()
                    == JupyterLabEnvironment.SAGEMAKER_STUDIO
                    or get_sagemaker_environment()
                    == JupyterLabEnvironment.SAGEMAKER_JUPYTERLAB
                ):
                    self.log.info(f"[AdvancedEnviornmentsHandler] SageMaker Studio environment detected")
                    envs = await SageMakerStudioAdvancedEnvironments().get_advanced_environments(
                        self.log
                    )
                else:
                    self.log.info(f"[AdvancedEnviornmentsHandler] Vanilla JupyterLab environment detected")
                    envs = (
                        await SageMakerAdvancedEnvironments().get_advanced_environments(
                            self.log
                        )
                    )
                self.finish(envs.json())
        except BotoClientSchedulerError as error:
            self.log.exception(f"[AdvancedEnvironmentsHandler] BotoClientSchedulerError error detected: {error}")
            self.set_status(error.status_code)
            self.finish({"error_code": error.error_code, "message": str(error.error_message)})
        except NoCredentialsSchedulerError as error:
            self.log.exception(f"[AdvancedEnvironmentsHandler] NoCredentialsSchedulerError error detected: {error}")
            self.set_stats(error.error_code)
            self.finish({"error_code": error.error_code, "message": str(error.error_message)})
        except BotoEndpointConnectionSchedulerError as error:
            self.log.exception(f"[AdvancedEnvironmentsHandler] EndpointConnectionError error detected: {error}")
            self.set_status(error.status_code)
            self.finish({"error_code": error.error_code, "message": str(error.error_message)})
        except SchedulerError as error:
            self.set_status(403)
            self.finish(
                json.dumps({"error_code": "NoCredentials", "message": str(error)})
            )
        except Exception as error:
            self.log.exception(f"[AdvancedEnviornmentsHandler] Generic exception detected: {error}")
            self.set_status(500)
            self.finish(json.dumps({"error": str(error)}))


class ValidateVolumePathHandler(ExtensionHandlerMixin, JupyterHandler):
    @tornado.web.authenticated
    async def post(self):
        try:
            body = self.get_json_body()
            if "file_path" in body:
                file_exist = os.path.exists(body["file_path"])
                self.set_status(200)
                self.finish(json.dumps({"file_path_exist": file_exist}))
            else:
                self.set_status(400)
                self.finish(json.dumps({"error": "invalid input"}))
        except Exception as e:
            self.log.exception(f"[ValidateVolumePathHandler] Encountered error when validating file path: {e}")
            self.set_status(500)
            self.finish(json.dumps({"error": e.msg}))


class SageMakerImagesListHandler(ExtensionHandlerMixin, JupyterHandler):
    @tornado.web.authenticated
    async def get(self):
        if get_sagemaker_environment() == JupyterLabEnvironment.SAGEMAKER_JUPYTERLAB:
            image_metadata = await get_image_metadata_jupyterlab()
            self.finish(json.dumps(
                [
                    {
                        "image_arn": image_metadata.image_arn,
                        "image_display_name": image_metadata.image_display_name,
                    }
                ])
            )
        else:
            # Image list handler is not implemented for other app types
            self.finish(json.dumps([]))
