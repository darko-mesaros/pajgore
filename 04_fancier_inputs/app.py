import os
import boto3
from tqdm import tqdm
from botocore.exceptions import ClientError, NoCredentialsError
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.styles import Style
from colorama import init, Fore, Style as ColoramaStyle

# Initialize Colorama so we can have nice colors
init(autoreset=True)

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


# Function that will add Tabs and colors to the prompt
def colorful_input(message, completer=None):
    # Returns a style for the prompt. A simple ANSI cyan
    # with some Bold (where supported)
    style = Style.from_dict({
        'prompt': 'ansicyan bold',
        })
    return prompt(message, completer=completer, style=style)


if __name__ == "__main__":
    # Bubble up the error from the other functions
    try:
        # Calling the colorful_input function, and adding the
        # prompt_toolkit PathCompleter() class
        file_path = colorful_input(
                "Enter file name to be uploaded: ", PathCompleter())
        bucket_name = colorful_input(
                "Enter the name of he bucket to upload to: ")
        url = upload_and_sign(file_path, bucket_name)

        # Using colorama to print text in color
        print(f"{Fore.GREEN}Here is your presigned URL:\
                {ColoramaStyle.RESET_ALL} \n{url}")
    except Exception as e:
        # Using colorama to print text in color - this time in red
        print(f"{Fore.RED}An error has occured:\
                {ColoramaStyle.RESET_ALL} {str(e)}")
