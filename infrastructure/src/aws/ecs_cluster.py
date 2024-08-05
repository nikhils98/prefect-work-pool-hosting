import pulumi_aws as aws

from utils import prefix_name


class EcsCluster:
    def __init__(self) -> None:
        self.cluster_name = prefix_name("ecs-cluster")
        self.cluster = aws.ecs.Cluster(
            self.cluster_name,
            name=self.cluster_name,
            settings=[
                aws.ecs.ClusterSettingArgs(name="containerInsights", value="enabled")
            ],
        )
