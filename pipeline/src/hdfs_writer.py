from hdfs import InsecureClient
import os
from .locations import get_location_name


class HDFSWriter:
    """Helper class to write data into HDFS files partitioned by coordinates."""

    def __init__(self, client: InsecureClient, base_path: str, namespace: str = None):
        self.client = client
        self.base_path = base_path.rstrip("/")
        self.namespace = namespace
        self.default_name = "unknown_location"

    def _get_partition_filename(self, partition_key: str) -> str:
        """Get HDFS file path for a coordinate-based partition key."""
        location_name = get_location_name(partition_key, self.default_name)
        file_name = f"{location_name}.log"
        hdfs_path = os.path.join(self.base_path, file_name).replace('\\', '/')
        print("hdfs_path: ", hdfs_path)
        return hdfs_path

    def append(self, partition_key: str, data: str, encoding: str = "utf-8"):
        """Append data to the HDFS file for the given partition."""
        hdfs_file_path = self._get_partition_filename(partition_key)

        # Ensure parent directory exists
        parent_dir = os.path.dirname(hdfs_file_path)
        if not self.client.status(parent_dir, strict=False):
            self.client.makedirs(parent_dir)

        # Create file if it doesn't exist
        if not self.client.status(hdfs_file_path, strict=False):
            with self.client.write(hdfs_file_path, encoding=encoding, overwrite=True) as writer:
                pass

        # Append data
        with self.client.write(hdfs_file_path, encoding=encoding, append=True) as writer:
            writer.write(data)
