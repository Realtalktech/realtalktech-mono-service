import boto3

# Configuration
AWS_ACCESS_KEY_ID = 'AKIAQ3EGPNN5DV6E4BAZ'
AWS_SECRET_ACCESS_KEY = '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'
S3_BUCKET = 'vendor-logos-bucket'

# Create an S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

def empty_s3_bucket(bucket_name):
    # First, delete all objects in the bucket
    response = s3.list_objects_v2(Bucket=bucket_name)
    while 'Contents' in response:
        print(f"Deleting {len(response['Contents'])} objects...")
        delete = {'Objects': [{'Key': obj['Key']} for obj in response['Contents']]}
        s3.delete_objects(Bucket=bucket_name, Delete=delete)
        response = s3.list_objects_v2(Bucket=bucket_name)

    # Next, if the bucket is versioned, delete all versions
    response = s3.list_object_versions(Bucket=bucket_name)
    while 'Versions' in response or 'DeleteMarkers' in response:
        print(f"Deleting {len(response.get('Versions', [])) + len(response.get('DeleteMarkers', []))} items...")
        delete = {'Objects': []}
        delete['Objects'].extend([{'Key': item['Key'], 'VersionId': item['VersionId']} for item in response.get('Versions', [])])
        delete['Objects'].extend([{'Key': item['Key'], 'VersionId': item['VersionId']} for item in response.get('DeleteMarkers', [])])
        s3.delete_objects(Bucket=bucket_name, Delete=delete)
        response = s3.list_object_versions(Bucket=bucket_name)

    print(f"The bucket {bucket_name} has been emptied.")

if __name__ == "__main__":
    empty_s3_bucket(S3_BUCKET)
