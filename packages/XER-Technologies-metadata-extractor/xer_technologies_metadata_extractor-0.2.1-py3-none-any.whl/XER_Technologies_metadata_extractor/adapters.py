"""
Storage adapters for MetadataExtractor.

Provides adapters for different storage backends while using the same core extraction logic.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, Optional, Union

import pandas as pd

from XER_Technologies_metadata_extractor.extract import MetadataExtractor


class LocalFileAdapter:
    """Adapter for processing local files with MetadataExtractor."""

    def __init__(self, data_dir: Union[str, Path]) -> None:
        """Initialize with data directory path."""
        self.data_dir = Path(data_dir)
        self.extractor = MetadataExtractor()

    def extract_metadata(
        self,
        csv_file: Optional[str] = None,
        bin_file: Optional[str] = None,
        verbose: bool = True,
    ) -> Dict[str, Any]:
        """
        Extract metadata from local files. Handles either CSV or binary files.

        Args:
            csv_file: Name of the CSV file in the data directory
            bin_file: Name of the binary file in the data directory
            verbose: Whether to print detailed information during processing

        Returns:
            dict: Extracted metadata for the specified file

        Raises:
            ValueError: If both files are provided or if no file is provided
            FileNotFoundError: If the specified file is not found
        """
        if csv_file and bin_file:
            raise ValueError(
                "Cannot process both CSV and binary files in the same call. "
                "Call this method separately for each file type."
            )

        if not csv_file and not bin_file:
            raise ValueError("Must provide either csv_file or bin_file")

        if csv_file:
            csv_path = self.data_dir / csv_file
            if not csv_path.exists():
                raise FileNotFoundError(
                    f"CSV file {csv_file} not found in {self.data_dir}"
                )
            csv_data = csv_path.read_bytes()
            return self.extractor.extract_csv_metadata(
                csv_data=csv_data, csv_filename=csv_file, verbose=verbose
            )

        if not bin_file:  # This should never happen due to earlier checks
            raise ValueError("Must provide either csv_file or bin_file")

        bin_path = self.data_dir / bin_file
        if not bin_path.exists():
            raise FileNotFoundError(
                f"Binary file {bin_file} not found in {self.data_dir}"
            )
        bin_data = bin_path.read_bytes()
        return self.extractor.extract_binary_metadata(
            bin_data=bin_data, bin_filename=bin_file, verbose=verbose
        )

    def extract_csv_data(self, csv_file: str) -> pd.DataFrame:
        """
        Extract all data from a local CSV file at once.

        Args:
            csv_file: Name of the CSV file in the data directory

        Returns:
            pd.DataFrame: The entire CSV data as a pandas DataFrame
        """
        csv_path = self.data_dir / csv_file
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file {csv_file} not found in {self.data_dir}")
        return self.extractor.extract_from_csv_data(csv_path.read_bytes())

    def extract_csv_data_chunked(
        self, csv_file: str, chunk_size: int = 10000
    ) -> Iterator[pd.DataFrame]:
        """
        Extract data from a local CSV file in chunks for memory-efficient processing.

        This method opens the file in binary mode and streams it directly to pandas,
        making it memory efficient for large files.

        Args:
            csv_file: Name of the CSV file in the data directory
            chunk_size: Number of rows to process at a time

        Returns:
            Iterator[pd.DataFrame]: An iterator yielding chunks of the CSV data

        Raises:
            FileNotFoundError: If the CSV file is not found
        """
        csv_path = self.data_dir / csv_file
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file {csv_file} not found in {self.data_dir}")

        with open(csv_path, "rb") as f:
            for chunk in pd.read_csv(f, chunksize=chunk_size):
                yield chunk

    # Individual metric calculation methods
    def calculate_engine_metrics(
        self, csv_file: str, verbose: bool = False
    ) -> Dict[str, Any]:
        """Calculate engine-related metrics from a local CSV file."""
        df = self.extract_csv_data(csv_file)
        engine_hours = self.extractor.calculate_engine_working_hours(
            df, verbose=verbose
        )
        engine_starts = self.extractor.calculate_engine_starts(df)
        rpm_stats = self.extractor.calculate_rpm_statistics(df)
        return {
            "engine_metrics": {
                "total_engine_hours": engine_hours.get("total_hours", 0),
                "total_engine_starts": engine_starts.get("total_starts", 0),
            },
            "rpm_metrics": {
                "average_rpm": rpm_stats["operating_statistics"].get(
                    "operating_mean", 0
                ),
                "max_rpm": rpm_stats["operating_statistics"].get("operating_max", 0),
                "idle_time_percentage": rpm_stats.get("idle_time_percentage", 0),
            },
        }

    def calculate_hub_current_metrics(self, csv_file: str) -> Dict[str, Any]:
        """Calculate hub current metrics from a local CSV file."""
        df = self.extract_csv_data(csv_file)
        return self.extractor.calculate_hub_current_statistics(df)

    def calculate_hub_voltage_metrics(self, csv_file: str) -> Dict[str, Any]:
        """Calculate hub voltage metrics from a local CSV file."""
        df = self.extract_csv_data(csv_file)
        return self.extractor.calculate_hub_voltage_statistics(df)

    def calculate_battery_current_metrics(self, csv_file: str) -> Dict[str, Any]:
        """Calculate battery current metrics from a local CSV file."""
        df = self.extract_csv_data(csv_file)
        return self.extractor.calculate_battery_current_statistics(df)

    def calculate_cht1_metrics(self, csv_file: str) -> Dict[str, Any]:
        """Calculate CHT1 metrics from a local CSV file."""
        df = self.extract_csv_data(csv_file)
        return self.extractor.calculate_cht1_statistics(df)

    def calculate_cht2_metrics(self, csv_file: str) -> Dict[str, Any]:
        """Calculate CHT2 metrics from a local CSV file."""
        df = self.extract_csv_data(csv_file)
        return self.extractor.calculate_cht2_statistics(df)

    def calculate_hub_throttle_metrics(self, csv_file: str) -> Dict[str, Any]:
        """Calculate hub throttle metrics from a local CSV file."""
        df = self.extract_csv_data(csv_file)
        return self.extractor.calculate_hub_throttle_statistics(df)

    def calculate_air_temp_metrics(self, csv_file: str) -> Dict[str, Any]:
        """Calculate air temperature metrics from a local CSV file."""
        df = self.extract_csv_data(csv_file)
        return self.extractor.calculate_air_temp_statistics(df)

    def calculate_efficiency_metrics(self, csv_file: str) -> Dict[str, Any]:
        """Calculate efficiency metrics from a local CSV file."""
        df = self.extract_csv_data(csv_file)
        return self.extractor.calculate_efficiency_statistics(df)


class S3Adapter:
    """
    Adapter for processing S3 objects with MetadataExtractor.
    When running in AWS Lambda, the boto3 client will be automatically available
    and properly configured with the Lambda execution role.
    """

    def __init__(
        self,
        bucket_name: str,
        s3_client: Optional[Any] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: Optional[str] = None,
    ) -> None:
        """
        Initialize with S3 bucket and optional credentials.
        If s3_client is provided, it will be used instead of creating a new one.
        """
        self.bucket_name = bucket_name
        self.extractor = MetadataExtractor()

        if s3_client:
            self.s3_client = s3_client
        else:
            import boto3

            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region_name,
            )

    def extract_metadata(
        self,
        csv_object_key: Optional[str] = None,
        bin_object_key: Optional[str] = None,
        verbose: bool = True,
    ) -> Dict[str, Any]:
        """
        Extract metadata from S3 objects. Handles either CSV or binary files.

        Args:
            csv_object_key: S3 key for the CSV object
            bin_object_key: S3 key for the binary object
            verbose: Whether to print detailed information during processing

        Returns:
            dict: Extracted metadata for the specified object

        Raises:
            ValueError: If both objects are provided or if no object is provided
        """
        if csv_object_key and bin_object_key:
            raise ValueError(
                "Cannot process both CSV and binary objects in the same call. "
                "Call this method separately for each object type."
            )

        if not csv_object_key and not bin_object_key:
            raise ValueError("Must provide either csv_object_key or bin_object_key")

        try:
            if csv_object_key:
                response = self.s3_client.get_object(
                    Bucket=self.bucket_name, Key=csv_object_key
                )
                csv_data = response["Body"].read()
                csv_filename = csv_object_key.split("/")[-1]
                return self.extractor.extract_csv_metadata(
                    csv_data=csv_data, csv_filename=csv_filename, verbose=verbose
                )

            response = self.s3_client.get_object(
                Bucket=self.bucket_name, Key=bin_object_key  # type: ignore[arg-type] # bin_object_key is not None here
            )
            bin_data = response["Body"].read()
            bin_filename = bin_object_key.split("/")[-1]  # type: ignore[union-attr] # bin_object_key is not None here
            return self.extractor.extract_binary_metadata(
                bin_data=bin_data, bin_filename=bin_filename, verbose=verbose
            )
        except Exception as e:
            # Return error response with all required fields
            error_response = {
                "extraction_timestamp": datetime.now().isoformat(),
                "file_info": {},
                "filename_metadata": {},
                "validation_results": {},
                "engine_metrics": {},
                "errors": [f"Failed to extract metadata from S3: {str(e)}"],
                "warnings": [],
                "bucket": self.bucket_name,
                "key": csv_object_key or bin_object_key,
            }
            if bin_object_key:  # Binary files don't have engine metrics
                error_response.pop("engine_metrics")
            return error_response

    def extract_csv_data(self, csv_object_key: str) -> pd.DataFrame:
        """
        Extract all data from an S3 CSV object at once.

        Args:
            csv_object_key: S3 key for the CSV object

        Returns:
            pd.DataFrame: The entire CSV data as a pandas DataFrame
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name, Key=csv_object_key
            )
            return self.extractor.extract_from_csv_data(response["Body"].read())
        except Exception as e:
            raise Exception(f"Error reading CSV from S3: {str(e)}")

    def extract_csv_data_chunked(
        self, csv_object_key: str, chunk_size: int = 10000, stream: bool = False
    ) -> Iterator[pd.DataFrame]:
        """
        Extract data from an S3 CSV object in chunks for memory-efficient processing.

        This method can either:
        1. Stream data directly from S3 using the Body stream (when stream=True)
        2. Download and process in chunks (when stream=False)

        The streaming mode is particularly efficient for AWS Lambda where the S3
        Body stream can be used directly.

        Args:
            csv_object_key: S3 key for the CSV object
            chunk_size: Number of rows to process at a time
            stream: Whether to use S3 streaming mode (recommended for Lambda)

        Returns:
            Iterator[pd.DataFrame]: An iterator yielding chunks of the CSV data

        Raises:
            Exception: If there is an error reading from S3
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name, Key=csv_object_key
            )

            if stream:
                # Use S3 Body stream directly with pandas
                for chunk in pd.read_csv(response["Body"], chunksize=chunk_size):
                    yield chunk
            else:
                # Download and process in chunks
                data = response["Body"].read()
                for chunk in pd.read_csv(
                    pd.io.common.BytesIO(data), chunksize=chunk_size
                ):
                    yield chunk

        except Exception as e:
            raise Exception(f"Error reading CSV from S3: {str(e)}")

    # Individual metric calculation methods
    def calculate_engine_metrics(
        self, csv_object_key: str, verbose: bool = False
    ) -> Dict[str, Any]:
        """Calculate engine-related metrics from an S3 CSV object."""
        df = self.extract_csv_data(csv_object_key)
        engine_hours = self.extractor.calculate_engine_working_hours(
            df, verbose=verbose
        )
        engine_starts = self.extractor.calculate_engine_starts(df)
        rpm_stats = self.extractor.calculate_rpm_statistics(df)
        return {
            "engine_metrics": {
                "total_engine_hours": engine_hours.get("total_hours", 0),
                "total_engine_starts": engine_starts.get("total_starts", 0),
            },
            "rpm_metrics": {
                "average_rpm": rpm_stats["operating_statistics"].get(
                    "operating_mean", 0
                ),
                "max_rpm": rpm_stats["operating_statistics"].get("operating_max", 0),
                "idle_time_percentage": rpm_stats.get("idle_time_percentage", 0),
            },
        }

    def calculate_hub_current_metrics(self, csv_object_key: str) -> Dict[str, Any]:
        """Calculate hub current metrics from an S3 CSV object."""
        df = self.extract_csv_data(csv_object_key)
        return self.extractor.calculate_hub_current_statistics(df)

    def calculate_hub_voltage_metrics(self, csv_object_key: str) -> Dict[str, Any]:
        """Calculate hub voltage metrics from an S3 CSV object."""
        df = self.extract_csv_data(csv_object_key)
        return self.extractor.calculate_hub_voltage_statistics(df)

    def calculate_battery_current_metrics(self, csv_object_key: str) -> Dict[str, Any]:
        """Calculate battery current metrics from an S3 CSV object."""
        df = self.extract_csv_data(csv_object_key)
        return self.extractor.calculate_battery_current_statistics(df)

    def calculate_cht1_metrics(self, csv_object_key: str) -> Dict[str, Any]:
        """Calculate CHT1 metrics from an S3 CSV object."""
        df = self.extract_csv_data(csv_object_key)
        return self.extractor.calculate_cht1_statistics(df)

    def calculate_cht2_metrics(self, csv_object_key: str) -> Dict[str, Any]:
        """Calculate CHT2 metrics from an S3 CSV object."""
        df = self.extract_csv_data(csv_object_key)
        return self.extractor.calculate_cht2_statistics(df)

    def calculate_hub_throttle_metrics(self, csv_object_key: str) -> Dict[str, Any]:
        """Calculate hub throttle metrics from an S3 CSV object."""
        df = self.extract_csv_data(csv_object_key)
        return self.extractor.calculate_hub_throttle_statistics(df)

    def calculate_air_temp_metrics(self, csv_object_key: str) -> Dict[str, Any]:
        """Calculate air temperature metrics from an S3 CSV object."""
        df = self.extract_csv_data(csv_object_key)
        return self.extractor.calculate_air_temp_statistics(df)

    def calculate_efficiency_metrics(self, csv_object_key: str) -> Dict[str, Any]:
        """Calculate efficiency metrics from an S3 CSV object."""
        df = self.extract_csv_data(csv_object_key)
        return self.extractor.calculate_efficiency_statistics(df)
