import boto3, botocore
from config import Config

s3 = boto3.client(
   "s3",
   aws_access_key_id="AKIASIAHRIS5QIKHPS7E",
   aws_secret_access_key="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"
)

def upload_file_to_s3(file, bucket_name, acl="public-read"):

    try:

        s3.upload_fileobj(
            file,
            bucket_name,
            file.filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )

    except Exception as e:
        # This is a catch all exception, edit this part to fit your needs.
        print("Something Happened: ", e)
        return e
    
    return f"https://fabrykamruczenia.s3.amazonaws.com/{file.filename}"