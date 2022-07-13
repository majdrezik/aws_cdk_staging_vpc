#!/usr/bin/env python3
import os

import aws_cdk as cdk

from aws_cdk_stg.aws_cdk_stg_stack import AwsCdkStgStack
import aws_cdk_stg.config as config

app = cdk.App()
AwsCdkStgStack(app, "majdvpc-stg-stack", env=cdk.Environment(
    account=config.ACCOUNT,
    region=config.REGION
))

app.synth()
