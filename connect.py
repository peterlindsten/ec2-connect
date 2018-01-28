import argparse
import base64
import binascii
import os
import subprocess
import sys

import boto3
import rsa
import win32crypt


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('instance_name', help='Name tag of the instance to connect to')
    parser.add_argument('--region', '-r', dest='region', help='Region to connect to. Example: us-west-2')
    parser.add_argument('--keyfile', '-k', dest='keyfile',
                        help='Path to the keyfile, REQUIRED if env var EC2_CONNECT_KEYFILE is not set')
    parser.add_argument('--pw-to-clipboard', '-c', dest='clipboard', action='store_true',
                        help='Copies password to clipboard instead of writing to rdp file. Useful when'
                             ' GPO blocks rdp files with passwords.')
    parser.add_argument('--profile', '-p', dest='profile', help='Set AWS credentials profile')
    parser.add_argument('--no-rdp', '-n', dest='no_rdp', action='store_true', help="Don't launch Remote Desktop")

    args = parser.parse_args(argv)
    ensure_keyfile(args)

    ec2 = make_ec2_conn(args)

    iid, ip = get_iid_ip(args, ec2)

    pw = get_password(args, ec2, iid)

    rdp_file_path = make_rdp_file(args, ip, pw)

    if not args.no_rdp:
        subprocess.Popen(['mstsc.exe', os.path.abspath(rdp_file_path)])


def make_rdp_file(args, ip, pw):
    rdp_contents = 'auto connect:i:1\n'
    rdp_contents += 'full address:s:{}\n'.format(ip)
    rdp_contents += 'username:s:Administrator\n'
    if (args.clipboard):
        clip = subprocess.Popen(['clip.exe'], stdin=subprocess.PIPE)
        clip.communicate(pw)
        clip.wait()
    else:
        encrypted = crypt32_protect(pw)
        if not encrypted:
            raise Exception('Crypt32 failed')
        rdp_contents += 'password 51:b:{}\n'.format(encrypted)
    rdp_file_path = ip + '.rdp'
    with open(rdp_file_path, mode='w') as rdp_file:
        rdp_file.write(rdp_contents)
    return rdp_file_path


def get_password(args, ec2, iid):
    pw_response = ec2.get_password_data(InstanceId=iid)
    pw_data = pw_response['PasswordData']
    if not pw_data:
        raise Exception('Empty password. Instance not ready yet?')
    pw = rsa_decrypt(pw_data, args.keyfile)
    return pw


def get_iid_ip(args, ec2):
    response = ec2.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': [args.instance_name]}])
    reservations = response['Reservations']
    if reservations:
        instances = map(lambda x: x['Instances'], reservations).pop()
        if instances:
            instance = instances.pop()
            if not instance['Platform'] == 'windows':
                raise Exception('Non-windows instance detected')
            ip = instance["PublicIpAddress"]
            iid = instance["InstanceId"]
        else:
            raise Exception('No instances found')
    else:
        raise Exception('No reservations/instances found')
    if not iid:
        raise Exception('InstanceId empty')
    if not ip:
        raise Exception('Instance does not have a public IP')
    return iid, ip


def make_ec2_conn(args):
    if args.profile:
        boto3.setup_default_session(profile_name=args.profile)
    if args.region:
        ec2 = boto3.client('ec', region_name=args.region)
    else:
        ec2 = boto3.client('ec2')
    return ec2


def ensure_keyfile(args):
    env_keyfile = os.getenv('EC2_CONNECT_KEYFILE')
    if not args.keyfile:
        args.keyfile = env_keyfile
    if not args.keyfile:
        raise Exception('No keyfile specified')


def rsa_decrypt(ciphertext, keyfile):
    with open(keyfile) as pk_file:
        pk = rsa.PrivateKey.load_pkcs1(pk_file.read())
    encryptedData = base64.b64decode(ciphertext)
    plaintext = rsa.decrypt(encryptedData, pk)
    return plaintext


def crypt32_protect(plaintext):
    pwdHash = win32crypt.CryptProtectData(unicode(plaintext),u'psw',None,None,None,0x1)
    return binascii.hexlify(pwdHash)


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except Exception, e:
        print e.message
