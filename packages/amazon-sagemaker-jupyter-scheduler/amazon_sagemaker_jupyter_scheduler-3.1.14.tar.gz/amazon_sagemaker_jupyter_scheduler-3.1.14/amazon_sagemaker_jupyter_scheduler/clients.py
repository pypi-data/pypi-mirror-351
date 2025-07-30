import asyncio
import logging
import os
from typing import Dict, List, Optional
import botocore
from amazon_sagemaker_jupyter_scheduler.internal_metadata_adapter import (
    InternalMetadataAdapter,
)
from aiobotocore.session import get_session, AioSession

from amazon_sagemaker_jupyter_scheduler.app_metadata import (
    get_partition,
    get_region_name,
)

from amazon_sagemaker_jupyter_scheduler.util.constants import USE_DUALSTACK_ENDPOINT

LOOSELEAF_STAGE_MAPPING = {"devo": "beta", "loadtest": "gamma"}

from amazon_sagemaker_jupyter_scheduler.util.constants import IAM_TIMEOUT


class BaseAsyncBotoClient:
    cfg: any
    partition: str
    region_name: str
    sess: AioSession

    def __init__(self, partition: str, region_name: str):
        self.cfg = botocore.client.Config(
            # TODO: Refine these values (currently copied from LooseLeafNb2Kg)
            connect_timeout=10,
            read_timeout=20,
            retries={"max_attempts": 2},
            use_dualstack_endpoint=USE_DUALSTACK_ENDPOINT
        )
        self.partition = partition
        self.region_name = region_name
        self.sess = get_session()


