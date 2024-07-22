import sys

from dataclasses import dataclass


@dataclass
class Header:
    offset: int
    size: int


PAGE_SIZE = Header(16, 2)
PAGE_COUNT = Header(28, 4)

# import sqlparse - available if you need it!

database_file_path = sys.argv[1]
command = sys.argv[2]

if command == ".dbinfo":
    with open(database_file_path, "rb") as database_file:
        database_file.seek(PAGE_SIZE.offset)  # Skip the first 16 bytes of the header
        page_size = int.from_bytes(database_file.read(PAGE_SIZE.size))

        database_file.seek(PAGE_COUNT.offset, 0)  # Offset from beginning of file
        page_count = int.from_bytes(database_file.read(PAGE_COUNT.size))

        print(f"database page size: {page_size}")
        print(f"database page count: {page_count}")
else:
    print(f"Invalid command: {command}")
