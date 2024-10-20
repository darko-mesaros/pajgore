import os
import boto3
from tqdm import tqdm

s3_client = boto3.client('s3')


def upload_and_sign(file_path, bucket):
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    # callback function for the upload progress
    def upload_progress(bytes_transferred):
        pbar.update(bytes_transferred)

    # create the progress bar
    with tqdm(total=file_size, unit='B', unit_scale=True, desc=file_name) as pbar:
        s3_client.upload_file(
                file_path,
                bucket,
                file_name,
                Callback=upload_progress
                )

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
