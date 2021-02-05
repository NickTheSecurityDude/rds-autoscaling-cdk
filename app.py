#!/usr/bin/env python3

from aws_cdk import core

import boto3
import sys

client = boto3.client('sts')

region=client.meta.region_name

#if region != 'us-east-1':
#  print("This app may only be run from us-east-1")
#  sys.exit()

account_id = client.get_caller_identity()["Account"]

my_env = {'region': region, 'account': account_id}

from stacks.rds_stack import RDSStack

proj_name="proj-name"

app = core.App()

rds_stack=RDSStack(app, proj_name+"-rds",env=my_env)

app.synth()

# Tag all resources
for stack in [rds_stack]:
  core.Tags.of(stack).add("Project", proj_name)
  #core.Tags.of(stack).add("ProjectGroup", vars.project_vars['group_proj_name'])