class SageMakerAsyncBoto3Client(BaseAsyncBotoClient):
    def _create_sagemaker_client(self):
        # based on the Studio domain stage, we want to choose the sagemaker endpoint
        # rest of the services will use prod stages for non prod stages
        stage = InternalMetadataAdapter().get_stage()
        self.cfg = botocore.client.Config(
            connect_timeout=3,
            read_timeout=15,
            retries={"max_attempts": 2},
            use_dualstack_endpoint=USE_DUALSTACK_ENDPOINT
        )
        create_client_args = {
            "service_name": "sagemaker",
            "config": self.cfg,
            "region_name": self.region_name,
        }
        if stage.lower() != "prod":
            endpoint_stage = LOOSELEAF_STAGE_MAPPING[stage.lower()]
            create_client_args[
                "endpoint_url"
            ] = f"https://sagemaker.{endpoint_stage}.{self.region_name}.ml-platform.aws.a2z.com"

        return self.sess.create_client(**create_client_args)

    async def describe_training_job(self, job_name: str) -> Dict:
        async with self._create_sagemaker_client() as sm:
            return await sm.describe_training_job(TrainingJobName=job_name)

    async def create_training_job(self, input: Dict) -> Dict:
        try:
            async with self._create_sagemaker_client() as sm:
                return await sm.create_training_job(**input)
        except botocore.exceptions.ClientError as error:
            # TODO: Logger?
            print(f"Received ClientError: {str(error)}")
            # TODO: better error handling
            raise error

    async def list_tags(self, resource_arn: str) -> Dict:
        async with self._create_sagemaker_client() as sm:
            return await sm.list_tags(ResourceArn=resource_arn)

    async def search(self, input: Dict) -> Dict:
        try:
            async with self._create_sagemaker_client() as sm:
                return await sm.search(**input)
        except botocore.exceptions.ClientError as error:
            # TODO: Logger?
            print(f"Received ClientError: {str(error)}")
            # TODO: better error handling
            raise error

    async def stop_training_job(self, training_job_name: str) -> Dict:
        try:
            async with self._create_sagemaker_client() as sm:
                return await sm.stop_training_job(TrainingJobName=training_job_name)
        except botocore.exceptions.ClientError as error:
            # TODO: Logger?
            print(f"Received ClientError: {str(error)}")
            # TODO: better error handling
            raise error

    async def add_tags(self, resource_arn: str, tag_list: List[Dict]) -> Dict:
        try:
            async with self._create_sagemaker_client() as sm:
                return await sm.add_tags(ResourceArn=resource_arn, Tags=tag_list)
        except botocore.exceptions.ClientError as error:
            # TODO: Logger?
            print(f"Received ClientError: {str(error)}")
            # TODO: better error handling
            raise error

    async def delete_tags(self, resource_arn: str, tag_keys: List[str]):
        try:
            async with self._create_sagemaker_client() as sm:
                return await sm.delete_tags(ResourceArn=resource_arn, TagKeys=tag_keys)
        except botocore.exceptions.ClientError as error:
            # TODO: Logger?
            print(f"Received ClientError: {str(error)}")
            # TODO: better error handling
            raise error

    async def describe_lcc(self, lcc_arn: str):
        lcc_name = lcc_arn.split("studio-lifecycle-config/")[-1]

        async with self._create_sagemaker_client() as sm:
            return await sm.describe_studio_lifecycle_config(
                StudioLifecycleConfigName=lcc_name
            )

    async def list_domains(self):
        async with self._create_sagemaker_client() as sm:
            return await sm.list_domains()

    async def describe_domain(self, domain_id: str) -> Dict:
        if domain_id is None:
            return {}
        async with self._create_sagemaker_client() as sm:
            return await sm.describe_domain(DomainId=domain_id)

    async def describe_user_profile(
        self, domain_id: str, user_profile_name: str
    ) -> Dict:
        async with self._create_sagemaker_client() as sm:
            return await sm.describe_user_profile(
                DomainId=domain_id, UserProfileName=user_profile_name
            )

    async def describe_space(self, domain_id: str, space_name: str) -> Dict:
        async with self._create_sagemaker_client() as sm:
            return await sm.describe_space(DomainId=domain_id, SpaceName=space_name)

    async def describe_app(self, domain_id: str, space_name: str, app_type: str, app_name: str) -> Dict:
        async with self._create_sagemaker_client() as sm:
            return await sm.describe_app(DomainId=domain_id, SpaceName=space_name, AppType=app_type, AppName=app_name)

    async def create_pipeline(
        self,
        pipeline_name: str,
        pipeline_display_name: str,
        pipeline_description: str,
        pipeline_definition: str,
        role_arn: str,
        tags: List[Dict],
    ) -> Dict:
        async with self._create_sagemaker_client() as sm:
            return await sm.create_pipeline(
                PipelineName=pipeline_name,
                PipelineDisplayName=pipeline_display_name,
                PipelineDescription=pipeline_description,
                PipelineDefinition=pipeline_definition,
                RoleArn=role_arn,
                Tags=tags,
            )

    async def update_pipeline(
        self,
        pipeline_name: str,
        pipeline_display_name: str,
        pipeline_description: str,
        pipeline_definition: str,
        role_arn: str,
    ) -> Dict:
        async with self._create_sagemaker_client() as sm:
            return await sm.update_pipeline(
                PipelineName=pipeline_name,
                PipelineDisplayName=pipeline_display_name,
                PipelineDescription=pipeline_description,
                PipelineDefinition=pipeline_definition,
                RoleArn=role_arn,
            )

    async def describe_pipeline(self, pipeline_name: str) -> Dict:
        async with self._create_sagemaker_client() as sm:
            return await sm.describe_pipeline(
                PipelineName=pipeline_name,
            )

    async def list_pipeline_executions(self, pipeline_name: str) -> Dict:
        async with self._create_sagemaker_client() as sm:
            # TODO: use the next token to deal with pagination
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sagemaker.html#SageMaker.Client.get_paginator
            return await sm.list_pipeline_executions(
                PipelineName=pipeline_name,
            )

    async def delete_pipeline(self, pipeline_name: str) -> Dict:
        async with self._create_sagemaker_client() as sm:
            return await sm.delete_pipeline(
                PipelineName=pipeline_name,
            )

    async def stop_pipeline_execution(self, pipeline_execution_arn: str) -> Dict:
        async with self._create_sagemaker_client() as sm:
            return await sm.stop_pipeline_execution(
                PipelineExecutionArn=pipeline_execution_arn
            )

    async def describe_image(self, image_name: str) -> Dict:
         async with self._create_sagemaker_client() as sm:
            describe_image_version_args = {"ImageName": image_name}
            return await sm.describe_image(**describe_image_version_args)

    async def describe_image_version(
        self, image_name: str, image_version_number: int = None
    ) -> Dict:
        async with self._create_sagemaker_client() as sm:
            describe_image_version_args = {"ImageName": image_name}
            if image_version_number:
                describe_image_version_args["Version"] = image_version_number
            return await sm.describe_image_version(**describe_image_version_args)

    async def describe_app_image_config(self, app_image_config_name: str) -> Dict:
        async with self._create_sagemaker_client() as sm:
            return await sm.describe_app_image_config(
                AppImageConfigName=app_image_config_name
            )


