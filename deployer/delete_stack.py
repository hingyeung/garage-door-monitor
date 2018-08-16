#!/usr/bin/env python
import boto3
from botocore.exceptions import ClientError
import argparse
import logging

# To delete a Garage Door Monitor Stack:
# 1. delete all previous version of the IoT policy created as part of this stack
# 2. detach the IoT policy from all certificates
# 3. delete the stack

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--stack-name", action="store", required=True, dest="stackname",
                        help="Name of stack to be deleted")
    parser.add_argument("-p", "--profile", action="store", dest="profile", default="deployer",
                        help="Credential profile")
    args = parser.parse_args()
    return args.profile, args.stackname


def delete_previous_policy_versions(policyName):
    for policy_version in (filter(lambda version: version['isDefaultVersion'] == False,
                                  iot_client.list_policy_versions(policyName=policyName)['policyVersions'])):
        # delete policy version
        logger.info("Deleting policy {} version {}".format(policyName, policy_version['versionId']))
        iot_client.delete_policy_version(policyName=policyName, policyVersionId=policy_version['versionId'])


def detach_policy_from_all_certificates(policyName):
    certificatesToDetach = iot_client.list_targets_for_policy(policyName=policyName)['targets']
    for certificate in certificatesToDetach:
        logger.info("Detaching policy {} from certifcate {}".format(policyName, certificate))
        iot_client.detach_policy(policyName=policyName, target=certificate)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
profile, stackName = get_args()
session = boto3.Session(profile_name=profile)

cf_client = session.client('cloudformation')
iot_client = session.client('iot')

try:
    # get IoT policy created by this stack
    logger.info("Preparing to delete stack {}".format(stackName))
    stack = cf_client.describe_stacks(StackName=stackName)['Stacks'][0]
    policyName = next(output for output in stack['Outputs']
                      if output['OutputKey'] == 'GarageDoorMonitorIoTPolicy')['OutputValue']

    # delete all previous versions of this policy
    delete_previous_policy_versions(policyName)

    # get all certificates that are attached to this policy
    detach_policy_from_all_certificates(policyName)

    # delete the stack
    logger.info("Deleting stack {}".format(stackName))
    cf_client.delete_stack(StackName=stackName)

except ClientError as error:
    logger.error(error)
    exit(-1)


