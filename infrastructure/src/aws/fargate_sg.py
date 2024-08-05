import pulumi
import pulumi_aws as aws

from utils import prefix_name

config = pulumi.Config()


class FargateSg:
    def __init__(self):
        sg_name = prefix_name("fargate-sg")
        self.security_group = aws.ec2.SecurityGroup(
            sg_name,
            name=sg_name,
            tags={
                "Name": sg_name,
            },
            vpc_id=config.require("vpc_id"),
        )

        aws.vpc.SecurityGroupEgressRule(
            f"{sg_name}-allow-all-ipv4-egress-rule",
            security_group_id=self.security_group.id,
            cidr_ipv4="0.0.0.0/0",
            ip_protocol="-1",
        )
