import os
from amazon_sagemaker_jupyter_scheduler.clients import (
    get_sts_client,
)
from async_lru import alru_cache


@alru_cache(maxsize=1)
async def get_aws_account_id():
    accountId = os.environ.get("AWS_ACCOUNT_ID")
    if accountId is None:
        # we are in standalone jupyterlab
        get_caller_identity_response = await get_sts_client().get_caller_identity()
        accountId = get_caller_identity_response.get("Account")
    return accountId
