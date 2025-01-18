#Code by Sergio00166

from werkzeug.http import parse_options_header
from functions import validate_acl, safe_path
from os.path import dirname, exists
from shutil import SameFileError
from os import makedirs, sep


def save_upload(request, dest_url, root, ACL):

    environ = request.environ
    input_stream = environ['wsgi.input']
    content_length = int(environ.get('CONTENT_LENGTH', 0))
    content_type = environ.get('CONTENT_TYPE', '')

    if content_length == 0 or not\
    content_type.startswith('multipart/'):
        raise ValueError

    boundary = parse_options_header(content_type)[1]['boundary']
    boundary_bytes = f"--{boundary}".encode()
    end_boundary_bytes = f"--{boundary}--".encode()
    crlf = b"\r\n"

    file_obj,current_filename = None,None
    remaining = content_length
    inside_file_content = False

    while remaining > 0:
        line = input_stream.readline()
        remaining -= len(line)

        # Handle boundary
        if line.startswith(boundary_bytes):
            # Close the previous file when a new boundary is detected
            if file_obj:
                file_obj.close()
                file_obj,current_filename = None,None
            inside_file_content = False

            # End boundary detected, exit the loop
            if line.strip() == end_boundary_bytes: break
            continue

        # Handle headers
        if line.startswith(b"Content-Disposition:") and not inside_file_content:
            # Parse filename from Content-Disposition
            disposition_data = parse_options_header(line.decode('utf-8'))
            current_filename = disposition_data[1].get('filename')
        
            if current_filename:
                # Check permissions
                path = dest_url+"/"+current_filename
                file_path = path.replace("/", sep)
                file_path = safe_path(file_path, root, True)
                if exists(file_path): raise SameFileError
                validate_acl(path, ACL, True)                

                # Create parent and create object
                makedirs(dirname(file_path), exist_ok=True)
                file_obj = open(file_path, 'wb')

         
        # Empty line indicates the end of headers;
        # the next part is file content
        elif line == crlf and current_filename\
        and file_obj and not inside_file_content:
            inside_file_content = True
            continue

        # Write file content
        if inside_file_content and file_obj:
            file_obj.write(line)

    # Ensure the last file is closed
    if file_obj: file_obj.close()




