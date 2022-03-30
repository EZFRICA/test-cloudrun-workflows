# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from fastapi import FastAPI
import os, json
import time

from google.cloud import workflows_v1beta
from google.cloud.workflows import executions_v1beta
from google.cloud.workflows.executions_v1beta.types import executions, Execution

app = FastAPI()


@app.post("/")
async def execute_workflow():
    
    project = os.environ.get('GOOGLE_CLOUD_PROJECT')
    location = os.environ.get('WORKFLOW_LOCATION')
    workflow = os.environ.get('WORKFLOW_NAME')
    
    """Execute a workflow and print the execution results."""
    # [START workflows_api_quickstart]
    workflows_argument = {}

    # TODO(developer): Uncomment these lines and replace with your values.
    # project = 'my-project-id'
    # location = 'us-central1'
    # workflow = 'myFirstWorkflow'

    if not project:
        raise Exception('GOOGLE_CLOUD_PROJECT env var is required.')

    # Set up API clients.
    execution_client = executions_v1beta.ExecutionsClient()
    workflows_client = workflows_v1beta.WorkflowsClient()

    # Construct the fully qualified location path.
    parent = workflows_client.workflow_path(project, location, workflow)

    # Execute the workflow.
    execution = Execution(argument = json.dumps(workflows_argument))
    response = execution_client.create_execution(parent=parent, execution=execution)
    print(f"Created execution: {response.name}")

    # Wait for execution to finish, then print results.
    execution_finished = False
    backoff_delay = 1  # Start wait with delay of 1 second
    print('Poll every second for result...')
    while (not execution_finished):
        execution = execution_client.get_execution(request={"name": response.name})
        execution_finished = execution.state != executions.Execution.State.ACTIVE

        # If we haven't seen the result yet, wait a second.
        if not execution_finished:
            print('- Waiting for results...')
            time.sleep(backoff_delay)
            backoff_delay *= 2  # Double the delay to provide exponential backoff.
        else:
            print(f'Execution finished with state: {execution.state.name}')
            print(execution.result)
            return execution.result
    # [END workflows_api_quickstart]

