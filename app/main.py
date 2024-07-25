import pprint as pp
import struct
import sys
from dataclasses import dataclass
from enum import Enum

DB_HEADER_SIZE = 100
PAGE_HEADER_SIZE = 12

# fmt: off
DB_HEADER = [
    (">", 0),    # Force big endian
    ("16s", 16), # Intro "SQLite format 3\000"
    ("h", 2),    # Page size in bytes
    ("b", 1),    # Write version
    ("b", 1),    # Read version
    ("b", 1),    # Reserved space
    ("7x", 7),   # Unimportant
    ("i ", 4),   # Size of the database file in pages
    ("68x", 68), # Rest of the header
]
# fmt: on


# fmt: off
PAGE_HEADER = [
    (">", 0),  # Force big endian
    ("b", 1),  # Flag indicating the b-tree page type
    ("h", 2),  # Start of the first freeblock on the page
    ("h", 2),  # Number of cells on page
    ("h", 2),  # Start of the cell content area
    ("b", 1),  # Number of fragmented free bytes
    ("i", 4),  # Right-most pointer
]
# fmt: on


@dataclass
class DBHeader:
    banner: str
    page_size: int
    page_count: int
    write_version: int
    read_version: int
    reserved: int

    @staticmethod
    def parse(bs: bytes) -> "DBHeader":
        fmt = "".join([f for (f, _) in DB_HEADER])
        size = sum([i for (_, i) in DB_HEADER])

        assert size == DB_HEADER_SIZE
        assert struct.calcsize(fmt) == size
        assert len(bs) == size

        return DBHeader(*struct.unpack(fmt, bs))


class PageKind(Enum):
    InteriorIndex = 2  # An interior index b-tree page.
    InteriorTable = 5  # An interior table b-tree page.
    LeafIndex = 10  # A leaf index b-tree page.
    LeafTable = 13  # a leaf table b-tree page.


@dataclass
class PageHeader:
    """
    The b-tree page header is 8 bytes in size for leaf pages
    and 12 bytes for interior pages
    """

    kind: PageKind
    first_free_block: int
    number_of_cells: int
    start_of_cell_content: int
    number_of_free_bytes: int
    right_most_pointer: int | None = None

    @staticmethod
    def parse(bs: bytes) -> "PageHeader":
        fmt = "".join([f for (f, _) in PAGE_HEADER])
        size = sum([i for (_, i) in PAGE_HEADER])

        assert size == PAGE_HEADER_SIZE
        assert struct.calcsize(fmt) == size
        assert len(bs) == size

        vals = struct.unpack(fmt, bs)

        kind = PageKind(vals[0])
        match kind:
            case PageKind.InteriorIndex | PageKind.InteriorTable:
                vals = (kind, *vals[1:6])
            case PageKind.LeafIndex | PageKind.LeafTable:
                vals = (kind, *vals[1:5])

        return PageHeader(*vals)  # type: ignore


@dataclass
class DBInfo:
    db_header: DBHeader
    page_header: PageHeader

    def __post_init__(self):
        # NOTE: Approximation that only works in simple cases.
        self.number_of_tables = self.page_header.number_of_cells

    def __str__(self):
        return (
            f"database page size: {self.db_header.page_size}\n"
            f"database page count: {self.db_header.page_count}\n"
            f"number of tables: {self.number_of_tables}\n"
        )


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

    # def __init__(self, index: int, size: int, database: FileIO) -> None:
    # pass


def db_info(database_file_path) -> DBInfo:
    with open(database_file_path, "rb") as database_file:
        db_header = DBHeader.parse(database_file.read(DB_HEADER_SIZE))
        page_header = PageHeader.parse(database_file.read(PAGE_HEADER_SIZE))

        print(f"{pp.pformat(db_header)}", end="\n\n")
        print(f"{pp.pformat(page_header)}", end="\n\n")

        return DBInfo(db_header, page_header)


if __name__ == "__main__":
    database_file_path = sys.argv[1]
    command = sys.argv[2]

    if command == ".dbinfo":
        print(db_info(database_file_path))
    else:
        print(f"Invalid command: {command}")
