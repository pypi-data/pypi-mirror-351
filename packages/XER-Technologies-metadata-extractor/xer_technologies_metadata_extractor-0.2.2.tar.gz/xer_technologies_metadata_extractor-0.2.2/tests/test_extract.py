"""
Tests for the XER Technologies Metadata Extractor.
"""

import random
from pathlib import Path
from typing import Any, Dict

import pandas as pd
import pytest

from XER_Technologies_metadata_extractor import (
    LocalFileAdapter,
    MetadataExtractor,
    S3Adapter,
)
from XER_Technologies_metadata_extractor.validation import ValidationResult


@pytest.fixture
def data_dir() -> Path:
    """Fixture providing the path to test data directory."""
    return Path(__file__).parent.parent / "data"


@pytest.fixture
def sample_csv_file(data_dir: Path) -> str:
    """Fixture providing a sample CSV file path."""
    csv_files = list(data_dir.glob("*.csv"))
    if not csv_files:
        pytest.skip("No CSV files found in data directory")
    print(f"📁 Using CSV file: {csv_files[0].name}")
    return csv_files[0].name


@pytest.fixture
def sample_bin_file(data_dir: Path) -> str:
    """Fixture providing a sample binary file path."""
    bin_files = list(data_dir.glob("*.bin"))
    if not bin_files:
        pytest.skip("No binary files found in data directory")
    print(f"📁 Using binary file: {bin_files[0].name}")
    return bin_files[0].name


@pytest.fixture
def local_adapter(data_dir: Path) -> LocalFileAdapter:
    """Fixture providing a LocalFileAdapter instance."""
    return LocalFileAdapter(str(data_dir))


@pytest.fixture
def core_extractor() -> MetadataExtractor:
    """Fixture providing a core MetadataExtractor instance."""
    return MetadataExtractor()


@pytest.fixture
def s3_adapter() -> S3Adapter:
    """Fixture providing an S3Adapter instance with mock credentials."""
    return S3Adapter(
        bucket_name="test-bucket",
        aws_access_key_id="test-key",
        aws_secret_access_key="test-secret",
        region_name="us-east-1",
    )


