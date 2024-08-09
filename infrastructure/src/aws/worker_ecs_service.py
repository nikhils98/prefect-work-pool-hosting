import json
import pulumi
import pulumi_aws as aws

from utils import prefix_name

config = pulumi.Config()


class WorkerEcsService:
    def __init__(
        self,
        cluster: aws.ecs.Cluster,
        execution_role: aws.iam.Role,
        server: aws.ecs.Service,
    ):
        flow = "mean_and_median"
        server_host = "http://localhost"

        worker_name = prefix_name("worker")

        task_def = aws.ecs.TaskDefinition(
            f"{worker_name}-task-def",
            family=worker_name,
            network_mode="host",
            requires_compatibilities=["EC2"],
            execution_role_arn=execution_role.arn,
            container_definitions=json.dumps(
                [
                    {
                        "name": worker_name,
                        "image": "prefecthq/prefect:2.20-python3.12",
                        "cpu": 128,
                        "memory": 128,
                        "command": [
                            "/bin/sh",
                            "-c",
                            f"pip install prefect-aws && prefect worker start --pool {flow} --type ecs",
                        ],
                        "environment": [
                            {
                                "name": "PREFECT_API_URL",
                                "value": f"{server_host}/api",
                            },
                        ],
                    }
                ]
            ),
        )

        self.service = aws.ecs.Service(
            prefix_name("worker-ecs-service"),
            name=worker_name,
            cluster=cluster.id,
            scheduling_strategy="DAEMON",
            launch_type="EC2",
            task_definition=task_def.arn,
            opts=pulumi.ResourceOptions(depends_on=[server]),
        )