def get_sagemaker_client() -> SageMakerAsyncBoto3Client:
    return SageMakerAsyncBoto3Client(get_partition(), get_region_name())


class S3AsyncBoto3Client:
    cfg: any
    partition: str
    region_name: str
    sess: AioSession

    def __init__(self, partition: str, region_name: str):
        self.cfg = botocore.client.Config(
            # TODO: Refine these values (currently copied from LooseLeafNb2Kg)
            connect_timeout=15,
            read_timeout=15,
            retries={"max_attempts": 2},
            use_dualstack_endpoint=USE_DUALSTACK_ENDPOINT
        )
        self.partition = partition
        self.region_name = region_name
        self.sess = get_session()

    def _create_s3_client(self):
        return self.sess.create_client(
            "s3",
            config=self.cfg,
            region_name=self.region_name,
        )

    async def get_bucket_location(self, bucket: str, accountId: str):
        async with self._create_s3_client() as s3:
            return await s3.get_bucket_location(
                Bucket=bucket, ExpectedBucketOwner=accountId
            )

    async def upload_file(
        self, file_name: str, bucket: str, key: str, aws_account_id: str, encrypt: bool
    ):
        async with self._create_s3_client() as s3:
            with open(file_name, "rb") as f:
                args = {
                    "Body": f,
                    "Bucket": bucket,
                    "Key": key,
                    "ExpectedBucketOwner": aws_account_id,
                }

                if encrypt:
                    args["ServerSideEncryption"] = "aws:kms"

                await s3.put_object(**args)

    async def delete_object(self, bucket: str, key: str):
        async with self._create_s3_client() as s3:
            await s3.delete_object(Bucket=bucket, Key=key)

    async def get_object(self, bucket: str, key: str) -> Dict:
        async with self._create_s3_client() as s3:
            return await s3.get_object(Bucket=bucket, Key=key)

    async def get_object_content(self, bucket: str, key: str) -> str:
        async with self._create_s3_client() as s3:
            response = await s3.get_object(Bucket=bucket, Key=key)
            return await response["Body"].read()
        
    async def list_objects(self, bucket: str, prefix: str) -> List[str]:
        async with self._create_s3_client() as s3:
            paginator = s3.get_paginator('list_objects_v2')
            params = {'Bucket': bucket, 'Prefix': prefix}
            page_iterator = paginator.paginate(**params)

            list_s3_objects = []
            async for page in page_iterator:
                contents = page.get('Contents', [])
                for content in contents:
                    list_s3_objects.append(content.get("Key", ""))

            return list_s3_objects

    async def create_bucket(self, bucket_name: str, region_name: str):
        async with self._create_s3_client() as s3:
            if region_name == "us-east-1":
                # If your region is us-east-1 then you simply run the command without the --location constraint
                # because by default bucket is created in the us-east-1 region
                return await s3.create_bucket(
                    Bucket=bucket_name,
                )

            else:
                # TODO: consolidate the edge case
                return await s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": region_name},
                )
            
    async def head_bucket(self, bucket_name: str):
        async with self._create_s3_client() as s3:
            return await s3.head_bucket(Bucket=bucket_name)

    async def enable_server_side_encryption_with_s3_keys(self, bucket_name: str):
        async with self._create_s3_client() as s3:
            await s3.put_bucket_encryption(
                Bucket=bucket_name,
                ServerSideEncryptionConfiguration={
                    "Rules": [
                        {
                            "ApplyServerSideEncryptionByDefault": {
                                "SSEAlgorithm": "aws:kms",
                            }
                        }
                    ]
                },
            )

    async def enable_versioning(self, bucket_name: str):
        async with self._create_s3_client() as s3:
            await s3.put_bucket_versioning(
                Bucket=bucket_name, VersioningConfiguration={"Status": "Enabled"}
            )

    async def get_bucket_encryption(self, bucket_name: str) -> Dict:
        async with self._create_s3_client() as s3:
            return await s3.get_bucket_encryption(Bucket=bucket_name)


