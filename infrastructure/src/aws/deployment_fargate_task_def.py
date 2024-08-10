import json
import pulumi
import pulumi_aws as aws

from utils import prefix_name

config = pulumi.Config()
aws_config = pulumi.Config("aws")


class DeploymentFargateTaskDef:
    def __init__(
        self,
        execution_role_arn: pulumi.Output[str],
        server_ip: pulumi.Output[str],
        repo_url: pulumi.Output[str],
    ):
        name = prefix_name("deployment")
        flow = "mean_and_median"

        family = f"{name}-{flow}"

        aws.ecs.TaskDefinition(
            f"{family}-task-def",
            network_mode="awsvpc",
            family=family,
            requires_compatibilities=["FARGATE"],
            cpu=256,
            memory=512,
            runtime_platform=aws.ecs.TaskDefinitionRuntimePlatformArgs(
                operating_system_family="LINUX",
                cpu_architecture="X86_64",
            ),
            execution_role_arn=execution_role_arn,
            container_definitions=pulumi.Output.all(repo_url, server_ip).apply(
                lambda args: json.dumps(
                    [
                        {
                            "name": family,
                            "image": f"{args[0]}:{flow}-latest",
                            "essential": True,
                            "environment": [
                                {
                                    "name": "PREFECT_API_URL",
                                    "value": f"http://{args[1]}:4200/api",
                                },
                                {"name": "AWS_ECR_REPOSITORY", "value": args[0]},
                            ],
                            "logConfiguration": {
                                "logDriver": "awslogs",
                                "options": {
                                    "awslogs-create-group": "true",
                                    "awslogs-group": "prefect",
                                    "awslogs-region": aws_config.require("region"),
                                    "awslogs-stream-prefix": family,
                                },
                            },
                        }
                    ]
                )
            ),
        )
