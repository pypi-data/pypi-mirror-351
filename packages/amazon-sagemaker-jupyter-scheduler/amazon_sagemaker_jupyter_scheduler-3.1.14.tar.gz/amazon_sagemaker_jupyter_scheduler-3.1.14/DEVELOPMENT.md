

## Local Development install

The commands below will install a development environment for
SMUnoSchedulerJupyterLabExtension locally. Before running these commands, you should ensure that NodeJS is
installed locally.

```bash
# Clone the brazil workspace to your local environment
brazil ws create -n SMUnoSchedulerJupyterLabExtension && \
    cd SMUnoSchedulerJupyterLabExtension && \
    brazil ws use -p SMUnoSchedulerJupyterLabExtension --vs SMUnoSchedulerJupyterLabExtension/development

# Change dir to the source folder
cd src/SMUnoSchedulerJupyterLabExtension/

# use conda to keep your local python environment safe
# 1. Install Conda: https://docs.conda.io/en/latest/miniconda.html
# 2. Create a Conda environment:
conda create -n SagemakerScheduler python=3.9 jupyter_packaging jupyterlab==4.0.5 -y && conda activate SagemakerScheduler # needed only once

brazil setup platform-support && \
bb release

# Install the project in editable mode
pip install -e ".[dev]"

# Link your development version of the extension with JupyterLab
jupyter labextension develop . --overwrite

# Server extension must be manually installed in develop mode
jupyter server extension enable amazon_sagemaker_jupyter_scheduler

# If this is your first time, install the NodeJS module dependencies
bb install

# Rebuild extension Typescript source after making changes
bb build:labextension:dev
```

You can watch the source directory and run JupyterLab at the same time in
different terminals to watch for changes in the extension's source and
automatically rebuild the extension.

```bash
# Watch the source directory in one terminal, automatically rebuilding when needed
npm run watch
# Run JupyterLab in another terminal
jupyter lab --SchedulerApp.scheduler_class=amazon_sagemaker_jupyter_scheduler.scheduler.SageMakerScheduler --SchedulerApp.environment_manager_class=amazon_sagemaker_jupyter_scheduler.environments.SagemakerEnvironmentManager
```

With the `watch` command running, every file change will be built immediately
and made available in your running JupyterLab. Refresh JupyterLab to load the
change in your browser (you may need to wait several seconds for the extension
to be rebuilt).

If you are running JupyterLab on a remote machine, you can additionally include these flags while starting the JupyterLab session. This will enable you to access the JupyterLab from your remote machine, on your local machine.
```
# Replace <PORT> with a port number of your choice
jupyter lab --SchedulerApp.scheduler_class=amazon_sagemaker_jupyter_scheduler.scheduler.SageMakerScheduler --SchedulerApp.environment_manager_class=amazon_sagemaker_jupyter_scheduler.environments.SagemakerEnvironmentManager --no-browser --port<PORT>
```
On your local machine, do the following:
```
# Replace <PORT> with the port number used in the previous step, replace <USERNAME> and <HOST_ADDRESS> accordingly
ssh -L 8080:localhost:<PORT>:localhost <USERNAME>@<HOST_ADDRESS>
```

### Testing your changes locally
You need to configure AWS credentials before you can test your changes. Run the following command:
```
aws configure
# or use
ada credentials update ...
```
Provide the Access Key ID, Secret Access Key, Default region name (eg., us-west-2) and Default output format (eg., json). You need to have the access key details of an IAM User with necessary permissions.
If you do not have an IAM User with the required permissions, then create one with permissions similar to the ones mentioned in [this article](https://aws.amazon.com/blogs/machine-learning/schedule-your-notebooks-from-any-jupyterlab-environment-using-the-amazon-sagemaker-jupyterlab-extension/).
<br> <br>
Once the AWS credentials are configured, you are ready to test your changes.
## SageMaker Studio Development install
Start by building your changes into a tarball from your development environment.
```
brazil setup platform-support
brazil-build release
```
In `build/dist/` directory, you will be able to find a file with the extension `.tar.gz`. Upload this tarball to SageMaker Studio.
<br> <br>
Open a new terminal window and follow these steps to install your development version of the extension.
```
# Activate studio conda environment
conda activate studio

# Uninstall any older version
pip uninstall amazon_sagemaker_jupyter_scheduler

# Restart the jupyter server
restart-jupyter-server

# Refresh your browser after the above step, you should see that the extension icon no longer exists in notebook
# Open the terminal, and activate conda environment again
conda activate studio

# Install your development version of the extension
pip install amazon_sagemaker_jupyter_scheduler-x.x.x.tar.gz

# Restart the jupyter server
restart-jupyter-server

# Refresh your browser again, and check for the extension in a notebook
# You can also see the package version using pip
pip show amazon_sagemaker_jupyter_scheduler
```

## Testing scenarios
### Manually verify sanity. Follow these steps in any prod region for both private and shared spaces.
-  Test Create Job functionality:
    1. When clicking on Create Job, it should create a new job successfully.
    2. After clicking on Create Job, the job should be displayed in the List Jobs tab.
    3. After successful completion of job, download should fetch the output and logs.
-  Test Create Job Definition functionality:
    1. Select Run on Schedule in the create job form, and select an interval (Run every minute, etc.)
    2. Make sure the created job definition is showing in list job definition page
    3. After successful completion of job, download should fetch the output and logs
    4. Click on the job definition from the list and create a new job from definition by clicking on `Run Job`. Verify if a new job is created and runs successfully.
- Test the additional files packaging feature:
    1. Create a new notebook which accesses a local file, such as a text file and read its contents from one of the cells. Use this notebook to create new job.
    2. On the create job page, check the input folder check box.
    3. Click on Create Job, it should create and execute a new job successfully. Test the download functionality by clicking on the download button - it should have downloaded all the files in the notebook input folder.
    4. Repeat the same steps above by creating a job definition.
    5. Click on the created job/ job definition. On the job details and job definition details page, check if "Ran with input folder" field has value "Yes".


## Development uninstall

```bash
pip uninstall amazon_sagemaker_jupyter_scheduler
```



## Host Region update

Run this command -`python build-tools/get_host_mapping.py` from root of the project to update the host_region_mapping.json file.
This will read the sagemaker latest pricing pages and update the host types. This should be run periodically until we get a dynamic api to get the host type for a region.