def get_s3_client():
    return S3AsyncBoto3Client(get_partition(), get_region_name())


class EventBridgeAsyncBotoClient(BaseAsyncBotoClient):
    def _create_event_bridge_client(self):
        return self.sess.create_client(
            "events",
            config=self.cfg,
            region_name=self.region_name,
        )

    async def put_rule(
        self,
        name: str,
        description: str,
        schedule_expression: str,
        state: str,
        tags: Optional[List[Dict]] = None,
    ) -> Dict:
        async with self._create_event_bridge_client() as eb:
            if tags is None:
                tags = []

            return await eb.put_rule(
                Name=name,
                Description=description,
                ScheduleExpression=schedule_expression,
                State=state,
                Tags=tags,
            )

    async def put_targets(self, rule_name: str, targets: List[Dict]) -> Dict:
        async with self._create_event_bridge_client() as eb:
            return await eb.put_targets(Rule=rule_name, Targets=targets)

    async def describe_rule(self, name: str) -> Dict:
        async with self._create_event_bridge_client() as eb:
            return await eb.describe_rule(Name=name)

    async def disable_rule(self, name: str) -> None:
        async with self._create_event_bridge_client() as eb:
            await eb.disable_rule(Name=name)

    async def enable_rule(self, name: str) -> None:
        async with self._create_event_bridge_client() as eb:
            await eb.enable_rule(Name=name)

    async def remove_targets(self, rule_name: str, ids: List[str]) -> None:
        async with self._create_event_bridge_client() as eb:
            await eb.remove_targets(Rule=rule_name, Ids=ids)

    async def delete_rule(self, name: str) -> None:
        async with self._create_event_bridge_client() as eb:
            await eb.delete_rule(Name=name)

    async def list_tags_for_resource(self, resource_arn: str) -> Dict:
        async with self._create_event_bridge_client() as eb:
            return await eb.list_tags_for_resource(ResourceARN=resource_arn)

    async def tag_resource(self, resource_arn: str, tag_list: List[Dict]):
        async with self._create_event_bridge_client() as eb:
            await eb.tag_resource(ResourceARN=resource_arn, Tags=tag_list)

    async def untag_resource(self, resource_arn: str, tag_keys: List[str]):
        async with self._create_event_bridge_client() as eb:
            await eb.untag_resource(ResourceARN=resource_arn, TagKeys=tag_keys)


def get_event_bridge_client():
    return EventBridgeAsyncBotoClient(get_partition(), get_region_name())


