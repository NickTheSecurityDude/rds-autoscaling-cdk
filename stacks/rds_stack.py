##############################################################
#
# rds_stack.py
#
# Resources:
#  1 lambda functions (code in /lambda folder (from_asset))
#
##############################################################

from aws_cdk import (
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_applicationautoscaling as autoscale,
    core
)


class RDSStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # get acct id for policies
        # acct_id=env['account']

        # creates a new vpc, subnets, 2 nat gateways, etc
        vpc = ec2.Vpc(self, "VPC")

        # mocking vpc from my environment
        #vpc = ec2.Vpc.from_lookup(self, "nonDefaultVpc", vpc_id="vpc-9931a0fc")

        self._rds_subnet_group = rds.SubnetGroup(self, 'RdsSubnetGroup',
                                                 description="aaa",
                                                 subnet_group_name='aurora-mysql',
                                                 vpc_subnets=ec2.SubnetSelection(
                                                     subnet_type=ec2.SubnetType.PRIVATE),
                                                 vpc=vpc
                                                 )

        # create the RDS cluster
        self._rds_cluster = rds.DatabaseCluster(self, "RDS Cluster",
                                                cluster_identifier="rds-test",
                                                engine=rds.DatabaseClusterEngine.AURORA_MYSQL,
                                                instance_props=rds.InstanceProps(
                                                    vpc=vpc,
                                                    instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2,
                                                                                      ec2.InstanceSize.SMALL),
                                                ),
                                                port=3306,
                                                default_database_name="test",
                                                subnet_group=self._rds_subnet_group
                                                )

        # enable autoscaling for rds
        # 3 servers maximum
        # scale on 1% cpu for testing, 50% normally

        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_applicationautoscaling/ScalableTarget.html
        self._scaling_target = autoscale.ScalableTarget(self, "Scaling Target",
                                                        max_capacity=3,
                                                        min_capacity=1,
                                                        resource_id='cluster:' + self._rds_cluster.cluster_identifier,
                                                        scalable_dimension='rds:cluster:ReadReplicaCount',
                                                        service_namespace=autoscale.ServiceNamespace.RDS
                                                        )

        self._scale_policy = autoscale.TargetTrackingScalingPolicy(self, "Tracking Scaling Policy",
                                                                   policy_name='thisisscalingpolicyname',
                                                                   target_value=1,
                                                                   predefined_metric=autoscale.PredefinedMetric.RDS_READER_AVERAGE_CPU_UTILIZATION,
                                                                   scaling_target=self._scaling_target,
                                                                   scale_in_cooldown=core.Duration.minutes(5),
                                                                   scale_out_cooldown=core.Duration.minutes(5), )
