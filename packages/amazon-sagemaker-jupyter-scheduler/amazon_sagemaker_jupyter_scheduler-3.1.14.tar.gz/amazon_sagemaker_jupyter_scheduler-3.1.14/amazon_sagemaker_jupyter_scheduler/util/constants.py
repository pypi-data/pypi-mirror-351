from sagemaker_jupyterlab_extension_common.dual_stack_utils import is_dual_stack_enabled

LOG_FILE_NAME = "sagemaker-scheduler.api.log"
LOGGER_NAME = "sagemaker-scheduler-api-operations"

STUDIO_LOG_FILE_PATH = "/var/log/studio/scheduled_notebooks"
STUDIO_LOG_FILE_NAME = "sagemaker_scheduling_extension_api.log"


# Regex pattern for stack trace filters
email_regex = "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}"
# credit to https://uibakery.io/regex-library/phone-number-python
phone_number_regex = (
    "\+?\d{1,4}?[-.\s]?\(?(\d{1,3}?)\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}"
)

password_regex = "(?i)password\s*[:=]\s*\S+"
api_key_regex = "(?i)apikey\s*[:= ]\s*\S+"
aws_secretkey_regex = "(?i)aws_secret_access_key\s*[:=]\s*\S+"

IAM_TIMEOUT = 3

DEFAULT_JOB_DEFINITION_RETRY_VALUE = 1

USE_DUALSTACK_ENDPOINT = is_dual_stack_enabled()
