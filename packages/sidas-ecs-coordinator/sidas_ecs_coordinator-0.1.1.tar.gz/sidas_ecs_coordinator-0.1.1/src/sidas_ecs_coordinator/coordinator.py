import os

import boto3
from sidas.core import Coordinator, DefaultAsset

from .config import (
    SIDAS_ECS_COORDINATOR_CLUSTER_ENV_KEY,
    SIDAS_ECS_COORDINATOR_TASK_DEF_ENV_KEY,
    SIDAS_ECS_COORDINATOR_TASK_SECURITY_GROUP_ID_KEY,
    SIDAS_ECS_COORDINATOR_TASK_SUBNET_GROUP_ID_KEY,
    SIDAS_ECS_MATERIALIZER_CONTAINER_NAME_KEY,
)


class EcsCoordinator(Coordinator):
    def __init__(self, cron_expression: str | None = None) -> None:
        super().__init__(cron_expression=cron_expression)
        self.client = boto3.client("ecs")

    def trigger_materialization(self, asset: DefaultAsset) -> None:
        asset_id = asset.asset_id()

        self.client.run_task(
            cluster=os.environ[SIDAS_ECS_COORDINATOR_CLUSTER_ENV_KEY],
            launchType="FARGATE",
            taskDefinition=os.environ[SIDAS_ECS_COORDINATOR_TASK_DEF_ENV_KEY],
            group="Materializer",
            networkConfiguration={
                "awsvpcConfiguration": {
                    "subnets": os.environ[
                        SIDAS_ECS_COORDINATOR_TASK_SUBNET_GROUP_ID_KEY
                    ].split("."),
                    "securityGroups": [
                        os.environ[SIDAS_ECS_COORDINATOR_TASK_SECURITY_GROUP_ID_KEY]
                    ],
                    "assignPublicIp": "DISABLED",
                }
            },
            overrides={
                "containerOverrides": [
                    {
                        "name": os.environ[SIDAS_ECS_MATERIALIZER_CONTAINER_NAME_KEY],
                        "command": [
                            "sidas",
                            "materialize",
                            f"{asset_id}",
                        ],
                        "environment": [
                            {
                                "name": "ASSET_ID",
                                "value": asset_id,
                            }
                        ],
                    }
                ]
            },
        )

        # the task has been kicked off without an error, we can set the status
        asset.in_trigger_materialization()