class EC2AsyncBotoClient(BaseAsyncBotoClient):
    def _create_ec2_client(self):
        return self.sess.create_client(
            "ec2",
            config=self.cfg,
            region_name=self.region_name,
        )

    async def list_security_groups_by_vpc_id(self, vpc_id: str):
        async with self._create_ec2_client() as ec2:
            return await ec2.describe_security_groups(
                Filters=[
                    {
                        "Name": "vpc-id",
                        "Values": [vpc_id],
                    },
                ]
            )

    async def list_subnets_by_vpc_id(self, vpc_id: str):
        async with self._create_ec2_client() as ec2:
            return await ec2.describe_subnets(
                Filters=[
                    {
                        "Name": "vpc-id",
                        "Values": [vpc_id],
                    },
                ]
            )

    async def list_routetable_by_vpc_id(self, vpc_id: str):
        async with self._create_ec2_client() as ec2:
            return await ec2.describe_route_tables(
                Filters=[
                    {
                        "Name": "vpc-id",
                        "Values": [vpc_id],
                    },
                ]
            )


def get_ec2_client():
    return EC2AsyncBotoClient(get_partition(), get_region_name())


class STSAsyncBotoClient(BaseAsyncBotoClient):
    def _create_sts_client(self):
        session = botocore.session.Session()
        endpoint_resolver = session.get_component('endpoint_resolver')
        endpoint_data = endpoint_resolver.construct_endpoint('sts', self.region_name, use_dualstack_endpoint=USE_DUALSTACK_ENDPOINT)

        # Use the resolved endpoint if available; otherwise, default to global STS endpoint.
        endpoint_url = "https://sts.amazonaws.com"
        # Use dual stack STS global endpoint if dual stack is enabled otherwise use legacy global STS endpoint.
        # https://docs.aws.amazon.com/general/latest/gr/sts.html
        if USE_DUALSTACK_ENDPOINT:
            endpoint_url = "https://sts.api.aws.com"

        if endpoint_data and 'hostname' in endpoint_data:
            resolved_url = endpoint_data['hostname']
            if not resolved_url.startswith("https://"):
                resolved_url = "https://" + resolved_url
            endpoint_url = resolved_url

        return self.sess.create_client(
            "sts",
            config=self.cfg,
            region_name=self.region_name,
            endpoint_url=endpoint_url
        )

    # Used to get AWS account id
    # This API does not require special IAM permissions
    async def get_caller_identity(self) -> Dict:
        async with self._create_sts_client() as sts:
            return await sts.get_caller_identity()


def get_sts_client():
    return STSAsyncBotoClient(get_partition(), get_region_name())


class IAMAsyncBotoClient(BaseAsyncBotoClient):
    def _create_iam_client(self):
        return self.sess.create_client(
            "iam",
            config=self.cfg,
            region_name=self.region_name,
        )

    # Used to get AWS account id
    # This API does not require special IAM permissions
    async def list_entities_for_policy(self, policy_arn, max_items=None) -> Dict:
        async with self._create_iam_client() as iam:
            return await iam.list_entities_for_policy(
                PolicyArn=policy_arn,
                EntityFilter="Role",
                MaxItems=max_items,
            )

    async def list_role_arns_with_matching_prefix(self, prefix: str) -> List[str]:
        matching_role_arns = []
        async with self._create_iam_client() as iam:
            paginator = iam.get_paginator("list_roles")
            async for page in paginator.paginate():
                for role in page["Roles"]:
                    if role["RoleName"].startswith(prefix):
                        matching_role_arns.append(role["Arn"])
        return matching_role_arns

    async def list_role_arns_with_matching_prefix_timeout_wrapper(
        self, prefix: str, logger
    ) -> List[str]:
        try:
            return await asyncio.wait_for(
                self.list_role_arns_with_matching_prefix(prefix), timeout=IAM_TIMEOUT
            )
        except asyncio.TimeoutError:
            logger.info("IAM call timed out, returning empty response")
            return []


def get_iam_client():
    return IAMAsyncBotoClient(get_partition(), get_region_name())
