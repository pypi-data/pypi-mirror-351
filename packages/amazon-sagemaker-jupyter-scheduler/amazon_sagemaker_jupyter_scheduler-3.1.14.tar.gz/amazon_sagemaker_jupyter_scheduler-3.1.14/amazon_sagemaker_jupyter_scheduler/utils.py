import re
import uuid
import datetime
from typing import Dict
from datetime import datetime


def sanitize_string(name: str, length: int):
    return re.sub(r"[^a-zA-Z0-9]", "", name)[:length]


def get_pipeline_expression_output_name(
    job_name: str, notebook_name: str, notebook_extension: str
) -> Dict:
    return {
        "Std:Join": {
            "On": "-",
            "Values": [
                f"{sanitize_string(job_name, 10)}",
                f"{sanitize_string(notebook_name,10)}",
                {"Get": "Execution.StartDateTime"},
                f"{notebook_extension}",
            ],
        }
    }


def generate_job_identifier(name: str, notebook_name: str):
    # accepted pattern - https://github.com/jupyter-server/jupyter-scheduler/commit/ee1e2be9cb630ebb2d4dcd7febb2b98ba119a14b
    # JOB_DEFINITION_ID_REGEX = r"(?P<job_definition_id>\w+(?:-\w+)+)"
    # JOB_ID_REGEX = r"(?P<job_id>\w+(?:-\w+)+)"
    # \w: Matches any word character (alphanumeric & underscore).
    # Only matches low-ascii characters (no accented or non-roman characters).
    # Equivalent to [A-Za-z0-9_]

    # Pipeline name: 256 chars
    # https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreatePipeline.html#sagemaker-CreatePipeline-request-PipelineName
    # Pattern: ^[a-zA-Z0-9](-*[a-zA-Z0-9]){0,255}
    # Even though it supports 256, going to reduce it to 63

    # Event Bridge Rule: 64
    # https://docs.aws.amazon.com/eventbridge/latest/APIReference/API_PutRule.html#eventbridge-PutRule-request-Name
    # [\.\-_A-Za-z0-9]+

    # Training name: 63 chars
    # https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateTrainingJob.html#sagemaker-CreateTrainingJob-request-TrainingJobName
    # ^[a-zA-Z0-9](-*[a-zA-Z0-9]){0,62}
    # Pipeline created Training jobs uses 20 chars from the field Name of the Training Step
    # We will split this between notebook name & job/job definition name
    # need to make sure these character also fits OSS requirement also.
    # pipelines-kbexktydy93v-<20 chars of Name>-aRjXdJ39fV
    # we will take 10 chars of job definition name and 10 chars of notebook name

    # Any customer given field will be sanitized to only include [A-Za-z0-9],
    # remove all other special chars
    # 19 chars - 2020-07-10-15-00-01
    # 8 chars - random id uuid4
    # 3 chars - delimiter (-)
    # max 33 chars - <job_name>-<notebook_name>
    # example - hourly-reportgenerator-ef21b9ad-2020-07-10-15-00-01
    sanitized_name = sanitize_string(name, 17)
    sanitized_notebook_name = sanitize_string(notebook_name, 16)
    random_id = str(uuid.uuid4())[:8]
    formatted_timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    return (
        f"{sanitized_name}-{sanitized_notebook_name}-{random_id}-{formatted_timestamp}"
    )
