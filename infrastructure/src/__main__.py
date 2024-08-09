from aws.ecs_cluster import EcsCluster
from aws.ecr_repository import EcrRepository
from aws.ec2_instance import Ec2Instance
from aws.fargate_sg import FargateSg
from aws.ecs_task_execution_role import EcsTaskExecutionRole
from aws.server_ecs_service import ServerEcsService
from aws.worker_ecs_service import WorkerEcsService

ecs_cluster = EcsCluster()
ecr_repository = EcrRepository()
fargate_sg = FargateSg()
ec2_instance = Ec2Instance(
    cluster_name=ecs_cluster.cluster_name, fargate_sg_id=fargate_sg.security_group.id
)
ecs_task_execution_role = EcsTaskExecutionRole()
server_ecs_service = ServerEcsService(
    cluster=ecs_cluster.cluster,
    execution_role=ecs_task_execution_role.role,
    instance=ec2_instance.instance,
)
worker_ecs_service = WorkerEcsService(
    cluster=ecs_cluster.cluster,
    execution_role=ecs_task_execution_role.role,
    server=server_ecs_service.service,
)
