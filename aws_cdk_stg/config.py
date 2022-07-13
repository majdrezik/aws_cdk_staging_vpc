import aws_cdk as cdk

PROJECT_OWNER = 'majd'
ACCOUNT = "415102591172"
VPC_NAME = 'majdvpc-stg'
VPC_CIDR = '172.16.0.0/16'
MAX_AZS = 2
ENV_NAME = 'stg'
VPC_PREFIX = 'majdvpc-'
S3_ELB_LOG_BUCKET_NAME = 'majdvpc-stg-elb-log-bucket-s3'
S3_ELB_LOG_BUCKET_ID = 'majdvpc-stg-elb-log-bucket-s3'
S3_ELB_LOG_BUCKET_PREFIX = 'elb-logs'
INTERNET_GATEWAY = 'majdvpc-stg-ig'
NAT_GATEWAY = 'majdvpc-stg-nat'

REGION = 'us-west-2'  # Oregon
KEY_PAIR_NAME = ''
if REGION == 'us-west-2':
    KEY_PAIR_NAME = 'Majd-stg-kp'
elif REGION == 'us-west-1':
    KEY_PAIR_NAME = 'MajdKP-Ohio'
elif REGION == 'us-east-1':
    KEY_PAIR_NAME = 'MajdKP2'

NUMBER_OF_NAT_GW = 1
SUBNET_CIDR_MASK = 24

# PORTS

RDS_PORT = 3306
PUBLIC_EC2_PORT = 8080
PRIVATE_EC2_PORT = 8080
SSL_CERTIFICATE_ARN = 'arn:aws:acm:us-west-2:415102591172:certificate/30941231-a8e9-4660-b42d-cb7d3c4a1084'
#SSL_CERTIFICATE_ARN = "arn:aws:acm:us-east-1:415102591172:certificate/0ad3ae1d-8cae-4877-abd1-23966cba351b"
SSL_CERTIFICATE_ID = '0ad3ae1d-8cae-4877-abd1-23966cba351b'
PUBLIC_ROUTE_TABLE = 'majdvpc-stg-public-route-table'
PRIVATE_ROUTE_TABLE = 'majdvpc-stg-private-route-table'
PUBLIC_EC2_ID = 'public EC2'
PRIVATE_EC2_ID = 'private EC2'

# security groups
EC2_PRIVATE_SECURITY_GROUP_ID = 'majdvpc-stg-ec2-private-SG'
EC2_PUBLIC_SECURITY_GROUP_ID = 'majdvpc-stg-ec2-public-SG'
DB_SECURITY_GROUP_ID = 'majdvpc-stg-db-SG'

EC2_PRIVATE_SECURITY_GROUP_NAME = 'majdvpc-stg-ec2-private-SG'
EC2_PUBLIC_SECURITY_GROUP_NAME = 'majdvpc-stg-ec2-public-SG'
DB_SECURITY_GROUP_NAME = 'majdvpc-stg-db-SG'

# subnets and instances
PUBLIC_SUBNET_A = 'majdvpc-staging-public-subnet_a'
PRIVATE_SUBNET_A = 'majdvpc-staging-private-subnet_a'
PUBLIC_SUBNET_B = 'majdvpc-staging-public-subnet_b'
PRIVATE_SUBNET_B = 'majdvpc-staging-private-subnet_b'

PUBLIC_SUBNET_A_CIDR = '172.16.100.0/24'
PUBLIC_SUBNET_B_CIDR = '172.16.200.0/24'
PRIVATE_SUBNET_A_CIDR = '172.16.1.0/24'
PRIVATE_SUBNET_B_CIDR = '172.16.2.0/24'

# RDS config
DB_ID = "Majd-RDS-ID2"
DB_ENGINE = 'MYSQL'
DB_MASTER_USERNAME = 'majdrezik'
DB_NAME = 'majdPetclinicdb2'
DB_MAX_ALLOCATED_STORAGE = 200
DB_OPTION_GROUP_ID = 'MEMCACHED'
DB_OPTION_GROUP_NAME = 'rds-option-group'
DB_OPTION_GROUP_PORT = 1158
EC2_INSTANCE_TYPE = 't3.nano'

# Load balancer configurations
LB_SECURITY_GROUP_NAME = 'majdvpc-stg-lb-SG'
LB_SECURITY_GROUP_ID = 'majdvpc-stg-lb-SG'
LB_NAME = 'Majd-stg-loadBalancer'
LB_ID = 'Majd-stg-loadBalancer'
LB_LISTENER_HTTPS_PORT = 443
LB_LISTENER_HTTP_PORT = 80
LB_LISTENER_HTTP_EXTERNAL_PROTOCOL = cdk.aws_elasticloadbalancing.LoadBalancingProtocol.HTTP
LB_LISTENER_HTTPS_EXTERNAL_PROTOCOL = cdk.aws_elasticloadbalancing.LoadBalancingProtocol.HTTPS
LB_TARGET_PORT = 8080
LB_HEALTHCHECK_PORT = 8080
LB_HEALTHY_THRESHOLD = 3
LB_UNHEALTHY_THRESHOLD = 3
LB_INTERVAL = cdk.Duration.minutes(5)
LB_HEALTHCHECK_PATH = '/'
LB_HEALTHCHECK_PROTOCOL = cdk.aws_elasticloadbalancing.LoadBalancingProtocol.HTTP
LB_HEALTHCHECK_TIMEOUT = cdk.Duration.seconds(5)
AVAILABILITY_ZONE_1 = REGION+'b'
AVAILABILITY_ZONE_2 = REGION+'c'
ELB_ACCOUNT_ID = ''
if REGION == 'us-west-2':
    ELB_ACCOUNT_ID = '797873946194'
elif REGION == 'us-west-1':
    ELB_ACCOUNT_ID = '027434742980'
elif REGION == 'us-east-1':
    ELB_ACCOUNT_ID = '127311923021'
ELB_PRINCIPAL = 'arn:aws:iam::' + ELB_ACCOUNT_ID + ':root'
# Route53 configurations
ROUTE53_ID = 'Majdvpc-PetCLinicStaging'
ROUTE53_NAME = 'Majdvpc-PetCLinicStaging'
ROUTE53_TYPE = 'A'
ROUTE53_RECORD_NAME = PROJECT_OWNER + '-' + ENV_NAME + '-petclinic.devopslets.com'
ROUTE53_HOSTED_ZONE_ID = 'Z2CBEA9Q705SAP'
ROUTE53_ZONE_NAME = 'devopslets.com'
