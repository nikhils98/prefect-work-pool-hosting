import json
import pulumi_aws as aws

from utils import prefix_name


# This is the role that we’ll assign to server, worker, flow processes
# as well as the deployment task. Ideally this can be
# broken down into more granular permissions
# and perhaps not all 4 of the processes require the same
# permissions at all so we’d have different roles in that case.
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
