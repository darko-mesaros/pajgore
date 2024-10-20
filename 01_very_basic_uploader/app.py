import os
import boto3

s3_client = boto3.client('s3')


def upload_and_sign(file_path, bucket):
    file_name = os.path.basename(file_path)

    s3_client.upload_file(file_path, bucket, file_name)

    url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                "Bucket": bucket,
                "Key": file_name
                },
            ExpiresIn=3600)
    return url


if __name__ == "__main__":
    file_path = input("Enter file name to be uploaded: ")
    bucket_name = input("Enter the name of he bucket to upload to: ")

    url = upload_and_sign(file_path, bucket_name)

    print(f"Here is your presigned URL: \n{url}")