class TestCoreMetadataExtractor:
    """Test the core storage-agnostic MetadataExtractor."""

    def test_validate_data_csv(
        self, core_extractor: MetadataExtractor, data_dir: Path, sample_csv_file: str
    ) -> None:
        """Test CSV validation with bytes data."""
        csv_path = data_dir / sample_csv_file
        csv_data = csv_path.read_bytes()

        print(f"✅ Validating CSV: {sample_csv_file} ({len(csv_data):,} bytes)")

        result = core_extractor.validate_data(csv_data, sample_csv_file)
        assert isinstance(result, ValidationResult)
        assert result.is_valid
        print(f"   Validation result: {result.is_valid} - {result.message}")

    def test_validate_data_bin(
        self, core_extractor: MetadataExtractor, data_dir: Path, sample_bin_file: str
    ) -> None:
        """Test binary validation with bytes data."""
        bin_path = data_dir / sample_bin_file
        bin_data = bin_path.read_bytes()

        print(f"✅ Validating Binary: {sample_bin_file} ({len(bin_data):,} bytes)")

        result = core_extractor.validate_data(bin_data, sample_bin_file)
        assert isinstance(result, ValidationResult)
        assert result.is_valid
        print(f"   Validation result: {result.is_valid} - {result.message}")

    def test_validate_data_file_object(
        self, core_extractor: MetadataExtractor, data_dir: Path, sample_csv_file: str
    ) -> None:
        """Test validation with file-like object."""
        csv_path = data_dir / sample_csv_file

        with open(csv_path, "rb") as f:
            result = core_extractor.validate_data(f, sample_csv_file)
            assert isinstance(result, ValidationResult)
            assert result.is_valid
            print(f"✅ File object validation: {sample_csv_file} - {result.message}")

    def test_extract_from_csv_data(
        self, core_extractor: MetadataExtractor, data_dir: Path, sample_csv_file: str
    ) -> None:
        """Test CSV extraction from bytes and file objects."""
        csv_path = data_dir / sample_csv_file

        # Test with bytes
        csv_data = csv_path.read_bytes()
        df = core_extractor.extract_from_csv_data(csv_data)
        assert len(df) > 0
        assert len(df.columns) > 0
        print(
            f"📊 CSV extraction (bytes): {len(df):,} rows × {len(df.columns)} columns"
        )
        print(
            f"   Columns: {list(df.columns)[:5]}{'...' if len(df.columns) > 5 else ''}"
        )

        # Test with file object
        with open(csv_path, "rb") as f:
            df2 = core_extractor.extract_from_csv_data(f)
            assert len(df2) > 0
            assert len(df2.columns) > 0
            print(
                f"📊 CSV extraction (file obj): {len(df2):,} rows × {len(df2.columns)} columns"
            )

    def test_get_csv_info(
        self, core_extractor: MetadataExtractor, data_dir: Path, sample_csv_file: str
    ) -> None:
        """Test CSV info extraction without loading full data."""
        csv_path = data_dir / sample_csv_file
        csv_data = csv_path.read_bytes()

        info = core_extractor.get_csv_info(csv_data)
        assert "data_size_bytes" in info
        assert "total_rows" in info
        assert "total_columns" in info
        assert "columns" in info
        assert info["total_rows"] > 0
        assert info["total_columns"] > 0

        print(
            f"📈 CSV Info: {info['total_rows']:,} rows × {info['total_columns']} columns"
        )
        print(
            f"   Size: {info['data_size_bytes']:,} bytes ({info['data_size_bytes']/1024/1024:.2f} MB)"
        )
        print(
            f"   Columns: {info['columns'][:3]}{'...' if len(info['columns']) > 3 else ''}"
        )

    def test_get_binary_info(
        self, core_extractor: MetadataExtractor, data_dir: Path, sample_bin_file: str
    ) -> None:
        """Test binary info extraction."""
        bin_path = data_dir / sample_bin_file
        bin_data = bin_path.read_bytes()

        info = core_extractor.get_binary_info(bin_data)
        assert "data_size_bytes" in info
        assert "data_size_mb" in info
        assert "header_sample" in info
        assert info["data_size_bytes"] > 0

        print("🔧 Binary Info:")
        print(
            f"   Size: {info['data_size_bytes']:,} bytes ({info['data_size_mb']:.2f} MB)"
        )
        print(f"   Header sample (hex): {info['header_sample'][:20].hex()}")

    def test_extract_filename_metadata_successful(
        self, core_extractor: MetadataExtractor
    ) -> None:
        """Test extract_filename_metadata with successful parsing."""
        filename = "XFD_108_20250219_2007.csv"
        result = core_extractor.extract_filename_metadata(filename)

        assert result["filename"] == filename
        assert result["parsing_successful"] is True
        assert result["fileType"] == "XFD"
        assert result["serialNumber"] == "108"
        assert result["flightDate"] == "2025-02-19"
        assert result["timestamp"] == "2025-02-19T20:07:00"

        print(f"✅ Extract Metadata (Success): {filename}")
        print(f"   Parsed: {result['parsing_successful']}")
        print(f"   Type: {result['fileType']}")
        print(f"   Serial: {result['serialNumber']}")
        print(f"   Date: {result['flightDate']}")
        print(f"   Timestamp: {result['timestamp']}")

    def test_extract_filename_metadata_failure(
        self, core_extractor: MetadataExtractor
    ) -> None:
        """Test extract_filename_metadata with failed parsing."""
        filename = "invalid_file.csv"
        result = core_extractor.extract_filename_metadata(filename)

        assert result["filename"] == filename
        assert result["parsing_successful"] is False
        assert result["fileType"] == "XFD"  # CSV files are treated as XFD data
        assert result["serialNumber"] is None
        assert result["flightDate"] is None
        assert result["timestamp"] is None

        print(f"✅ Extract Metadata (Failure): {filename}")
        print(f"   Parsed: {result['parsing_successful']}")
        print(f"   Type: {result['fileType']}")

    def test_extract_metadata(
        self,
        core_extractor: MetadataExtractor,
        data_dir: Path,
        sample_csv_file: str,
        sample_bin_file: str,
    ) -> None:
        """Test metadata extraction for both CSV and binary files."""
        csv_path = data_dir / sample_csv_file
        bin_path = data_dir / sample_bin_file

        # Test CSV metadata extraction
        csv_data = csv_path.read_bytes()
        csv_result = core_extractor.extract_csv_metadata(
            csv_data=csv_data, csv_filename=sample_csv_file, verbose=True
        )

        assert "extraction_timestamp" in csv_result
        assert "file_info" in csv_result
        assert "filename_metadata" in csv_result
        assert "validation_results" in csv_result
        assert "engine_metrics" in csv_result
        assert "errors" in csv_result
        assert "warnings" in csv_result

        print("\n📋 CSV Metadata:")
        print(f"   Timestamp: {csv_result['extraction_timestamp']}")
        print(f"   File Info: {csv_result['file_info']}")
        print(f"   Filename Metadata: {csv_result['filename_metadata']}")
        print(f"   Validation: {csv_result['validation_results']}")
        print(f"   Engine Metrics: {csv_result['engine_metrics']}")
        print(f"   Errors: {csv_result['errors']}")
        print(f"   Warnings: {csv_result['warnings']}")

        # Test binary metadata extraction
        bin_data = bin_path.read_bytes()
        bin_result = core_extractor.extract_binary_metadata(
            bin_data=bin_data, bin_filename=sample_bin_file, verbose=True
        )

        assert "extraction_timestamp" in bin_result
        assert "file_info" in bin_result
        assert "filename_metadata" in bin_result
        assert "validation_results" in bin_result
        assert "errors" in bin_result
        assert "warnings" in bin_result

        print("\n📋 Binary Metadata:")
        print(f"   Timestamp: {bin_result['extraction_timestamp']}")
        print(f"   File Info: {bin_result['file_info']}")
        print(f"   Filename Metadata: {bin_result['filename_metadata']}")
        print(f"   Validation: {bin_result['validation_results']}")
        print(f"   Errors: {bin_result['errors']}")
        print(f"   Warnings: {bin_result['warnings']}")


