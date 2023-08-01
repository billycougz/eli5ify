import concurrent.futures
import os
import uuid
import boto3

s3 = boto3.client('s3')

def _generate_presigned_url(filename):
    bucket_name = os.getenv('FILE_BUCKET_NAME')
    object_key = 'source-files/' + filename
    file_extension = os.path.splitext(filename)[1]

    presigned_url = s3.generate_presigned_url(
        ClientMethod='put_object',
        Params={'Bucket': bucket_name, 'Key': object_key, 'ContentType': get_content_type(file_extension)},
        ExpiresIn=3600  # Set the expiration time for the presigned URL (in seconds)
    )

    return presigned_url

def get_content_type(file_extension):
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.pdf': 'application/pdf',
        '.txt': 'text/plain',
        '.html': 'text/html',
        # Add more file extensions and their corresponding MIME types as needed
    }

    return mime_types.get(file_extension.lower(), 'application/octet-stream')

def _replace_filename_with_uuid(filename):
    _, file_extension = os.path.splitext(filename)
    random_uuid = str(uuid.uuid4())
    new_filename = f"{random_uuid}{file_extension}"
    return new_filename

def generate_presigned_urls(source_filenames):
    # Replace filenames with UUID-based filenames
    uuid_filenames = [_replace_filename_with_uuid(filename) for filename in source_filenames]

    # Using ThreadPoolExecutor for concurrent URL generation
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit each filename to the executor
        future_to_url = {executor.submit(_generate_presigned_url, filename): filename for filename in uuid_filenames}

        presigned_urls = {}
        for future in concurrent.futures.as_completed(future_to_url):
            filename = future_to_url[future]
            try:
                presigned_url = future.result()
                presigned_urls[filename] = presigned_url
            except Exception as e:
                presigned_urls[filename] = f"Error generating presigned URL: {e}"

    # ToDo: Need to return UUID-based source filenames?
    return presigned_urls
    