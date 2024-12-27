# Code by Sergio1260

from re import compile as re_compile
from flask import Response, request
from flask import send_file as df_send_file
from os.path import getsize

RANGE_REGEX = re_compile(r"bytes=(\d+)-(\d*)")


def send_file(file_path):
    file_size = getsize(file_path)
    range_header = request.headers.get('Range')
    
    if range_header:
        ranges = parse_ranges(range_header, file_size)
        if not ranges: return Response("Invalid Range", status=416)

        if len(ranges) == 1:
            content_range = f"bytes {ranges[0][0]}-{ranges[-1][1]}/{file_size}"
        else: content_range = f"bytes {ranges[0][0]}-{ranges[-1][1]}/{file_size}"

        return Response(generate(file_path,ranges), status=206, headers={
            'Content-Range': content_range,
            'Accept-Ranges': 'bytes',
            'Content-Length': str(sum([end - start + 1 for start, end in ranges])) 
        })
    
    return df_send_file(file_path)


def parse_ranges(range_header, file_size):
    range_match,ranges = RANGE_REGEX.match(range_header),[]
    if range_match:
        start = int(range_match.group(1))
        end = range_match.group(2)
        if not end: end = file_size-1
        else: end = int(end)
        if start>=file_size or end>=file_size or start>end: return None
        ranges.append((start, end))
    return ranges

def read_chunk(file, remaining_bytes):
    while remaining_bytes > 0:
        chunk = file.read(min(1024 * 1024, remaining_bytes))
        remaining_bytes -= len(chunk)
        yield chunk

def generate(file_path, ranges):
    with open(file_path, 'rb') as file:
        for start, end in ranges:
            file.seek(start)
            remaining_bytes = end - start + 1
            yield from read_chunk(file, remaining_bytes)

