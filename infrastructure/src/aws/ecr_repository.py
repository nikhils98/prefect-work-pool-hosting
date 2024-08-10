import json
import pulumi_aws as aws

from utils import prefix_name


# Note the repository name is simply prefix_name()
# The idea here is that in future we may build and
# deploy multiple flows and we can upload all of them
# in the same repository, differentiating with tag
# such as mean_and_median-latest
class EcrRepository:
    def __init__(self) -> None:
        repo_name = prefix_name()
        resource_name = prefix_name("ecr-repository")

        self.repo = aws.ecr.Repository(
            resource_name,
            name=repo_name,
        )

        aws.ecr.LifecyclePolicy(
            f"{resource_name}-lifecycle-policy",
            repository=self.repo.name,
            policy=json.dumps(
                {
                    "rules": [
                        {
                            "rulePriority": 1,
                            "description": "Expire older images",
                            "selection": {
                                "tagStatus": "tagged",
                                "tagPatternList": ["mean_and_median*"],
                                "countType": "imageCountMoreThan",
                                "countNumber": 20,
                            },
                            "action": {"type": "expire"},
                        }
                    ]
                }
            ),
        )
