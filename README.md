# S3 Deep Glacier Uploader tool

## Prerequisites

* Have a AWS account and S3 Bucket

## Instalation & Configuration

```
pipenv install
```

Create a aws-credentials.ini file with the following format:
```
[default]
aws_access_key_id=YOUR_AWS_ACCESS_KEY
aws_secret_access_key=YOUR_AWS_SECRET_KEY
aws_bucket_name=YOUR_BUCKET_NAME
```

## Use

```
pipenv run app
```

1) The tool will ask `Enter S3 folders`. Write your desired path of folder ex.: photos/2019/02
2) Next question is `Enter file path`. Write entire file path of the file that you want to upload. (not tested in windows)

This script is going to upload your file only in Storage Class `DEEP_ARCHIVE`

Done!
