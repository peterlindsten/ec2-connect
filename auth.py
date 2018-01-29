import boto3
import argparse
import os
import getpass


parser = argparse.ArgumentParser()
parser.add_argument('token')
args = parser.parse_args()

sts = boto3.client('sts')
caller = sts.get_caller_identity()
username = getpass.getuser()
response = sts.get_session_token(SerialNumber='arn:aws:iam::{}:mfa/{}'.format(caller['Account'],username),TokenCode=str(args.token))

print 'export AWS_ACCESS_KEY_ID="{}"'.format(response['Credentials']['AccessKeyId'])
print 'export AWS_SECRET_ACCESS_KEY="{}"'.format(response['Credentials']['SecretAccessKey'])
print 'export AWS_SESSION_TOKEN="{}"'.format(response['Credentials']['SessionToken'])

print 'echo "Done"'
