import json
import pulumi_aws as aws

from utils import prefix_name


class EcsTaskExecutionRole:
    def __init__(self):
        role_name = prefix_name("ecs-task-execution-role")
        self.role = aws.iam.Role(
            role_name,
            name=role_name,
            assume_role_policy=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"Service": "ecs-tasks.amazonaws.com"},
                            "Action": "sts:AssumeRole",
                        }
                    ],
                }
            ),
        )

        aws.iam.RolePolicyAttachment(
            f"{role_name}-ecr-full-access-pa",
            role=self.role.name,
            policy_arn="arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess",
        )

        aws.iam.RolePolicyAttachment(
            f"{role_name}-cwl-full-access-pa",
            role=self.role.name,
            policy_arn="arn:aws:iam::aws:policy/CloudWatchLogsFullAccess",
        )

        aws.iam.RolePolicyAttachment(
            f"{role_name}-ecs-task-exec-pa",
            role=self.role.name,
            policy_arn="arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
        )
