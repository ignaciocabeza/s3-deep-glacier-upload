import logging
import os
import sys
import threading
import ntpath
import configparser

import boto3
from botocore.exceptions import ClientError
from boto3.s3.transfer import TransferConfig
from rich.console import Console
from rich.prompt import Prompt
from rich import print

class ProgressPercentage(object):

    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()

console = Console()

def upload_file(file_name, bucket, access_key, secret_key, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )

    try:
        config = TransferConfig(use_threads=False)
        extra_args = {'StorageClass': 'DEEP_ARCHIVE', 'ACL': 'bucket-owner-full-control'}
        response = s3_client.upload_file(file_name, bucket, object_name, ExtraArgs=extra_args, Config=config, Callback=ProgressPercentage(file_name))
    except ClientError as e:
        logging.error(e)
        return False

    return True

if __name__ == "__main__":

    parser = configparser.ConfigParser()
    parser.read('./aws-credentials.ini')
    if 'default' not in parser.sections():
        raise Exception('Bad configuration file')
    
    if 'aws_access_key_id' not in parser['default'] or \
       'aws_secret_access_key' not in parser['default'] or \
       'aws_bucket_name' not in parser['default']:
       raise Exception('Bad configuration file')

    aws_access_key = parser['default']['aws_access_key_id']
    aws_access_secret_key = parser['default']['aws_secret_access_key']
    bucket_name = parser['default']['aws_bucket_name']

    s3_folder = Prompt.ask("Enter S3 folder (without `/` at beginning and end)")
    to_upload = Prompt.ask("Enter file path")

    exclude = ['.DS_Store']

    if os.path.isdir(to_upload):
        files = [x for x in os.listdir(to_upload) if x not in exclude]
        for index, file in enumerate(files):
            object_name = f'{s3_folder}/{file}'
            print(f'File {index+1} of {len(files)}')
            print(f'Destination: {object_name}')

            # upload file
            response = upload_file(os.path.join(to_upload, file), bucket_name, aws_access_key, aws_access_secret_key, object_name)
            if response:
                print(f'Succeed')
            else: 
                print(f'Failed')
    else:
        basename = ntpath.basename(to_upload)
        object_name = f'{s3_folder}/{basename}'
        print(f'Destination: {object_name}')
        response = upload_file(to_upload, bucket_name, aws_access_key, aws_access_secret_key, object_name)

        if response:
            print(f'Succeed')
        else: 
            print(f'Failed')
