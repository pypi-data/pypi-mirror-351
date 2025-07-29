"""
Validation module for XER Technologies Metadata Extractor.

Provides validation functions for CSV and binary files.
"""

from typing import List, NamedTuple, Optional

from XER_Technologies_metadata_extractor.config import (
    BIN_FILENAME_PATTERN,
    CSV_ENCODING,
    MIN_BIN_FILE_SIZE,
    MIN_CSV_LINES,
    XFD_COLUMNS,
    XFD_FILENAME_PREFIX,
)


class ValidationResult(NamedTuple):
    """Result of file validation with detailed feedback."""

    is_valid: bool
    message: str
    detected_version: Optional[str] = None
    warnings: List[str] = []


class FileValidator:
    """Handles validation of CSV and binary files for metadata extraction."""

    def __init__(self) -> None:
        """Initialize the file validator."""
        pass

    def precheck_csv_file(self, file_data: bytes, filename: str) -> ValidationResult:
        """
        Comprehensive precheck for CSV files with XFD format validation.

        Args:
            file_data: Raw file data as bytes
            filename: Name of the file being validated

        Returns:
            ValidationResult with validation status, message, version, and warnings
        """
        warnings: List[str] = []

        # Basic file checks
        basic_check = self._basic_file_checks(file_data, filename, ".csv")
        if not basic_check.is_valid:
            return basic_check

        # Check filename convention
        if not filename.startswith(XFD_FILENAME_PREFIX):
            warnings.append(
                f"File '{filename}' doesn't follow the standard XFD naming convention "
                f"(expected: XFD_108_20250219_2007.csv) but will be processed as XFD data."
            )

        # Decode and parse CSV content
        try:
            content = file_data.decode(CSV_ENCODING)
        except UnicodeDecodeError as e:
            return ValidationResult(
                is_valid=False,
                message=f"CSV file is not properly encoded (expected {CSV_ENCODING}): {str(e)}",
            )

        lines = content.strip().split("\n")

        # Check minimum line count
        if len(lines) < MIN_CSV_LINES:
            return ValidationResult(
                is_valid=False,
                message=f"CSV file has insufficient data (found {len(lines)} lines, minimum {MIN_CSV_LINES} required)",
            )

        # Validate CSV structure and XFD format
        header = [col.strip() for col in lines[0].split(",")]
        data_sample = lines[1:MIN_CSV_LINES]  # Sample for validation

        structure_result = self._validate_csv_structure(header, data_sample)
        if not structure_result.is_valid:
            return ValidationResult(
                is_valid=False, message=structure_result.message, warnings=warnings
            )

        # Validate XFD columns
        xfd_result = self._validate_xfd_columns(header)
        if not xfd_result.is_valid:
            return ValidationResult(
                is_valid=False, message=xfd_result.message, warnings=warnings
            )

        return ValidationResult(
            is_valid=True,
            message=f"CSV file validation successful. Detected XFD format {xfd_result.detected_version}",
            detected_version=xfd_result.detected_version,
            warnings=warnings,
        )

    def precheck_bin_file(self, file_data: bytes, filename: str) -> ValidationResult:
        """
        Comprehensive precheck for binary files (Mission Planner format).

        Args:
            file_data: Raw file data as bytes
            filename: Name of the file being validated

        Returns:
            ValidationResult with validation status, message, and warnings
        """
        warnings: List[str] = []

        # Basic file checks
        basic_check = self._basic_file_checks(file_data, filename, ".bin")
        if not basic_check.is_valid:
            return basic_check

        # Check minimum file size for Mission Planner files
        if len(file_data) < MIN_BIN_FILE_SIZE:
            return ValidationResult(
                is_valid=False,
                message=f"BIN file is too small ({len(file_data)} bytes). "
                f"Mission Planner files typically require at least {MIN_BIN_FILE_SIZE} bytes.",
            )

        # Validate filename format
        import re

        if not re.search(BIN_FILENAME_PATTERN, filename, re.IGNORECASE):
            return ValidationResult(
                is_valid=False,
                message="BIN file name should follow the format: YYYY-MM-DD HH-MM-SS.bin "
                f"(e.g., 2025-01-15 14-30-45.bin). Found: {filename}",
            )

        # Validate Mission Planner binary format
        format_result = self._validate_mission_planner_format(file_data)
        if not format_result.is_valid:
            return ValidationResult(
                is_valid=False, message=format_result.message, warnings=warnings
            )

        return ValidationResult(
            is_valid=True,
            message="BIN file validation successful. Valid Mission Planner format detected.",
            warnings=warnings,
        )

    def _basic_file_checks(
        self, file_data: bytes, filename: str, expected_ext: str
    ) -> ValidationResult:
        """Perform basic file validation checks."""
        if not filename:
            return ValidationResult(is_valid=False, message="Filename is required")

        if not file_data:
            return ValidationResult(is_valid=False, message="File data is empty")
        import os

        file_extension = os.path.splitext(filename)[1].lower()
        if file_extension != expected_ext:
            return ValidationResult(
                is_valid=False,
                message=f"Expected {expected_ext} file, got {file_extension}",
            )

        return ValidationResult(is_valid=True, message="Basic checks passed")

    def _validate_csv_structure(
        self, header: List[str], data_sample: List[str]
    ) -> ValidationResult:
        """Validate basic CSV structure and detect extra columns."""
        if not header:
            return ValidationResult(is_valid=False, message="CSV header is empty")

        header_col_count = len(header)

        # Check for extra columns in data rows
        for i, row in enumerate(data_sample, 1):
            if not row.strip():  # Skip empty rows
                continue

            columns = [col.strip() for col in row.split(",")]
            if len(columns) > header_col_count:
                return ValidationResult(
                    is_valid=False,
                    message=f"Row {i} has {len(columns)} columns but header has {header_col_count}. "
                    f"Extra columns detected without corresponding headers.",
                )

        return ValidationResult(is_valid=True, message="CSV structure is valid")

    def _validate_xfd_columns(self, header: List[str]) -> ValidationResult:
        """Validate XFD column format and detect version."""
        # Check if version is embedded in the header line (e.g., " XFD_version 3.1.1")
        version_from_header = None
        cleaned_header = []

        for col in header:
            col_stripped = col.strip()
            if "XFD_version" in col_stripped:
                # Extract version from header like " XFD_version 3.1.1"
                import re

                version_match = re.search(r"XFD_version\s+([\d.]+)", col_stripped)
                if version_match:
                    version_from_header = f"v{version_match.group(1)}"
                # Don't include this in the column list for comparison
                continue
            cleaned_header.append(col_stripped)

        header_set = {col.lower() for col in cleaned_header}

        # If we found a version in the header, validate against that specific version
        if version_from_header and version_from_header in XFD_COLUMNS:
            expected_set = {col.lower() for col in XFD_COLUMNS[version_from_header]}
            missing_columns = expected_set - header_set
            extra_columns = header_set - expected_set

            if not missing_columns and not extra_columns:
                return ValidationResult(
                    is_valid=True,
                    message=f"Valid XFD format version {version_from_header}",
                    detected_version=version_from_header,
                )
            elif missing_columns:
                return ValidationResult(
                    is_valid=False,
                    message=f"XFD {version_from_header} format missing columns: {sorted(missing_columns)}",
                )
            elif extra_columns:
                return ValidationResult(
                    is_valid=False,
                    message=f"XFD {version_from_header} format has extra columns: {sorted(extra_columns)}",
                )

        # Check each version's columns against the header (fallback for files without version in header)
        for version, expected_columns in XFD_COLUMNS.items():
            expected_set = {col.lower() for col in expected_columns}
            missing_columns = expected_set - header_set

            if not missing_columns:
                # All expected columns found for this version
                extra_columns = header_set - expected_set
                if extra_columns:
                    return ValidationResult(
                        is_valid=False,
                        message=f"Extra columns found that don't match XFD {version} format: {sorted(extra_columns)}",
                    )

                return ValidationResult(
                    is_valid=True,
                    message=f"Valid XFD format version {version}",
                    detected_version=version,
                )

        # Find the version with the fewest missing columns for better error reporting
        best_match = min(
            XFD_COLUMNS.items(),
            key=lambda x: len(set(col.lower() for col in x[1]) - header_set),
        )

        missing = set(col.lower() for col in best_match[1]) - header_set

        return ValidationResult(
            is_valid=False,
            message=f"Could not match any XFD version. Closest match is {best_match[0]} "
            f"but missing columns: {sorted(missing)}",
        )

    def _validate_mission_planner_format(self, file_data: bytes) -> ValidationResult:
        """Validate Mission Planner binary format."""
        # Mission Planner .bin files typically start with specific headers
        # This is a basic validation - you may need to adjust based on your specific requirements

        # Check for common Mission Planner signatures
        # Mission Planner logs often contain specific message types in the first few bytes
        try:
            # Look for common Mission Planner message headers in the first 100 bytes
            header_sample = file_data[:100]

            # Mission Planner files often contain ASCII message type identifiers
            # Common ones include: FMT, PARM, GPS, IMU, etc.
            common_mp_headers = [b"FMT", b"PARM", b"GPS", b"IMU", b"BARO", b"MAG"]

            found_headers = []
            for header in common_mp_headers:
                if header in header_sample:
                    found_headers.append(header.decode("ascii"))

            if found_headers:
                return ValidationResult(
                    is_valid=True,
                    message=f"Mission Planner format detected (found headers: {', '.join(found_headers)})",
                )

            # If no specific headers found, check if it looks like binary data
            # Mission Planner files should not be pure text
            try:
                header_sample.decode("ascii")
                # If it decodes as ASCII, it might not be a proper binary file
                return ValidationResult(
                    is_valid=False,
                    message="File appears to be text-based, not a Mission Planner binary file",
                )
            except UnicodeDecodeError:
                # Good, it's binary data
                return ValidationResult(
                    is_valid=True,
                    message="Binary format detected (no specific Mission Planner headers found, but appears to be valid binary data)",
                )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"Error validating Mission Planner format: {str(e)}",
            )
