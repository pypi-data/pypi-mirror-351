import os
import json
import subprocess


def host_region_mapping():
    IRONMAN_CONFIG_PACKAGE_NAME = "IronmanUtilizationServiceConfigData"
    DEFAULT_RESOURCE_LIMITS_FILE_NAME = "default-resource-limits.json"
    HOST_REGION_MAPPING_FILE_NAME = "host_region_mapping.json"

    ironman_service_config_pkg = subprocess.check_output(
        ["brazil-path", f"[{IRONMAN_CONFIG_PACKAGE_NAME}]run.runtimefarm"],
        universal_newlines=True,
    ).strip()

    # The appconfig contains instance limits for alpha (us-west-2 only), beta (us-west-2 only), gamma and prod stages
    # Retrieving prod regions and the associated instance limits, as the both gamma and prod regions have the same instance limits
    # For other/unavailable stages/regions, the default instance limits are returned 
    # TODO: Add support for alpha, beta and gamma stages by creating a region mapping .json file for each stage
    region_mapping_path = os.path.join(ironman_service_config_pkg, "appconfig", "prod")
    regions = os.listdir(region_mapping_path)

    region_mapping = {}

    for region in regions:
        resource_limits_file_path = os.path.join(
            region_mapping_path, region, DEFAULT_RESOURCE_LIMITS_FILE_NAME
        )
        with open(resource_limits_file_path, "rb") as file:
            resource_limits = json.loads(file.read())
            default_resource_limit_instances = resource_limits.get(
                "ironman.resourceKeyToDefaultRiskAwareResourceLimit", {}
            )
            instance_details = [
                key[len("training-job/") :]
                for key, _ in default_resource_limit_instances.items()
                if key.startswith("training-job/ml")
            ]
            region_mapping[region] = instance_details

    # Available instance types is a public contract: https://aws.amazon.com/sagemaker/pricing/
    host_region_mapping_path = os.path.join(
        os.path.dirname(__file__),
        "amazon_sagemaker_jupyter_scheduler",
        HOST_REGION_MAPPING_FILE_NAME,
    )
    with open(host_region_mapping_path, "w") as file:
        json.dump(region_mapping, file)


if __name__ == "__main__":
    host_region_mapping()
