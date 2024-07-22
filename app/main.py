import sys

from dataclasses import dataclass


@dataclass
class Header:
    offset: int
    size: int


PAGE_SIZE = Header(16, 2)
PAGE_COUNT = Header(28, 4)


class Page:
    """
    A b-tree page is divided into regions in the following order:

    - The 100-byte database file header (found on page 1 only)
    - The 8 or 12 byte b-tree page header
    - The cell pointer array
    - Unallocated space
    - The cell content area
    - The reserved region.
    """

    DB_HEADER_SIZE = 100
    TREE_HEADER_SIZE = (8, 12)


# import sqlparse - available if you need it!

database_file_path = sys.argv[1]
command = sys.argv[2]

if command == ".dbinfo":
    with open(database_file_path, "rb") as database_file:
        database_file.seek(PAGE_SIZE.offset)  # Skip the first 16 bytes of the header
        page_size = int.from_bytes(database_file.read(PAGE_SIZE.size))

        database_file.seek(PAGE_COUNT.offset, 0)  # Offset from beginning of file
        page_count = int.from_bytes(database_file.read(PAGE_COUNT.size))

        database_file.seek(Page.DB_HEADER_SIZE)
        page = database_file.read(page_size - Page.DB_HEADER_SIZE)

        print(f"database page size: {page_size}")
        print(f"database page count: {page_count}")

        print(f"Raw page contents: \n{page.decode('utf-8', errors='replace')}")

else:
    print(f"Invalid command: {command}")
