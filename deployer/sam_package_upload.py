#!/usr/bin/env python

import argparse
from subprocess import call

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-p", "--profile", action="store", dest="profile", default="deployer",
                        help="Credential profile")
    parser.add_argument("--s3-bucket", action="store", dest="s3_bucket", required=True,
                        help="The  name  of  the  S3 bucket where this command uploads the artifacts that are referenced in your template.")
    parser.add_argument("--s3-prefix", action="store", dest="s3_prefix", required=True,
                        help="A prefix name that the command adds to the artifacts' name when "
                             "it uploads them to the S3 bucket. The prefix name is a path name "
                             "(folder name) for the S3 bucket.")
    parser.add_argument("-d", "--deploy", action="store_true", dest="deploy_mode", default=False, help="Deploy stack after packaging with SAM")
    parser.add_argument("-s", "--stack-name", action="store", dest="stackname", default="",
                        help="Name of stack to be deleted (required if deploying stack after packaging)")
    args = parser.parse_args()
    return args.profile, args.stackname, args.deploy_mode, args.s3_bucket, args.s3_prefix


profile, stackname, deploy_mode, s3_bucket, s3_prefix = get_args()

if deploy_mode and len(stackname) == 0:
    print("Stack name must be provided for stack deployment")
    exit(-1)

package_cmd = "sam package --template-file deployer/garage_door_monitor.yaml " \
              "--profile {} " \
              "--s3-bucket {} " \
              "--s3-prefix {} " \
              "--output-template-file out/garage_door_monitor_output.yaml".format(profile, s3_bucket, s3_prefix)
status = call(package_cmd, shell=True)
if status != 0:
    print('SAM package failed')
    exit(-1)

if deploy_mode:
    deploy_cmd = "sam deploy --template-file out/garage_door_monitor_output.yaml " \
                 "--profile {} " \
                 "--capabilities CAPABILITY_IAM " \
                 "--stack-name {}".format(profile, stackname)
    exit(call(deploy_cmd, shell=True))
else:
    print('Skipping stack deployment')
