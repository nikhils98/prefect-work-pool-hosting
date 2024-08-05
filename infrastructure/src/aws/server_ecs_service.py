import json
import pulumi
import pulumi_aws as aws

from utils import prefix_name


class ServerEcsService:
    def __init__(
        self,
        cluster: aws.ecs.Cluster,
        execution_role: aws.iam.Role,
        instance: aws.ec2.Instance,
    ):
        container_volume_path = "/app/prefect"
        server_name = prefix_name("server")

        task_def = aws.ecs.TaskDefinition(
            f"{server_name}-task-def",
            family=server_name,
            network_mode="host",
            requires_compatibilities=["EC2"],
            execution_role_arn=execution_role.arn,
            container_definitions=json.dumps(
                [
                    {
                        "name": server_name,
                        "image": "prefecthq/prefect:2.20-python3.12",
                        "cpu": 512,
                        "memory": 512,
                        "portMappings": [
                            {"containerPort": 4200, "hostPort": 4200, "protocol": "tcp"}
                        ],
                        "mountPoints": [
                            {
                                "sourceVolume": "prefect",
                                "containerPath": container_volume_path,
                            }
                        ],
                        "command": [
                            "/opt/prefect/entrypoint.sh",
                            "prefect",
                            "server",
                            "start",
                        ],
                        "environment": [
                            {
                                "name": "PREFECT_SERVER_API_HOST",
                                "value": "0.0.0.0",
                            },
                            {"name": "PREFECT_HOME", "value": container_volume_path},
                        ],
                    }
                ]
            ),
            volumes=[
                {
                    "name": "prefect",
                    "dockerVolumeConfiguration": {
                        "scope": "shared",
                        "autoprovision": True,
                    },
                }
            ],
        )

        service = aws.ecs.Service(
            prefix_name("server-ecs-service"),
            name=server_name,
            cluster=cluster.id,
            launch_type="EC2",
            task_definition=task_def.arn,
            opts=pulumi.ResourceOptions(depends_on=[instance]),
            wait_for_steady_state=True,
            # Since we have set network_mode=host and defined a host port
            # we cannot run multiple tasks in the same instance.
            # DAEMON ensures there's only task running per ec2 instance.
            # So in a deployment, it first terminates the existing task
            # then starts the new one. If we want maximum availibility
            # then we must explore dynamic port mapping in aws and other
            # network modes such as awsvpc.
            scheduling_strategy="DAEMON",
        )