class TestLocalFileAdapter:
    """Test the LocalFileAdapter."""

    def test_extract_metadata(
        self,
        local_adapter: LocalFileAdapter,
        sample_csv_file: str,
        sample_bin_file: str,
    ) -> None:
        """Test metadata extraction through adapter."""
        # Test CSV extraction
        csv_result = local_adapter.extract_metadata(
            csv_file=sample_csv_file, verbose=True
        )

        assert "extraction_timestamp" in csv_result
        assert "file_info" in csv_result
        assert "filename_metadata" in csv_result
        assert "validation_results" in csv_result
        assert "engine_metrics" in csv_result
        assert "errors" in csv_result
        assert "warnings" in csv_result

        print("\n📋 Local Adapter CSV Metadata Extraction:")
        print(f"   Timestamp: {csv_result['extraction_timestamp']}")
        print(f"   File Info: {csv_result['file_info']}")
        print(f"   Filename Metadata: {csv_result['filename_metadata']}")
        print(f"   Validation: {csv_result['validation_results']}")
        print(f"   Engine Metrics: {csv_result['engine_metrics']}")
        print(f"   Errors: {csv_result['errors']}")
        print(f"   Warnings: {csv_result['warnings']}")

        # Test Binary extraction
        bin_result = local_adapter.extract_metadata(
            bin_file=sample_bin_file, verbose=True
        )

        assert "extraction_timestamp" in bin_result
        assert "file_info" in bin_result
        assert "filename_metadata" in bin_result
        assert "validation_results" in bin_result
        assert "errors" in bin_result
        assert "warnings" in bin_result

        print("\n📋 Local Adapter Binary Metadata Extraction:")
        print(f"   Timestamp: {bin_result['extraction_timestamp']}")
        print(f"   File Info: {bin_result['file_info']}")
        print(f"   Filename Metadata: {bin_result['filename_metadata']}")
        print(f"   Validation: {bin_result['validation_results']}")
        print(f"   Errors: {bin_result['errors']}")
        print(f"   Warnings: {bin_result['warnings']}")


