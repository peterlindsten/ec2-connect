# ec2-connect

Utility to connect to windows instances on ec2

## Installation
clone repo
python -m pip install -r requirements.txt

## Usage
```
usage: connect.py [-h] [--region REGION] [--keyfile KEYFILE]
                     [--pw-to-clipboard] [--profile PROFILE] [--no-rdp]
                     instance_name
   
   positional arguments:
     instance_name         Name tag of the instance to connect to
   
   optional arguments:
     -h, --help            show this help message and exit
     --region REGION, -r REGION
                           Region to connect to. Example: us-west-2
     --keyfile KEYFILE, -k KEYFILE
                           Path to the keyfile, REQUIRED if env var
                           EC2_CONNECT_KEYFILE is not set
     --pw-to-clipboard, -c
                           Copies password to clipboard instead of writing to rdp
                           file. Useful when GPO blocks rdp files with passwords.
     --profile PROFILE, -p PROFILE
                           Set AWS credentials profile
     --no-rdp, -n          Don't launch Remote Desktop
```

If you need to use MFA, there are helper scripts for sh environments (git-bash, mingw, cygwin(untested), etc)

```
./auth.sh <Timed One-time password>
```
Example
`./auth.sh 012345`

This only works for virtual MFAs, but if you have a hardware MFA, it shouldn't be too difficult to modify auth.py with
 your devices ID

## Note
If .rdp password encryption is wanted, make sure site-packages/pywin32_system32 is on PATH:  
`export PATH=/c/Python27/Lib/site-packages/pywin32_system32:$PATH`  
Else you can simply use the `-c` switch

If you see `DLL load failed: The specified module could not be found.` then this is what is wrong