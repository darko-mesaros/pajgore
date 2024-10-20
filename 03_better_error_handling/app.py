import os
import boto3
from tqdm import tqdm
from botocore.exceptions import ClientError, NoCredentialsError

s3_client = boto3.client('s3')


def upload_and_sign(file_path, bucket):
    # Start of our Try statement for the upload
    try:
        file_name = os.path.basename(file_path)

        # Check if file exists:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")

        file_size = os.path.getsize(file_path)

        # callback function for the upload progress
        def upload_progress(bytes_transferred):
            pbar.update(bytes_transferred)

        # create the progress bar
        with tqdm(total=file_size, unit='B', unit_scale=True, desc=file_name)\
                as pbar:
            # Try to upload the file
            try:
                s3_client.upload_file(
                        file_path,
                        bucket,
                        file_name,
                        Callback=upload_progress
                        )
            except ClientError as e:
                raise Exception(f"Failed to upload file: {str(e)}")

        # Try to presign the file
        try:
            url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={
                        "Bucket": bucket,
                        "Key": file_name
                        },
                    ExpiresIn=3600)
            return url
        except ClientError as e:
            raise Exception(f"Failed to generate a presigned URL: {str(e)}")

    # If we are missing the credentials, let us know
    except NoCredentialsError:
        raise Exception("AWS Credentials not found,\
                please configure your AWS Credentials.")


if __name__ == "__main__":
    # Bubble up the error from the other functions
    try:
        file_path = input("Enter file name to be uploaded: ")
        bucket_name = input("Enter the name of he bucket to upload to: ")
        url = upload_and_sign(file_path, bucket_name)

        print(f"Here is your presigned URL: \n{url}")
    except Exception as e:
        print(f"An error has occured: {str(e)}")