class TestS3Adapter:
    """Test the S3Adapter."""

    def test_extract_metadata(
        self, s3_adapter: S3Adapter, sample_csv_file: str, sample_bin_file: str
    ) -> None:
        """Test metadata extraction through adapter."""
        # Test CSV extraction
        csv_result = s3_adapter.extract_metadata(
            csv_object_key=sample_csv_file, verbose=True
        )

        assert "extraction_timestamp" in csv_result
        assert "file_info" in csv_result
        assert "filename_metadata" in csv_result
        assert "validation_results" in csv_result
        assert "engine_metrics" in csv_result
        assert "errors" in csv_result
        assert "warnings" in csv_result

        print("\n📋 S3 Adapter CSV Metadata Extraction:")
        print(f"   Timestamp: {csv_result['extraction_timestamp']}")
        print(f"   File Info: {csv_result['file_info']}")
        print(f"   Filename Metadata: {csv_result['filename_metadata']}")
        print(f"   Validation: {csv_result['validation_results']}")
        print(f"   Engine Metrics: {csv_result['engine_metrics']}")
        print(f"   Errors: {csv_result['errors']}")
        print(f"   Warnings: {csv_result['warnings']}")

        # Test Binary extraction
        bin_result = s3_adapter.extract_metadata(
            bin_object_key=sample_bin_file, verbose=True
        )

        assert "extraction_timestamp" in bin_result
        assert "file_info" in bin_result
        assert "filename_metadata" in bin_result
        assert "validation_results" in bin_result
        assert "errors" in bin_result
        assert "warnings" in bin_result

        print("\n📋 S3 Adapter Binary Metadata Extraction:")
        print(f"   Timestamp: {bin_result['extraction_timestamp']}")
        print(f"   File Info: {bin_result['file_info']}")
        print(f"   Filename Metadata: {bin_result['filename_metadata']}")
        print(f"   Validation: {bin_result['validation_results']}")
        print(f"   Errors: {bin_result['errors']}")
        print(f"   Warnings: {bin_result['warnings']}")


