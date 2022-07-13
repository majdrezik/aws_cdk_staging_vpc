from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_ec2 as ec2,
    RemovalPolicy,
    aws_s3 as s3,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_elasticloadbalancing as elb,
)
from constructs import Construct

import aws_cdk.aws_elasticloadbalancingv2 as elbv2
import aws_cdk.aws_rds as rds

from . import config


class AwsCdkStgStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(
            self,
            id=config.VPC_PREFIX + config.ENV_NAME,  # majdvpc-stg
            cidr=config.VPC_CIDR,
            enable_dns_support=True,
            max_azs=config.MAX_AZS,
            # nat_gateway_provider=ec2.NatProvider.gateway(eip_allocation_ids=["52.55.202.92"]),
            nat_gateways=config.NUMBER_OF_NAT_GW,
            enable_dns_hostnames=True,
            subnet_configuration=[
                ###########################################
                #               Public Subnets
                ###########################################
                ec2.SubnetConfiguration(
                    name=config.PUBLIC_SUBNET_A,
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=config.SUBNET_CIDR_MASK,
                    map_public_ip_on_launch=True,
                    reserved=False
                ),
                ###########################################
                #               Private Subnets
                ###########################################
                ec2.SubnetConfiguration(
                    name=config.PRIVATE_SUBNET_A,
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT,
                    cidr_mask=config.SUBNET_CIDR_MASK,
                    reserved=False
                )
            ],
            vpc_name=config.VPC_PREFIX + config.ENV_NAME,
        )

        #######################################################################
        #                       Security Groups
        #######################################################################

        """
             2 security groups for the 2 kinds of EC2; public sg and private sg.
        """

        ec2_public_sg = ec2.SecurityGroup(
            self,
            id=config.EC2_PUBLIC_SECURITY_GROUP_ID,
            vpc=vpc,
            allow_all_outbound=True,
            description=config.EC2_PUBLIC_SECURITY_GROUP_NAME,
            security_group_name=config.EC2_PUBLIC_SECURITY_GROUP_NAME
        )

        ec2_private_sg = ec2.SecurityGroup(
            self,
            id=config.EC2_PRIVATE_SECURITY_GROUP_ID,
            vpc=vpc,
            allow_all_outbound=True,
            description=config.EC2_PRIVATE_SECURITY_GROUP_NAME,
            security_group_name=config.EC2_PRIVATE_SECURITY_GROUP_NAME
        )

        """
            security group for the LB
        """

        loadBalancer_sg = ec2.SecurityGroup(
            self,
            id=config.LB_SECURITY_GROUP_ID,
            vpc=vpc,
            allow_all_outbound=True,
            description=config.LB_SECURITY_GROUP_NAME,
            security_group_name=config.LB_SECURITY_GROUP_NAME
        )

        """
            Configure Inbound and Outbound Rules of SG
        """
        # ec2_public_sg.connections.allow_from(
        #     other=ec2.Peer.any_ipv4(),
        #     port_range=ec2.Port.tcp(config.PUBLIC_EC2_PORT),
        #     description="Public EC2 inbound"
        # )

        ec2_public_sg.add_ingress_rule(
            peer=ec2.Peer.security_group_id(
                security_group_id=loadBalancer_sg.security_group_id
            ),
            connection=ec2.Port.tcp(config.PUBLIC_EC2_PORT)
        )
        """
            Allow connections to the private EC2 instance only throught the LB. - from HTTP
        """
        # ec2_private_sg.connections.allow_from(
        #     other=ec2.Peer.security_group_id(
        #         # security_group_id=config.LB_SECURITY_GROUP_ID
        #         loadBalancer_sg.security_group_id
        #     ),
        #     port_range=ec2.Port.tcp(config.LB_LISTENER_HTTP_PORT),
        #     description="Private EC2 inbound"
        # )

        ec2_private_sg.add_ingress_rule(
            peer=ec2.Peer.security_group_id(
                security_group_id=loadBalancer_sg.security_group_id
            ),
            connection=ec2.Port.tcp(config.PRIVATE_EC2_PORT)
        )

        """
           Allow connections to the private EC2 instance only throught the LB. - from HTTPS
        """
        # ec2_private_sg.connections.allow_from(
        #     other=ec2.Peer.security_group_id(
        #         security_group_id=config.LB_SECURITY_GROUP_ID
        #     ),
        #     port_range=ec2.Port.tcp(config.LB_LISTENER_HTTPS_PORT),
        #     description="Private EC2 inbound"
        # )

        """
            Allow all traffic to LB from port 443 (HTTPS)
        """
        loadBalancer_sg.connections.allow_from(
            other=ec2.Peer.any_ipv4(),
            port_range=ec2.Port.tcp(config.LB_LISTENER_HTTPS_PORT),
            description="LB HTTPS inbound"
        )

        """
            Allow all traffic to LB from port 80 (HTTP)
        """
        loadBalancer_sg.connections.allow_from(
            other=ec2.Peer.any_ipv4(),
            port_range=ec2.Port.tcp(config.LB_LISTENER_HTTP_PORT),
            description="LB HTTP inbound"
        )

        """
            SG for the RDS instance
        """
        rds_sg = ec2.SecurityGroup(
            self,
            id=config.DB_SECURITY_GROUP_ID,
            vpc=vpc,
            allow_all_outbound=True,
            description=config.DB_SECURITY_GROUP_NAME,
            security_group_name=config.DB_SECURITY_GROUP_NAME
        )

        """
            Allow traffic to RDS db only through the private EC2 instance.
        """
        # rds_sg.connections.allow_from(
        #     other=ec2.Peer.security_group_id(
        #         security_group_id=config.EC2_PRIVATE_SECURITY_GROUP_ID
        #     ),
        #     port_range=ec2.Port.tcp(config.PRIVATE_EC2_PORT),
        #     description='allow traffic on port 3306 from the private EC2 instance security group',
        # )

        rds_sg.add_ingress_rule(
            peer=ec2.Peer.security_group_id(
                security_group_id=ec2_private_sg.security_group_id
            ),
            connection=ec2.Port.tcp(config.RDS_PORT)
        )

        #######################################################################
        #                           EC2 Instances
        #######################################################################

        """
             AMI configurations
        """
        amzn_linux = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
        )

        """
             Instance Role and SSM Managed Policy
        """
        role = iam.Role(self, "InstanceSSM", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))

        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"))

        """
           Public EC2 instance
        """
        public_instance = ec2.Instance(self, config.PUBLIC_EC2_ID,
                                       instance_name=config.VPC_NAME + '-' + config.PUBLIC_EC2_ID,
                                       instance_type=ec2.InstanceType(config.EC2_INSTANCE_TYPE),
                                       machine_image=amzn_linux,
                                       vpc=vpc,
                                       role=role,
                                       key_name=config.KEY_PAIR_NAME,
                                       security_group=ec2_public_sg,
                                       vpc_subnets=ec2.SubnetSelection(
                                           availability_zones=[
                                               config.AVAILABILITY_ZONE_1,
                                               # config.AVAILABILITY_ZONE_2
                                           ],
                                           subnet_type=ec2.SubnetType.PUBLIC
                                       )
                                       )

        """
            Private EC2 instance
        """
        private_instance = ec2.Instance(self, config.PRIVATE_EC2_ID,
                                        instance_name=config.VPC_NAME + '-' + config.PRIVATE_EC2_ID,
                                        instance_type=ec2.InstanceType(config.EC2_INSTANCE_TYPE),
                                        machine_image=amzn_linux,
                                        vpc=vpc,
                                        role=role,
                                        key_name=config.KEY_PAIR_NAME,
                                        security_group=ec2_private_sg,
                                        vpc_subnets=ec2.SubnetSelection(
                                            availability_zones=[
                                                config.AVAILABILITY_ZONE_1,
                                                # config.AVAILABILITY_ZONE_2
                                            ],
                                            subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT
                                        )
                                        )

        # When using CDK VPC construct, an Internet Gateway is created by default
        # whenever you create a public subnet. The default route is also setup for
        # the public subnet.
        # https://stackoverflow.com/questions/58812479/how-to-add-an-internet-gateway-to-a-vpc-using-aws-cdk

        #######################################################################
        #                           Load Balancer
        #######################################################################

        """
             create a new S3 bucket to store the ELB logs in it.
        """
        s3bucket = s3.Bucket(self,
                             id=config.S3_ELB_LOG_BUCKET_ID,
                             # block_public_access : by default, New buckets and objects don’t allow public access.
                             bucket_name=config.S3_ELB_LOG_BUCKET_NAME,
                             public_read_access=False  # by default, it's set to False.
                             )

        """
            grant access to read and write to the S3 bucket from the private isntances.
        """
        # s3bucket.grant_read_write(
        #     identity=private_instance.role
        # )

        my_custom_policy = iam.PolicyDocument(
            statements=[iam.PolicyStatement(
                actions=["s3:PutObject", "s3:PutObjectAcl", "s3:GetObject"
                         ],
                principals=[iam.ArnPrincipal(config.ELB_PRINCIPAL)],
                resources=["arn:aws:s3:::" + config.S3_ELB_LOG_BUCKET_NAME + "/*"]
            )]
        )

        cfn_bucket_policy = s3.CfnBucketPolicy(self, "MyCfnBucketPolicy",
                                               bucket=config.S3_ELB_LOG_BUCKET_NAME,
                                               policy_document=my_custom_policy)

        access_logging_policy_property = elb.CfnLoadBalancer.AccessLoggingPolicyProperty(
            enabled=True,
            s3_bucket_name=config.S3_ELB_LOG_BUCKET_NAME,
            # the properties below are optional
            # emit_interval=123,
            s3_bucket_prefix=config.S3_ELB_LOG_BUCKET_PREFIX
        )

        elb_health_check = elb.HealthCheck(
            port=config.LB_HEALTHCHECK_PORT,
            healthy_threshold=config.LB_HEALTHY_THRESHOLD,
            # interval=config.LB_INTERVAL,
            path=config.LB_HEALTHCHECK_PATH,
            protocol=config.LB_HEALTHCHECK_PROTOCOL,
            timeout=config.LB_HEALTHCHECK_TIMEOUT,
            unhealthy_threshold=config.LB_UNHEALTHY_THRESHOLD
        )

        elb_subnet_selection = ec2.SubnetSelection(
            availability_zones=[
                config.AVAILABILITY_ZONE_1,
                config.AVAILABILITY_ZONE_2
            ],
            subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT
        )

        loadBalancer = elb.LoadBalancer(self,
                                        id=config.LB_ID,
                                        vpc=vpc,
                                        access_logging_policy=access_logging_policy_property,
                                        cross_zone=True,
                                        health_check=elb_health_check,
                                        internet_facing=True,
                                        # listeners are added via the static method
                                        subnet_selection=elb_subnet_selection
                                        )

        loadBalancer.add_listener(external_port=config.LB_LISTENER_HTTPS_PORT,
                                  # allow_connections_from : by default, connections will be allowed from anywhere
                                  # external_protocol May be omitted if the external port is either 80 or 443.
                                  # external_protocol=[config.LB_LISTENER_HTTPS_EXTERNAL_PROTOCOL].
                                  # policy_names=,
                                  internal_port=config.PRIVATE_EC2_PORT,
                                  ssl_certificate_arn=config.SSL_CERTIFICATE_ARN,
                                  # ssl_certificate_id=config.SSL_CERTIFICATE_ID
                                  )

        # Didn't add this listener before
        loadBalancer.add_listener(external_port=config.LB_LISTENER_HTTP_PORT,
                                  # allow_connections_from : by default, connections will be allowed from anywhere
                                  # external_protocol May be omitted if the external port is either 80 or 443.
                                  # external_protocol=[config.LB_LISTENER_HTTPS_EXTERNAL_PROTOCOL].
                                  # policy_names=,
                                  # ssl_certificate_arn=config.SSL_CERTIFICATE_ARN,
                                  # ssl_certificate_id=config.SSL_CERTIFICATE_ID
                                  internal_port=config.PRIVATE_EC2_PORT,
                                  )

        #######################################################################
        #                          Route53 - Domain Name
        #######################################################################

        """ Creates record in hosted zone and assign it to load balancer"""
        route53.ARecord(self,
                        id=config.ROUTE53_ID,
                        target=route53.RecordTarget.from_alias(
                            targets.ClassicLoadBalancerTarget(loadBalancer)
                        ),
                        zone=route53.HostedZone(self,
                                                id=config.ROUTE53_HOSTED_ZONE_ID,
                                                zone_name=config.ROUTE53_ZONE_NAME
                                                ),
                        record_name=config.ROUTE53_RECORD_NAME
                        )

        #######################################################################
        #                           RDS - MySQL
        #######################################################################

        # rds_option_group = rds.OptionGroup(self,
        #                                    id=config.DB_OPTION_GROUP_ID,
        #                                    configurations=[],
        #                                    # configurations=[rds.OptionConfiguration(
        #                                    #     name=config.DB_OPTION_GROUP_NAME,
        #                                    #     port=config.DB_OPTION_GROUP_PORT,
        #                                    #     vpc=vpc
        #                                    # )],
        #                                    engine=rds.DatabaseInstanceEngine.mysql(
        #                                        version=rds.MysqlEngineVersion.VER_8_0_19)
        #                                    )
        #
        # rds_option_group.add_configuration(
        #     name=config.DB_OPTION_GROUP_NAME,
        #     port=config.DB_OPTION_GROUP_PORT,
        #     vpc=vpc
        # )

        """
           RDS - Database instance
        """

        # Allocated storage is by default : 100 GB
        rds_instance = rds.DatabaseInstance(self,
                                            id=config.DB_ID,
                                            credentials=rds.Credentials.from_username(
                                                username=config.DB_MASTER_USERNAME,
                                            ),
                                            storage_encrypted=True,
                                            engine=rds.DatabaseInstanceEngine.mysql(
                                                version=rds.MysqlEngineVersion.VER_8_0_19),
                                            database_name=config.DB_NAME,
                                            instance_type=ec2.InstanceType.of(
                                                ec2.InstanceClass.BURSTABLE3,
                                                ec2.InstanceSize.MEDIUM
                                            ),
                                            vpc=vpc,
                                            availability_zone=config.AVAILABILITY_ZONE_1,
                                            enable_performance_insights=False,
                                            instance_identifier=config.DB_NAME,
                                            max_allocated_storage=config.DB_MAX_ALLOCATED_STORAGE,
                                            multi_az=False,
                                            # option_group=rds_option_group,
                                            publicly_accessible=False,
                                            removal_policy=RemovalPolicy.DESTROY
                                            )

        # Rotate the master user password every 30 days
        # rds_instance.add_rotation_single_user()
