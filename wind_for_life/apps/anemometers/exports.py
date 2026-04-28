"""Export utilities for anemometer readings."""

import csv
import io


class ReadingExporter:
    """Handles data export in multiple formats."""

    @staticmethod
    def to_json(serialized_readings: list[dict]) -> list[dict]:
        """Return readings data ready for JSON serialization.

        Args:
            serialized_readings: List of dictionaries with reading data.

        Returns:
            The same data, ready to be returned in HTTP response.
        """
        return serialized_readings

    @staticmethod
    def to_csv(serialized_readings: list[dict]) -> str:
        """Render serialized readings as CSV string.

        Args:
            serialized_readings: List of dictionaries with reading data.

        Returns:
            CSV-formatted string.
        """
        if not serialized_readings:
            return ""

        output = io.StringIO()
        fieldnames = list(serialized_readings[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for reading in serialized_readings:
            # Convert list tags to comma-separated string for CSV
            row = {**reading}
            if "tags" in row and isinstance(row["tags"], list):
                row["tags"] = ",".join(row["tags"])
            writer.writerow(row)

        return output.getvalue()