class TestKPICalculationMethods:
    """Test the KPI calculation methods for engine and flight data analysis."""

    @pytest.fixture
    def sample_engine_data(self) -> pd.DataFrame:
        """Create sample engine data for testing KPI calculations."""
        # Create sample data with engine starts and running periods
        timestamps = []
        rpms = []
        current_time = 1000  # Start at 1 second

        # First period: Engine off
        for _ in range(20):
            timestamps.append(current_time)
            rpms.append(0)  # Engine off
            current_time += 100

        # First start and running period
        for _ in range(80):
            timestamps.append(current_time)
            rpms.append(
                1500 + random.randint(-50, 50)
            )  # Engine running around 1500 RPM
            current_time += 100

        # Add a gap and engine stop
        current_time += 15000  # 15 second gap
        for _ in range(20):
            timestamps.append(current_time)
            rpms.append(0)  # Engine off again
            current_time += 100

        # Second start and running period
        for _ in range(80):
            timestamps.append(current_time)
            rpms.append(1500 + random.randint(-50, 50))  # Engine running again
            current_time += 100

        return pd.DataFrame(
            {
                "time": timestamps,  # Changed from 'timestamp' to 'time' to match the default
                "HUB_RPM": rpms,  # This matches the default rpm_column name
            }
        )

    def test_calculate_engine_working_hours(
        self, core_extractor: MetadataExtractor, sample_engine_data: pd.DataFrame
    ) -> None:
        """Test engine working hours calculation."""
        print("Testing engine working hours calculation")

        result = core_extractor.calculate_engine_working_hours(
            sample_engine_data, verbose=True
        )

        # Verify structure
        assert "total_hours" in result
        assert "total_seconds" in result
        assert "average_rpm" in result
        assert "max_rpm" in result
        assert "min_rpm" in result

        # Verify calculations
        assert result["total_hours"] > 0
        assert result["total_seconds"] > 0
        assert result["average_rpm"] > 0

        print(
            f"   Engine Hours: {result['total_hours']} hours ({result['total_seconds']} seconds)"
        )
        print(f"   Average RPM: {result['average_rpm']}")
        print(f"   RPM Range: {result['min_rpm']} - {result['max_rpm']}")
        print("✅ Engine working hours calculation successful")

    def test_calculate_engine_starts(
        self, core_extractor: MetadataExtractor, sample_engine_data: pd.DataFrame
    ) -> None:
        """Test engine starts calculation."""
        print("\n🚀 Testing engine starts calculation")

        result = core_extractor.calculate_engine_starts(sample_engine_data)

        # Verify structure
        assert "total_starts" in result
        assert "start_indices" in result
        assert "average_start_rpm" in result
        assert "max_start_rpm" in result
        assert "min_start_rpm" in result

        # Should detect at least one start (0 -> >0 transition)
        assert result["total_starts"] >= 1
        assert len(result["start_indices"]) == result["total_starts"]

        print(f"   Total Starts: {result['total_starts']}")
        print(f"   Start Indices: {result['start_indices']}")
        print(f"   Average Start RPM: {result['average_start_rpm']}")
        print(
            f"   Start RPM Range: {result['min_start_rpm']} - {result['max_start_rpm']}"
        )
        print("✅ Engine starts calculation successful")

    def test_calculate_rpm_statistics(
        self, core_extractor: MetadataExtractor, sample_engine_data: pd.DataFrame
    ) -> None:
        """Test RPM statistics calculation."""
        print("\n📊 Testing RPM statistics calculation")

        result = core_extractor.calculate_rpm_statistics(sample_engine_data)

        # Verify structure
        assert "basic_statistics" in result
        assert "operating_statistics" in result
        assert "change_analysis" in result
        assert "idle_time_percentage" in result

        # Verify basic statistics
        basic_stats = result["basic_statistics"]
        assert "count" in basic_stats
        assert "mean" in basic_stats
        assert "median" in basic_stats
        assert "std" in basic_stats
        assert "min" in basic_stats
        assert "max" in basic_stats

        # Verify operating statistics
        operating_stats = result["operating_statistics"]
        assert "operating_count" in operating_stats
        assert "operating_mean" in operating_stats

        # Verify change analysis
        change_stats = result["change_analysis"]
        assert "max_rpm_change" in change_stats
        assert "avg_rpm_change" in change_stats

        print(
            f"   Basic Stats - Count: {basic_stats['count']}, Mean: {basic_stats['mean']}, Range: {basic_stats['min']}-{basic_stats['max']}"
        )
        print(
            f"   Operating Stats - Count: {operating_stats['operating_count']}, Mean: {operating_stats['operating_mean']}"
        )
        print(
            f"   Change Analysis - Max Change: {change_stats['max_rpm_change']}, Avg Change: {change_stats['avg_rpm_change']}"
        )
        print(f"   Idle Time: {result['idle_time_percentage']}%")
        print("✅ RPM statistics calculation successful")

    def test_kpi_error_handling(self, core_extractor: MetadataExtractor) -> None:
        """Test KPI calculation error handling."""
        print("\n⚠️  Testing KPI error handling")

        # Test with missing columns
        invalid_df = pd.DataFrame({"wrong_column": [1, 2, 3]})

        # Test engine hours with missing columns
        result = core_extractor.calculate_engine_working_hours(invalid_df, verbose=True)
        assert "error" in result
        print(f"   Missing columns error: {result['error']}")

        # Test engine starts with missing RPM column
        result = core_extractor.calculate_engine_starts(invalid_df)
        assert "error" in result
        print(f"   Missing RPM column error: {result['error']}")

        # Test with empty DataFrame
        empty_df = pd.DataFrame({"HUB_RPM": [], "time": []})
        result = core_extractor.calculate_engine_working_hours(empty_df, verbose=True)
        assert "total_hours" in result
        assert result["total_hours"] == 0.0
        print(f"   Empty data handling: {result.get('message', 'Handled correctly')}")

        print("✅ Error handling test completed")

    def test_kpi_with_real_csv_data(
        self, core_extractor: MetadataExtractor, data_dir: Path
    ) -> None:
        """Test KPI calculation with real CSV data if available."""
        print("\n📈 Testing KPI with real CSV data")

        csv_files = list(data_dir.glob("*.csv"))
        if not csv_files:
            print("   No CSV files found - skipping real data test")
            return

        try:
            # Load first CSV file
            csv_path = csv_files[0]
            df = pd.read_csv(csv_path)

            print(f"   Using file: {csv_path.name}")
            print(f"   Data shape: {df.shape}")
            print(
                f"   Columns: {list(df.columns)[:5]}{'...' if len(df.columns) > 5 else ''}"
            )

            # Check if we have RPM-like columns
            rpm_columns = [col for col in df.columns if "RPM" in col.upper()]
            timestamp_columns = [
                col
                for col in df.columns
                if any(word in col.lower() for word in ["time", "timestamp"])
            ]

            if rpm_columns and timestamp_columns:
                rpm_col = rpm_columns[0]
                timestamp_col = timestamp_columns[0]

                print(f"   Using RPM column: {rpm_col}")
                print(f"   Using timestamp column: {timestamp_col}")

                # Calculate individual KPIs
                engine_hours = core_extractor.calculate_engine_working_hours(
                    df, rpm_column=rpm_col, timestamp_column=timestamp_col
                )
                engine_starts = core_extractor.calculate_engine_starts(
                    df, rpm_column=rpm_col
                )
                rpm_stats = core_extractor.calculate_rpm_statistics(
                    df, rpm_column=rpm_col
                )

                print("   Real Data KPIs:")
                print(f"     Engine Hours: {engine_hours.get('total_hours', 0)}")
                print(f"     Total Starts: {engine_starts.get('total_starts', 0)}")
                print(
                    f"     Average RPM: {rpm_stats['operating_statistics'].get('operating_mean', 0)}"
                )
                print("✅ Real data KPI calculation successful")
            else:
                print("   No suitable RPM/timestamp columns found")
                print(f"   Available columns: {list(df.columns)}")

        except Exception as e:
            print(f"   Error processing real data: {str(e)}")

        print("✅ Real data test completed")

    def test_extract_metadata_from_data_dir(
        self, core_extractor: MetadataExtractor, data_dir: Path
    ) -> None:
        """
        Simple test to demonstrate metadata extraction from files in the data directory.
        Can be run independently with:
        pytest tests/test_extract.py::TestKPICalculationMethods::test_extract_metadata_from_data_dir -v -s
        """
        print("\n📂 Testing metadata extraction from data directory")

        # Find CSV and binary files
        csv_files = list(data_dir.glob("*.csv"))
        bin_files = list(data_dir.glob("*.bin"))

        if not csv_files and not bin_files:
            pytest.skip("No CSV or binary files found in data directory")

        print(f"\nFound {len(csv_files)} CSV files and {len(bin_files)} binary files")

        # Process first CSV file if available
        if csv_files:
            csv_path = csv_files[0]
            print(f"\n📊 Processing CSV file: {csv_path.name}")

            with open(csv_path, "rb") as f:
                csv_data = f.read()

            # Extract CSV metadata using the new method
            result = core_extractor.extract_csv_metadata(
                csv_data=csv_data,
                csv_filename=csv_path.name,
                verbose=False,  # Disable verbose mode for raw results
            )

            print("\n🔍 Raw Metadata Results (CSV):")
            print(f"{result}")

            # Then show formatted results
            print("\n📋 Formatted Metadata Structure:")

            def print_dict(d: Dict[str, Any], indent: int = 0) -> None:
                for key, value in d.items():
                    if isinstance(value, dict):
                        print("  " * indent + f"{key}:")
                        print_dict(value, indent + 1)
                    elif (
                        isinstance(value, list) and value and isinstance(value[0], dict)
                    ):
                        print("  " * indent + f"{key}: [{len(value)} items]")
                        for item in value[:2]:  # Show first 2 items
                            print_dict(item, indent + 1)
                        if len(value) > 2:
                            print("  " * (indent + 1) + "...")
                    else:
                        if isinstance(value, list) and len(value) > 3:
                            value = f"[{len(value)} items]"
                        print("  " * indent + f"{key}: {value}")

            print_dict(result)

        # Process first binary file if available
        if bin_files:
            bin_path = bin_files[0]
            print(f"\n🔧 Processing binary file: {bin_path.name}")

            with open(bin_path, "rb") as f:
                bin_data = f.read()

            # Extract binary metadata using the new method
            result = core_extractor.extract_binary_metadata(
                bin_data=bin_data, bin_filename=bin_path.name, verbose=False
            )

            print("\n🔍 Raw Metadata Results (Binary):")
            print(f"{result}")

            # Then show formatted results
            print("\n📋 Binary Metadata Structure:")
            print_dict(result)

        print("\n✅ Metadata extraction demonstration completed")
