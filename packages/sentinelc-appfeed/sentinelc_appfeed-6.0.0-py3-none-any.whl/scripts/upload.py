from os import environ
import sys
import boto3


def get_env_setting(setting, default=None):
    """Get the environment setting or return exception"""
    try:
        return environ[setting]
    except KeyError:
        if default is None:
            print(
                "Error: the %s env variable is not set and has no default." % setting,
                file=sys.stderr,
            )
            sys.exit(1)

        return default


S3_REGION = get_env_setting("S3_REGION", default="nyc3")
S3_ENDPOINT_DOMAIN = get_env_setting("S3_ENDPOINT_DOMAIN", default="nyc3.digitaloceanspaces.com")
AWS_ACCESS_KEY_ID = get_env_setting("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = get_env_setting("AWS_SECRET_ACCESS_KEY")
BUCKETNAME = get_env_setting("BUCKETNAME", default="sentinelc")

S3_ENDPOINT_URL = f"https://{S3_ENDPOINT_DOMAIN}"


def init_s3_client():
    session = boto3.session.Session()
    return session.client(
        "s3",
        region_name=S3_REGION,
        endpoint_url=S3_ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )


filename = "feeds/demo-feed.json"
key = "apps/demo.json"
s3client = init_s3_client()
s3client.upload_file(filename, BUCKETNAME, key)
s3client.put_object_acl(ACL="public-read", Bucket=BUCKETNAME, Key=key)
