import os
import re
import traceback
from datetime import datetime
from io import StringIO
from typing import Any, BinaryIO, Dict, Iterator, Optional, Union

import pandas as pd

from XER_Technologies_metadata_extractor.utilities import COLUMN_MAPPINGS
from XER_Technologies_metadata_extractor.validation import (
    FileValidator,
    ValidationResult,
)


class MetadataExtractor:
    """
    Storage-agnostic metadata extractor for CSV and binary files.

    Accepts bytes or file-like objects instead of file paths, making it suitable
    for both local file processing and cloud storage streaming.
    """

    def __init__(self) -> None:
        """Initialize the metadata extractor."""
        self.validator = FileValidator()

    def _read_data(self, file_data: Union[bytes, BinaryIO]) -> bytes:
        """Helper to read data from bytes or file-like object."""
        if hasattr(file_data, "read"):
            data_bytes = file_data.read()
            if hasattr(file_data, "seek"):
                file_data.seek(0)  # Reset for potential reuse
            return data_bytes
        return file_data

    # ----------------------### VALIDATION FUNCTIONS ###----------------------

    def validate_data(
        self, file_data: Union[bytes, BinaryIO], filename: str
    ) -> ValidationResult:
        """
        Validate data automatically based on filename extension.

        Args:
            file_data: File data as bytes or file-like object
            filename: Name of the file being validated

        Returns:
            ValidationResult with detailed validation feedback
        """

        data_bytes = self._read_data(file_data)
        file_extension = os.path.splitext(filename)[1].lower()

        if file_extension == ".csv":
            return self.validator.precheck_csv_file(data_bytes, filename)
        elif file_extension == ".bin":
            return self.validator.precheck_bin_file(data_bytes, filename)
        else:
            return ValidationResult(
                is_valid=False,
                message=f"Unsupported file type: {file_extension}. "
                f"Supported types: .csv, .bin",
            )

    # ----------------------### EXTRACTION FUNCTIONS ###----------------------

    def extract_from_csv_data(self, file_data: Union[bytes, BinaryIO]) -> pd.DataFrame:
        """
        Extract data from CSV bytes or file-like object by loading the entire file into memory.

        This method is suitable for small to medium-sized files where memory usage is not a concern.
        For very large files, consider using extract_from_csv_data_chunked instead.

        Args:
            file_data: CSV data as bytes or file-like object

        Returns:
            pd.DataFrame: The entire CSV data as a pandas DataFrame
        """
        data_bytes = self._read_data(file_data)
        text_data = data_bytes.decode("utf-8")
        return pd.read_csv(StringIO(text_data))

    def extract_from_csv_data_chunked(
        self, file_data: BinaryIO, chunk_size: int = 10000
    ) -> Iterator[pd.DataFrame]:
        """
        Extract data from CSV in chunks for memory-efficient processing of large files.

        This method streams data directly from the file-like object without loading
        the entire file into memory. This is ideal for:
        - Processing very large CSV files that might not fit in memory
        - Streaming processing of data
        - Systems with limited memory resources

        Args:
            file_data: CSV data as a file-like object (must be BinaryIO)
            chunk_size: Number of rows to process at a time (default: 10000)

        Returns:
            Iterator[pd.DataFrame]: An iterator yielding chunks of the CSV data

        Raises:
            TypeError: If file_data is not a file-like object
        """
        if not hasattr(file_data, "read"):
            raise TypeError("file_data must be a file-like object supporting read()")

        return pd.read_csv(file_data, chunksize=chunk_size)

    def get_csv_info(self, file_data: Union[bytes, BinaryIO]) -> Dict[str, Any]:
        """Get basic information about CSV data without loading it entirely."""
        data_bytes = self._read_data(file_data)
        data_size = len(data_bytes)

        text_data = data_bytes.decode("utf-8")
        lines = text_data.strip().split("\n")

        if not lines:
            raise ValueError("CSV data is empty")

        header_line = lines[0].rstrip(
            "\r"
        )  # Remove carriage return but preserve column whitespace
        # Don't strip column names to match pandas behavior exactly
        columns = header_line.split(",")

        return {
            "data_size_bytes": data_size,
            "data_size_mb": round(data_size / (1024 * 1024), 2),
            "total_rows": len(lines) - 1,  # Exclude header
            "total_columns": len(columns),
            "columns": columns,
        }

    def get_binary_info(self, file_data: Union[bytes, BinaryIO]) -> Dict[str, Any]:
        """Get basic information about binary data."""
        data_bytes = self._read_data(file_data)
        data_size = len(data_bytes)

        return {
            "data_size_bytes": data_size,
            "data_size_mb": round(data_size / (1024 * 1024), 2),
            "header_sample": data_bytes[:100],  # First 100 bytes for inspection
        }

    # ----------------------### FILENAME PARSING FUNCTIONS ###----------------------

    @staticmethod
    def parse_xfd_filename(filename: str) -> Optional[Dict[str, Any]]:
        """
        Parse XFD filename pattern: XFD_108_20250219_2007.csv or XFD_108_20250219_2007_Created.csv

        Args:
            filename (str): The name of the file to parse

        Returns:
            dict: Extracted metadata or None if pattern doesn't match
        """
        # Updated pattern to optionally match additional text after the timestamp
        pattern = r"XFD_(\d+)_(\d{8})_(\d{4})(?:_[^.]+)?\.csv"
        match = re.match(pattern, filename, re.IGNORECASE)

        if not match:
            return None

        serial_number, date_str, time_str = match.groups()

        try:
            # Parse date and time
            date_obj = datetime.strptime(date_str + time_str, "%Y%m%d%H%M")
            flight_date = date_obj.strftime("%Y-%m-%d")

            return {
                "fileType": "XFD",
                "serialNumber": serial_number,
                "flightDate": flight_date,
                "timestamp": date_obj.isoformat(),
            }
        except ValueError:
            return None

    @staticmethod
    def parse_generic_csv_filename(filename: str) -> Dict[str, Any]:
        """
        Parse generic CSV filename that should be treated as XFD data.
        Attempts to extract date and time from the filename if possible.

        Args:
            filename (str): The name of the file to parse

        Returns:
            dict: Extracted metadata with fileType set to 'XFD' and serialNumber set to None
        """
        # Try to extract date and time from various common formats
        date_patterns = [
            # YYYYMMDD_HHMMSS format (e.g., Flight_Test_20240516_084236.csv)
            r".*?(\d{8})_(\d{6})\.csv$",
            # YYYY-MM-DD HH-MM-SS format
            r".*?(\d{4}-\d{2}-\d{2})[_\s](\d{2}-\d{2}-\d{2})\.csv$",
            # YYYYMMDD format
            r".*?(\d{8})\.csv$",
        ]

        for pattern in date_patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                try:
                    if len(match.groups()) == 2:
                        # We have both date and time
                        date_str, time_str = match.groups()

                        # Handle different date formats
                        if "-" in date_str:
                            # YYYY-MM-DD format
                            date_obj = datetime.strptime(
                                f"{date_str} {time_str.replace('-', ':')}",
                                "%Y-%m-%d %H:%M:%S",
                            )
                        else:
                            # YYYYMMDD format
                            date_obj = datetime.strptime(
                                date_str + time_str, "%Y%m%d%H%M%S"
                            )

                        flight_date = date_obj.strftime("%Y-%m-%d")
                        return {
                            "fileType": "XFD",
                            "serialNumber": None,  # Will need to be provided by user
                            "flightDate": flight_date,
                            "timestamp": date_obj.isoformat(),
                        }
                    elif len(match.groups()) == 1:
                        # We only have date
                        date_str = match.group(1)
                        if "-" in date_str:
                            # YYYY-MM-DD format
                            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                        else:
                            # YYYYMMDD format
                            date_obj = datetime.strptime(date_str, "%Y%m%d")

                        flight_date = date_obj.strftime("%Y-%m-%d")
                        return {
                            "fileType": "XFD",
                            "serialNumber": None,  # Will need to be provided by user
                            "flightDate": flight_date,
                            "timestamp": date_obj.isoformat(),
                        }
                except ValueError:
                    continue

        # If we couldn't extract date/time, just return basic metadata
        return {
            "fileType": "XFD",
            "serialNumber": None,  # Will need to be provided by user
            "flightDate": None,
            "timestamp": None,
        }

    @staticmethod
    def parse_mp_filename(filename: str) -> Optional[Dict[str, Any]]:
        """
        Parse Mission Planner filename pattern: 2025-03-03 15-24-15.bin

        Args:
            filename (str): The name of the file to parse

        Returns:
            dict: Extracted metadata or None if pattern doesn't match
        """
        # Use case-insensitive pattern for .bin extension
        pattern = r"(\d{4}-\d{2}-\d{2}) (\d{2}-\d{2}-\d{2})\.bin$"
        match = re.search(pattern, filename, re.IGNORECASE)

        if not match:
            return None

        date_str, time_str = match.groups()

        try:
            # Parse date and time
            date_obj = datetime.strptime(
                f"{date_str} {time_str.replace('-', ':')}", "%Y-%m-%d %H:%M:%S"
            )

            return {
                "fileType": "MP",
                "flightDate": date_str,
                "timestamp": date_obj.isoformat(),
                "serialNumber": None,  # MP files don't typically contain serial numbers in filename
            }
        except ValueError:
            return None

    @staticmethod
    def parse_filename_metadata(filename: str) -> Optional[Dict[str, Any]]:
        """
        Parse filename and extract metadata based on file type and naming conventions.

        Args:
            filename (str): The name of the file to parse

        Returns:
            dict: Extracted metadata or None if no pattern matches
        """
        # Convert filename to lowercase for case-insensitive extension check
        filename_lower = filename.lower()

        # Try XFD format first
        if filename.startswith("XFD_") and filename_lower.endswith(".csv"):
            xfd_metadata = MetadataExtractor.parse_xfd_filename(filename)
            if xfd_metadata:
                return xfd_metadata

        # Try generic CSV format
        if filename_lower.endswith(".csv"):
            return MetadataExtractor.parse_generic_csv_filename(filename)

        # Try Mission Planner format
        if filename_lower.endswith(".bin"):
            mp_metadata = MetadataExtractor.parse_mp_filename(filename)
            if mp_metadata:
                return mp_metadata

        # If no pattern matches, return None
        return None

    def extract_filename_metadata(self, filename: str) -> Dict[str, Any]:
        """
        Extract metadata from filename and return structured information.

        Args:
            filename (str): The name of the file to parse

        Returns:
            dict: Extracted metadata with parsing status in a flattened structure:
                - filename: Original filename
                - parsing_successful: Whether parsing succeeded
                - fileType: Type of file (XFD, MP, Unknown)
                - serialNumber: Serial number if available
                - flightDate: Flight date if available
                - timestamp: ISO formatted timestamp if available
        """
        parsed_metadata = self.parse_filename_metadata(filename)

        if parsed_metadata is not None and any(
            v is not None for k, v in parsed_metadata.items() if k != "fileType"
        ):
            # Only mark as successful if we extracted any meaningful information beyond just the file type
            return {
                "filename": filename,
                "parsing_successful": True,
                "fileType": parsed_metadata["fileType"],
                "serialNumber": parsed_metadata["serialNumber"],
                "flightDate": parsed_metadata["flightDate"],
                "timestamp": parsed_metadata["timestamp"],
            }
        else:
            # For XFD files that failed to parse but match the pattern
            if filename.startswith("XFD_") and filename.lower().endswith(".csv"):
                return {
                    "filename": filename,
                    "parsing_successful": False,
                    "fileType": "XFD",
                    "serialNumber": None,
                    "flightDate": None,
                    "timestamp": None,
                }
            # For CSV files, treat as generic XFD data
            elif filename.lower().endswith(".csv"):
                return {
                    "filename": filename,
                    "parsing_successful": False,
                    "fileType": "XFD",
                    "serialNumber": None,
                    "flightDate": None,
                    "timestamp": None,
                }
            # For bin files that look like Mission Planner files
            elif filename.lower().endswith(".bin"):
                return {
                    "filename": filename,
                    "parsing_successful": False,
                    "fileType": "MP",
                    "serialNumber": None,
                    "flightDate": None,
                    "timestamp": None,
                }
            # For completely unknown files
            else:
                return {
                    "filename": filename,
                    "parsing_successful": False,
                    "fileType": "Unknown",
                    "serialNumber": None,
                    "flightDate": None,
                    "timestamp": None,
                }

    # ----------------------### COMPREHENSIVE METADATA EXTRACTION ###----------------------

    def extract_csv_metadata(
        self, csv_data: Union[bytes, BinaryIO], csv_filename: str, verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Extract all available metadata from a CSV file.

        Args:
            csv_data: CSV file data as bytes or file-like object
            csv_filename: Name of the CSV file
            verbose: Whether to print detailed information during processing

        Returns:
            dict: Comprehensive metadata including:
                - Extraction timestamp
                - File information (size, format)
                - Filename metadata (flattened structure)
                - Content validation results
                - Engine KPIs (if applicable)
                - Various metric calculations
                - Errors/warnings
        """
        if verbose:
            print("🔍 Starting CSV metadata extraction...")

        results: Dict[str, Any] = {
            "extraction_timestamp": datetime.now().isoformat(),
            "file_info": {},
            "filename_metadata": {},
            "validation_results": {},
            "engine_metrics": {},
            "hub_current_metrics": {},
            "hub_voltage_metrics": {},
            "battery_current_metrics": {},
            "cht1_metrics": {},
            "cht2_metrics": {},
            "hub_throttle_metrics": {},
            "air_temp_metrics": {},
            "efficiency_metrics": {},
            "errors": [],
            "warnings": [],
        }

        try:
            # 1. Extract filename metadata
            results["filename_metadata"] = self.extract_filename_metadata(csv_filename)

            if verbose and results["filename_metadata"]["parsing_successful"]:
                print("   📋 Filename parsing: ✅ Success")
                print(f"      File Type: {results['filename_metadata']['fileType']}")
                print(
                    f"      Serial Number: {results['filename_metadata']['serialNumber']}"
                )
                print(
                    f"      Flight Date: {results['filename_metadata']['flightDate']}"
                )
                print(f"      Timestamp: {results['filename_metadata']['timestamp']}")

            # 2. Validate file data
            validation = self.validate_data(csv_data, csv_filename)
            results["validation_results"] = {
                "is_valid": validation.is_valid,
                "message": validation.message,
                "detected_version": validation.detected_version,
                "warnings": validation.warnings,
            }

            if verbose:
                print(
                    f"   ✅ File validation: {'✅ Valid' if validation.is_valid else '❌ Invalid'}"
                )
                if validation.warnings:
                    print(f"      Warnings: {len(validation.warnings)} found")

            # 3. Extract basic file info
            csv_info = self.get_csv_info(csv_data)
            results["file_info"] = {
                "file_size_bytes": csv_info["data_size_bytes"],
                "file_size_mb": csv_info["data_size_mb"],
                "total_rows": csv_info["total_rows"],
                "total_columns": csv_info["total_columns"],
                "column_names": csv_info["columns"],
            }

            if verbose:
                print("   📈 File Info:")
                print(
                    f"      Size: {csv_info['data_size_bytes']:,} bytes ({csv_info['data_size_mb']:.2f} MB)"
                )
                print(
                    f"      Dimensions: {csv_info['total_rows']:,} rows × {csv_info['total_columns']} columns"
                )

            # 4. Calculate all metrics if possible
            try:
                df = self.extract_from_csv_data(csv_data)

                # Check if we have RPM data
                rpm_columns = [col for col in df.columns if "RPM" in col.upper()]
                if rpm_columns:
                    rpm_column = rpm_columns[0]
                    if verbose:
                        print(
                            f"\n🔧 Calculating engine metrics with column: {rpm_column}"
                        )
                        print(f"   Available columns: {list(df.columns)}")

                    engine_hours = self.calculate_engine_working_hours(
                        df, rpm_column=rpm_column, verbose=verbose
                    )
                    engine_starts = self.calculate_engine_starts(
                        df, rpm_column=rpm_column
                    )
                    rpm_stats = self.calculate_rpm_statistics(df, rpm_column=rpm_column)

                    results["engine_metrics"] = {
                        "total_engine_hours": engine_hours.get("total_hours", 0),
                        "total_engine_starts": engine_starts.get("total_starts", 0),
                    }

                    results["rpm_metrics"] = {
                        "average_rpm": rpm_stats["operating_statistics"].get(
                            "operating_mean", 0
                        ),
                        "max_rpm": rpm_stats["operating_statistics"].get(
                            "operating_max", 0
                        ),
                        "idle_time_percentage": rpm_stats.get(
                            "idle_time_percentage", 0
                        ),
                    }

                    if "debug_info" in engine_hours:
                        results["debug"] = engine_hours["debug_info"]

                # Calculate all other metrics
                metrics_to_calculate = [
                    (
                        self.calculate_hub_current_statistics,
                        "hub_current_metrics",
                        "⚡ Hub Current Statistics",
                    ),
                    (
                        self.calculate_hub_voltage_statistics,
                        "hub_voltage_metrics",
                        "⚡ Hub Voltage Statistics",
                    ),
                    (
                        self.calculate_battery_current_statistics,
                        "battery_current_metrics",
                        "🔋 Battery Current Statistics",
                    ),
                    (
                        self.calculate_cht1_statistics,
                        "cht1_metrics",
                        "🌡️ CHT1 Statistics",
                    ),
                    (
                        self.calculate_cht2_statistics,
                        "cht2_metrics",
                        "🌡️ CHT2 Statistics",
                    ),
                    (
                        self.calculate_hub_throttle_statistics,
                        "hub_throttle_metrics",
                        "🎮 Hub Throttle Statistics",
                    ),
                    (
                        self.calculate_air_temp_statistics,
                        "air_temp_metrics",
                        "🌡️ Air Temperature Statistics",
                    ),
                    (
                        self.calculate_efficiency_statistics,
                        "efficiency_metrics",
                        "⚡ System Efficiency Statistics",
                    ),
                ]

                for calc_func, metric_key, verbose_header in metrics_to_calculate:
                    stats = calc_func(df)
                    if "error" not in stats:
                        results[metric_key] = stats
                        if verbose:
                            print(f"\n{verbose_header}:")
                            for key, value in stats.items():
                                print(f"   {key.replace('_', ' ').title()}: {value}")
                    else:
                        results["warnings"].append(stats["error"])

            except Exception as e:
                error_msg = f"Could not calculate metrics: {str(e)}"
                results["warnings"].append(error_msg)
                if verbose:
                    print(f"   ⚠️  Metrics calculation failed: {str(e)}")
                    print(f"   Traceback: {traceback.format_exc()}")

        except Exception as e:
            error_msg = f"Error processing CSV file: {str(e)}"
            results["errors"].append(error_msg)
            if verbose:
                print(f"   ❌ Error: {error_msg}")

        # Summary
        if verbose:
            print("\n📊 Extraction Summary:")
            print(f"   Errors: {len(results['errors'])}")
            print(f"   Warnings: {len(results['warnings'])}")

            if results["errors"]:
                print("   ❌ Errors found:")
                for error in results["errors"]:
                    print(f"      - {error}")

            if results["warnings"]:
                print("   ⚠️  Warnings:")
                for warning in results["warnings"]:
                    print(f"      - {warning}")

        return results

    def extract_binary_metadata(
        self, bin_data: Union[bytes, BinaryIO], bin_filename: str, verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Extract metadata from a binary file.

        Args:
            bin_data: Binary file data as bytes or file-like object
            bin_filename: Name of the binary file
            verbose: Whether to print detailed information during processing

        Returns:
            dict: Binary file metadata including:
                - Extraction timestamp
                - File information (size, format)
                - Filename metadata
                - Validation results
                - Errors/warnings
        """
        if verbose:
            print(f"\n🔧 Processing Binary file: {bin_filename}")

        results: Dict[str, Any] = {
            "extraction_timestamp": datetime.now().isoformat(),
            "file_info": {},
            "filename_metadata": {},
            "validation_results": {},
            "errors": [],
            "warnings": [],
        }

        try:
            # 1. Extract filename metadata
            results["filename_metadata"] = self.extract_filename_metadata(bin_filename)

            if verbose and results["filename_metadata"]["parsing_successful"]:
                print("   📋 Filename parsing: ✅ Success")
                print(f"      File Type: {results['filename_metadata']['fileType']}")
                print(
                    f"      Flight Date: {results['filename_metadata']['flightDate']}"
                )
                print(f"      Timestamp: {results['filename_metadata']['timestamp']}")

            # 2. Validate binary data
            validation = self.validate_data(bin_data, bin_filename)
            results["validation_results"] = {
                "is_valid": validation.is_valid,
                "message": validation.message,
                "warnings": validation.warnings,
            }

            # 3. Extract binary info
            bin_info = self.get_binary_info(bin_data)
            results["file_info"] = {
                "file_size_bytes": bin_info["data_size_bytes"],
                "file_size_mb": bin_info["data_size_mb"],
                "header_sample": bin_info["header_sample"][:50].hex(),
            }

            if verbose:
                print("   📈 Binary Info:")
                print(
                    f"      Size: {bin_info['data_size_bytes']:,} bytes ({bin_info['data_size_mb']:.2f} MB)"
                )

        except Exception as e:
            error_msg = f"Error processing binary file: {str(e)}"
            results["errors"].append(error_msg)
            if verbose:
                print(f"   ❌ Error: {error_msg}")

        # Summary
        if verbose:
            print("\n📊 Extraction Summary:")
            print(f"   Errors: {len(results['errors'])}")
            print(f"   Warnings: {len(results['warnings'])}")

            if results["errors"]:
                print("   ❌ Errors found:")
                for error in results["errors"]:
                    print(f"      - {error}")

            if results["warnings"]:
                print("   ⚠️  Warnings:")
                for warning in results["warnings"]:
                    print(f"      - {warning}")

        return results

    def calculate_efficiency_statistics(
        self,
        df: pd.DataFrame,
        hub_voltage_column: Optional[str] = None,
        hub_current_column: Optional[str] = None,
        hub_throttle_column: Optional[str] = None,
        hub_rpm_column: Optional[str] = None,
        da120_data_path: str = "DA120/",
    ) -> Dict[str, Any]:
        """
        Calculate system efficiency statistics from CSV data.

        Args:
            df: DataFrame containing engine data
            hub_voltage_column: Optional override for hub voltage column name
            hub_current_column: Optional override for hub current column name
            hub_throttle_column: Optional override for hub throttle column name
            hub_rpm_column: Optional override for hub RPM column name
            da120_data_path: Path to the DA120 data folder

        Returns:
            dict: System efficiency statistics including average, max, min, and standard deviation values
        """
        try:
            # Use provided column names or defaults from COLUMN_MAPPINGS
            hub_voltage_column = hub_voltage_column or COLUMN_MAPPINGS["hub"]["voltage"]
            hub_current_column = hub_current_column or COLUMN_MAPPINGS["hub"]["current"]
            hub_throttle_column = (
                hub_throttle_column or COLUMN_MAPPINGS["hub"]["throttle"]
            )
            hub_rpm_column = hub_rpm_column or COLUMN_MAPPINGS["hub"]["rpm"]

            # Check if all required columns exist
            required_columns = {
                "Hub voltage": hub_voltage_column,
                "Hub current": hub_current_column,
                "Hub throttle": hub_throttle_column,
                "Hub RPM": hub_rpm_column,
            }

            for name, col in required_columns.items():
                if col not in df.columns:
                    return {
                        "error": f'{name} column "{col}" not found',
                        "available_columns": list(df.columns),
                    }

            # Calculate HUB power
            hub_power = df[hub_voltage_column] * df[hub_current_column]

            # Calculate Engine power
            from XER_Technologies_metadata_extractor.utilities import throttle_function

            throttle_func = throttle_function(da120_data_path)
            rpm_values = df[hub_rpm_column].values.astype(float)
            throttle_values = df[hub_throttle_column].values.astype(float)
            engine_power = throttle_func.ev(rpm_values, throttle_values) * 1000

            # Calculate System efficiency
            system_efficiency = hub_power / engine_power * 100

            # Apply constraints using list comprehension
            system_efficiency = [
                0 if eff > 110 or eff <= 0 else eff for eff in system_efficiency
            ]

            # Calculate statistics
            stats = {
                "average_efficiency": float(pd.Series(system_efficiency).mean()),
                "max_efficiency": float(max(system_efficiency)),
                "min_efficiency": float(min(system_efficiency)),
                "std_dev_efficiency": float(pd.Series(system_efficiency).std()),
            }

            return stats

        except Exception as e:
            return {
                "error": f"Error calculating system efficiency statistics: {str(e)}"
            }

    # ----------------------### KPI CALCULATION METHODS ###----------------------

    def calculate_engine_working_hours(
        self,
        df: pd.DataFrame,
        rpm_column: Optional[str] = None,
        timestamp_column: Optional[str] = None,
        verbose: bool = False,
    ) -> Dict[str, Any]:
        """
        Calculate total engine working hours from CSV data.

        Args:
            df: DataFrame containing engine data
            rpm_column: Optional override for RPM column name
            timestamp_column: Optional override for timestamp column name
            verbose: Whether to print detailed information during processing

        Returns:
            dict: Engine working hours data and statistics
        """
        try:
            # Use provided column names or defaults from COLUMN_MAPPINGS
            rpm_column = rpm_column or COLUMN_MAPPINGS["engine"]["rpm"]
            timestamp_column = (
                timestamp_column or COLUMN_MAPPINGS["engine"]["timestamp"]
            )

            # Ensure we have the required columns
            if rpm_column not in df.columns or timestamp_column not in df.columns:
                return {
                    "error": f"Required columns not found. Need: {rpm_column}, {timestamp_column}",
                    "available_columns": list(df.columns),
                }

            if verbose:
                # Print timestamp info for debugging
                print("\nTimestamp Analysis:")
                print(f"  Column type: {df[timestamp_column].dtype}")
                print(f"  First few values: {df[timestamp_column].head().tolist()}")
                print(f"  Sample row: {df.iloc[0].to_dict()}")
                print(f"  Min timestamp: {df[timestamp_column].min()}")
                print(f"  Max timestamp: {df[timestamp_column].max()}")

            # Filter for non-zero RPM values (engine running)
            df_running = df[df[rpm_column] > 0].copy()

            if df_running.empty:
                return {
                    "total_hours": 0.0,
                    "total_seconds": 0.0,
                    "message": "No engine running periods detected",
                }

            if verbose:
                # Print running data info
                print("\nRunning Data Analysis:")
                print(f"  Total points: {len(df)}")
                print(f"  Running points: {len(df_running)}")
                print(
                    f"  Running timestamps: {df_running[timestamp_column].head().tolist()}"
                )

            # Calculate total time span in milliseconds
            time_span_ms = (
                df_running[timestamp_column].max() - df_running[timestamp_column].min()
            )

            if verbose:
                print("\nTime Calculations:")
                print(f"  Time span (ms): {time_span_ms}")

            # Calculate time differences between consecutive readings to detect gaps
            df_running["dtime"] = df_running[timestamp_column].diff()

            # Filter out large time gaps (likely data collection interruptions)
            # For millisecond timestamps, use 10000 ms (10 seconds) as max gap
            max_gap_ms = 10000  # 10 seconds max gap
            gaps = df_running[df_running["dtime"] > max_gap_ms]
            gaps_ms = float(gaps["dtime"].sum() if not gaps.empty else 0)

            if verbose:
                print(f"  Number of gaps: {len(gaps)}")
                print(f"  Total gap time (ms): {gaps_ms}")
                print(
                    f"  Average time between readings (ms): {df_running['dtime'].mean()}"
                )
                print(
                    f"  Median time between readings (ms): {df_running['dtime'].median()}"
                )

            # Calculate total runtime (time span minus gaps)
            total_seconds = float(
                (time_span_ms - gaps_ms) / 1000
            )  # Convert ms to seconds
            total_hours = round(
                total_seconds / 3600, 3
            )  # Convert to hours, 3 decimal places

            if verbose:
                print(f"  Total seconds: {total_seconds}")
                print(f"  Total hours: {total_hours}")

            return {
                "total_hours": total_hours,
                "total_seconds": total_seconds,
                "average_rpm": float(df_running[rpm_column].mean()),
                "max_rpm": float(df_running[rpm_column].max()),
                "min_rpm": float(df_running[rpm_column].min()),
                "data_points": len(df_running),
                "debug_info": {
                    "time_span_ms": float(time_span_ms),
                    "gaps_ms": gaps_ms,
                    "running_points": len(df_running),
                    "avg_time_between_readings_ms": float(df_running["dtime"].mean()),
                    "median_time_between_readings_ms": float(
                        df_running["dtime"].median()
                    ),
                },
            }

        except Exception as e:
            if verbose:
                print(f"\nError in engine hours calculation: {str(e)}")
            return {
                "error": f"Error calculating engine hours: {str(e)}",
                "total_hours": 0.0,
            }

    def calculate_engine_starts(
        self, df: pd.DataFrame, rpm_column: str = "HUB_RPM"
    ) -> Dict[str, Any]:
        """
        Calculate total engine starts from CSV data.

        Args:
            df: DataFrame containing engine data
            rpm_column: Name of the RPM column (default: 'HUB_RPM')

        Returns:
            dict: Engine starts data and statistics
        """
        try:
            if rpm_column not in df.columns:
                return {
                    "error": f'RPM column "{rpm_column}" not found',
                    "available_columns": list(df.columns),
                }

            # Create a boolean series for RPM transitions from 0 to >0 (engine starts)
            rpm_transitions = (df[rpm_column] > 0) & (df[rpm_column].shift(1) == 0)

            # Get indices where starts occur
            start_indices = df[rpm_transitions].index.tolist()
            total_starts = len(start_indices)

            # Calculate additional start-related metrics
            if total_starts > 0:
                # Get RPM values at start
                start_rpms = df.loc[start_indices, rpm_column].tolist()
                avg_start_rpm = round(sum(start_rpms) / len(start_rpms), 2)
                max_start_rpm = max(start_rpms)
                min_start_rpm = min(start_rpms)
            else:
                avg_start_rpm = max_start_rpm = min_start_rpm = 0

            return {
                "total_starts": total_starts,
                "start_indices": start_indices,
                "average_start_rpm": avg_start_rpm,
                "max_start_rpm": max_start_rpm,
                "min_start_rpm": min_start_rpm,
                "start_rpms": start_rpms if total_starts > 0 else [],
            }

        except Exception as e:
            return {
                "error": f"Error calculating engine starts: {str(e)}",
                "total_starts": 0,
            }

    def calculate_rpm_statistics(
        self, df: pd.DataFrame, rpm_column: str = "HUB_RPM"
    ) -> Dict[str, Any]:
        """
        Calculate RPM statistics from CSV data.

        Args:
            df: DataFrame containing engine data
            rpm_column: Name of the RPM column

        Returns:
            dict: RPM statistics including basic stats, operating stats, and change analysis
        """
        try:
            # Check if RPM column exists
            if rpm_column not in df.columns:
                return {
                    "error": f'RPM column "{rpm_column}" not found',
                    "available_columns": list(df.columns),
                }

            # Convert RPM column to numeric, replacing non-numeric values with NaN
            rpm_data = pd.to_numeric(df[rpm_column], errors="coerce")

            # Basic statistics (including zeros)
            basic_stats = {
                "count": int(rpm_data.count()),
                "mean": float(rpm_data.mean()),
                "median": float(rpm_data.median()),
                "std": float(rpm_data.std()),
                "min": float(rpm_data.min()),
                "max": float(rpm_data.max()),
            }

            # Operating statistics (excluding zeros)
            operating_rpm = rpm_data[rpm_data > 0]
            operating_stats = {
                "operating_count": int(operating_rpm.count()),
                "operating_mean": float(operating_rpm.mean()),
                "operating_median": float(operating_rpm.median()),
                "operating_std": float(operating_rpm.std()),
                "operating_min": float(operating_rpm.min()),
                "operating_max": float(operating_rpm.max()),
            }

            # RPM change analysis
            rpm_changes = rpm_data.diff().abs()
            change_stats = {
                "max_rpm_change": float(rpm_changes.max()),
                "avg_rpm_change": float(rpm_changes.mean()),
                "std_rpm_change": float(rpm_changes.std()),
            }

            # Calculate idle time percentage (RPM = 0)
            total_samples = len(rpm_data.dropna())
            idle_samples = len(rpm_data[rpm_data == 0].dropna())
            idle_percentage = (
                round((idle_samples / total_samples * 100), 2)
                if total_samples > 0
                else 0.0
            )

            return {
                "basic_statistics": basic_stats,
                "operating_statistics": operating_stats,
                "change_analysis": change_stats,
                "idle_time_percentage": idle_percentage,
            }

        except Exception as e:
            return {
                "error": f"Could not calculate RPM statistics: {str(e)}",
                "available_columns": list(df.columns),
            }

    def calculate_hub_current_statistics(
        self, df: pd.DataFrame, hub_current_column: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate hub current statistics from CSV data.

        Args:
            df: DataFrame containing engine data
            hub_current_column: Optional override for hub current column name

        Returns:
            dict: Hub current statistics including average, max, min, and standard deviation values
        """
        try:
            hub_current_column = hub_current_column or COLUMN_MAPPINGS["hub"]["current"]

            if hub_current_column not in df.columns:
                return {
                    "error": f'Hub current column "{hub_current_column}" not found',
                    "available_columns": list(df.columns),
                }

            hub_current_data = df[hub_current_column]

            # Calculate statistics
            stats = {
                "average_hub_current": round(hub_current_data.mean(), 2),
                "max_hub_current": round(hub_current_data.max(), 2),
                "min_hub_current": round(hub_current_data.min(), 2),
                "std_dev_hub_current": round(hub_current_data.std(), 2),
            }

            return stats

        except Exception as e:
            return {"error": f"Error calculating hub current statistics: {str(e)}"}

    def calculate_hub_voltage_statistics(
        self, df: pd.DataFrame, hub_voltage_column: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate hub voltage statistics from CSV data.

        Args:
            df: DataFrame containing engine data
            hub_voltage_column: Optional override for hub voltage column name

        Returns:
            dict: Hub voltage statistics including average, max, min, and standard deviation values
        """
        try:
            hub_voltage_column = hub_voltage_column or COLUMN_MAPPINGS["hub"]["voltage"]

            if hub_voltage_column not in df.columns:
                return {
                    "error": f'Hub voltage column "{hub_voltage_column}" not found',
                    "available_columns": list(df.columns),
                }

            hub_voltage_data = df[hub_voltage_column]

            # Calculate statistics
            stats = {
                "average_hub_voltage": round(hub_voltage_data.mean(), 2),
                "max_hub_voltage": round(hub_voltage_data.max(), 2),
                "min_hub_voltage": round(hub_voltage_data.min(), 2),
                "std_dev_hub_voltage": round(hub_voltage_data.std(), 2),
            }

            return stats

        except Exception as e:
            return {"error": f"Error calculating hub voltage statistics: {str(e)}"}

    def calculate_battery_current_statistics(
        self, df: pd.DataFrame, battery_current_column: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate battery current statistics from CSV data.

        Args:
            df: DataFrame containing engine data
            battery_current_column: Optional override for battery current column name

        Returns:
            dict: Battery current statistics including average, max, min, and standard deviation values
        """
        try:
            battery_current_column = (
                battery_current_column or COLUMN_MAPPINGS["battery"]["current"]
            )

            if battery_current_column not in df.columns:
                return {
                    "error": f'Battery current column "{battery_current_column}" not found',
                    "available_columns": list(df.columns),
                }

            battery_current_data = df[battery_current_column]

            # Calculate statistics
            stats = {
                "average_battery_current": round(battery_current_data.mean(), 2),
                "max_battery_current": round(battery_current_data.max(), 2),
                "min_battery_current": round(battery_current_data.min(), 2),
                "std_dev_battery_current": round(battery_current_data.std(), 2),
            }

            return stats

        except Exception as e:
            return {"error": f"Error calculating battery current statistics: {str(e)}"}

    def calculate_cht1_statistics(
        self, df: pd.DataFrame, cht1_column: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate CHT1 (Cylinder Head Temperature 1) statistics from CSV data.

        Args:
            df: DataFrame containing engine data
            cht1_column: Optional override for CHT1 column name

        Returns:
            dict: CHT1 statistics including average, max, min, and standard deviation values
        """
        try:
            cht1_column = cht1_column or COLUMN_MAPPINGS["temperature"]["cht1"]

            if cht1_column not in df.columns:
                return {
                    "error": f'CHT1 column "{cht1_column}" not found',
                    "available_columns": list(df.columns),
                }

            cht1_data = df[cht1_column]

            # Calculate statistics
            stats = {
                "average_cht1": round(cht1_data.mean(), 2),
                "max_cht1": round(cht1_data.max(), 2),
                "min_cht1": round(cht1_data.min(), 2),
                "std_dev_cht1": round(cht1_data.std(), 2),
            }

            return stats

        except Exception as e:
            return {"error": f"Error calculating CHT1 statistics: {str(e)}"}

    def calculate_cht2_statistics(
        self, df: pd.DataFrame, cht2_column: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate CHT2 (Cylinder Head Temperature 2) statistics from CSV data.

        Args:
            df: DataFrame containing engine data
            cht2_column: Optional override for CHT2 column name

        Returns:
            dict: CHT2 statistics including average, max, min, and standard deviation values
        """
        try:
            cht2_column = cht2_column or COLUMN_MAPPINGS["temperature"]["cht2"]

            if cht2_column not in df.columns:
                return {
                    "error": f'CHT2 column "{cht2_column}" not found',
                    "available_columns": list(df.columns),
                }

            cht2_data = df[cht2_column]

            # Calculate statistics
            stats = {
                "average_cht2": round(cht2_data.mean(), 2),
                "max_cht2": round(cht2_data.max(), 2),
                "min_cht2": round(cht2_data.min(), 2),
                "std_dev_cht2": round(cht2_data.std(), 2),
            }

            return stats

        except Exception as e:
            return {"error": f"Error calculating CHT2 statistics: {str(e)}"}

    def calculate_hub_throttle_statistics(
        self, df: pd.DataFrame, hub_throttle_column: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate hub throttle statistics from CSV data.

        Args:
            df: DataFrame containing engine data
            hub_throttle_column: Optional override for hub throttle column name

        Returns:
            dict: Hub throttle statistics including average, max, min, and standard deviation values
        """
        try:
            hub_throttle_column = (
                hub_throttle_column or COLUMN_MAPPINGS["hub"]["throttle"]
            )

            if hub_throttle_column not in df.columns:
                return {
                    "error": f'Hub throttle column "{hub_throttle_column}" not found',
                    "available_columns": list(df.columns),
                }

            hub_throttle_data = df[hub_throttle_column]

            # Calculate statistics
            stats = {
                "average_hub_throttle": round(hub_throttle_data.mean(), 2),
                "max_hub_throttle": round(hub_throttle_data.max(), 2),
                "min_hub_throttle": round(hub_throttle_data.min(), 2),
                "std_dev_hub_throttle": round(hub_throttle_data.std(), 2),
            }

            return stats

        except Exception as e:
            return {"error": f"Error calculating hub throttle statistics: {str(e)}"}

    def calculate_air_temp_statistics(
        self, df: pd.DataFrame, air_temp_column: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate air temperature statistics from CSV data.

        Args:
            df: DataFrame containing engine data
            air_temp_column: Optional override for air temperature column name

        Returns:
            dict: Air temperature statistics including average, max, min, and standard deviation values
        """
        try:
            air_temp_column = air_temp_column or COLUMN_MAPPINGS["temperature"]["air"]

            if air_temp_column not in df.columns:
                return {
                    "error": f'Air temperature column "{air_temp_column}" not found',
                    "available_columns": list(df.columns),
                }

            air_temp_data = df[air_temp_column]

            # Calculate statistics
            stats = {
                "average_air_temp": round(air_temp_data.mean(), 2),
                "max_air_temp": round(air_temp_data.max(), 2),
                "min_air_temp": round(air_temp_data.min(), 2),
                "std_dev_air_temp": round(air_temp_data.std(), 2),
            }

            return stats

        except Exception as e:
            return {"error": f"Error calculating air temperature statistics: {str(e)}"}
