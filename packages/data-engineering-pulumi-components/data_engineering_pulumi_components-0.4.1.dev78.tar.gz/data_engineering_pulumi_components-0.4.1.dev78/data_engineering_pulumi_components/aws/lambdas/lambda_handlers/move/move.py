import os
from urllib.parse import unquote_plus

import boto3

# Redirect to local AWS endpoints if running on Localstack
if "LOCALSTACK_HOSTNAME" in os.environ:
    print("Localstack detected - redirecting to locally hosted AWS")
    client = boto3.client(
        "s3", endpoint_url=f"http://{os.getenv('LOCALSTACK_HOSTNAME')}:4566"
    )
else:
    client = boto3.client("s3")


def handler(event, context):
    for record in event["Records"]:
        source_bucket = record["s3"]["bucket"]["name"]
        source_key = unquote_plus(record["s3"]["object"]["key"])
        destination_bucket = os.environ["DESTINATION_BUCKET"]
        destination_key = source_key

        client.copy_object(
            Bucket=destination_bucket,
            CopySource={"Bucket": source_bucket, "Key": source_key},
            Key=destination_key,
            ServerSideEncryption="AES256",
            ACL="bucket-owner-full-control",
        )

        client.delete_object(Bucket=source_bucket, Key=source_key)
