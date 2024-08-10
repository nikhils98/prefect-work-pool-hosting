import json
import pulumi
import pulumi_aws as aws

from utils import prefix_name

config = pulumi.Config()


class Ec2Instance:
    def __init__(self, cluster_name: str, fargate_sg_id: pulumi.Output[str]):
        # role with permissions to register and execute a Fargate task
        # which will be needed by the worker process.
        assume_role_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {
                        "Service": "ec2.amazonaws.com",
                    },
                    "Effect": "Allow",
                    "Sid": "",
                }
            ],
        }

        role_name = prefix_name("ec2-role")
        role = aws.iam.Role(
            role_name,
            name=role_name,
            assume_role_policy=json.dumps(assume_role_policy),
        )

        aws.iam.RolePolicyAttachment(
            f"{role_name}-container-service-pa",
            role=role.name,
            policy_arn="arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role",
        )

        # permissions required: task registration and execution
        aws.iam.RolePolicyAttachment(
            f"{role_name}-ecs-full-access-pa",
            role=role.name,
            policy_arn="arn:aws:iam::aws:policy/AmazonECS_FullAccess",
        )

        instance_profile = aws.iam.InstanceProfile(
            f"{role_name}-instance-profile", role=role.name
        )

        # Bash script that installs and runs the ecs-agent
        # which is required in a non Amazon linux distro to register the
        # EC2 instance in ECS. Without it ECS won’t be able to deploy
        # containers in the instance.
        # It also installs a desktop environment `xfce`
        # which we’ll need to access the server UI via RDP.
        # This script will only run when the instance is first initialized.
        user_data = f"""#!/bin/bash
          # Run update
          apt-get update

          # Install Docker
          apt-get install -y docker.io

          # Start Docker and enable it to run at startup
          systemctl start docker
          systemctl enable docker

          # Install the ECS agent
          docker run --name ecs-agent --detach=true --restart=unless-stopped --volume=/var/run/docker.sock:/var/run/docker.sock --volume=/var/log/ecs/:/log --volume=/var/lib/ecs/data:/data --net=host --env=ECS_LOGFILE=/log/ecs-agent.log --env=ECS_LOGLEVEL=info --env=ECS_DATADIR=/data --env=ECS_CLUSTER={cluster_name} amazon/amazon-ecs-agent:latest

          # Install xfce desktop environment
          apt install -y xfce4 xfce4-goodies

          # Install xrdp to allow rdp connections
          apt install -y xrdp
          echo "xfce4-session" | tee .xsession
          systemctl restart xrdp
    
          # Install firefox
          snap install firefox
      """

        # Note the ingress rules of the security group;
        # it allows incoming traffic only from the fargate security group.
        # This is needed to allow the flow process to be able to
        # communicate with the server.
        sg_name = prefix_name("ec2-sg")
        self.security_group = aws.ec2.SecurityGroup(
            sg_name,
            name=sg_name,
            description="Allow ALB inbound traffic and all outbound",
            tags={
                "Name": sg_name,
            },
            vpc_id=config.require("vpc_id"),
        )

        aws.vpc.SecurityGroupIngressRule(
            f"{sg_name}-allow-fargate-sg-egress-rule",
            security_group_id=self.security_group.id,
            from_port=80,
            ip_protocol="tcp",
            to_port=80,
            referenced_security_group_id=fargate_sg_id,
        )

        aws.vpc.SecurityGroupEgressRule(
            f"{sg_name}-allow-all-ipv4-egress-rule",
            security_group_id=self.security_group.id,
            cidr_ipv4="0.0.0.0/0",
            ip_protocol="-1",
        )

        # The instance that’ll run the server and worker processes.
        # Since both are rather lightweight we can run them in a
        # T4g.small instance. Of course if there are more internal users
        # accessing the server or several workers we may need a bigger machine.
        ec2_config = config.require_object("ec2")
        ec2_name = prefix_name("ec2")
        self.instance = aws.ec2.Instance(
            ec2_name,
            tags={"Name": ec2_name},
            instance_type=aws.ec2.InstanceType.T4G_SMALL,
            ami=ec2_config["ami_id"],
            key_name=ec2_config["key_pair"],
            user_data=user_data,
            iam_instance_profile=instance_profile.name,
            vpc_security_group_ids=[self.security_group.id],
            subnet_id=config.require("public_subnet_id"),
            root_block_device=aws.ec2.InstanceRootBlockDeviceArgs(volume_size=64),
            metadata_options=aws.ec2.InstanceMetadataOptionsArgs(
                http_endpoint="enabled", http_tokens="required"
            ),  # enable imdsv2
        )
