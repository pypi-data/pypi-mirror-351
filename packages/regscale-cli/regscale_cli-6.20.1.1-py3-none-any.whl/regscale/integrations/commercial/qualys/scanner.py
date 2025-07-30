"""
Qualys Total Cloud scanner integration class using JSONLScannerIntegration.
"""

import logging
import os
import time
import traceback
import xml.etree.ElementTree as ET
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union, TextIO

from pathlib import Path
from rich.progress import Progress, TextColumn, BarColumn, SpinnerColumn, TimeElapsedColumn, TaskID

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.integrations.commercial.qualys.variables import QualysVariables
from regscale.integrations.jsonl_scanner_integration import JSONLScannerIntegration
from regscale.integrations.scanner_integration import (
    IntegrationAsset,
    IntegrationFinding,
    issue_due_date,
    ScannerIntegrationType,
)
from regscale.integrations.variables import ScannerVariables
from regscale.models import AssetStatus, IssueSeverity, IssueStatus

logger = logging.getLogger("regscale")

NO_RESULTS = "No results available"
NO_DESCRIPTION = "No description available"
NO_REMEDIATION = "No remediation information available"


class QualysTotalCloudJSONLIntegration(JSONLScannerIntegration):
    """Class for handling Qualys Total Cloud scanner integration using JSONL."""

    title: str = "Qualys Total Cloud"
    asset_identifier_field: str = "qualysId"
    finding_severity_map: Dict[str, Any] = {
        "0": IssueSeverity.NotAssigned.value,
        "1": IssueSeverity.Low.value,
        "2": IssueSeverity.Moderate.value,
        "3": IssueSeverity.Moderate.value,
        "4": IssueSeverity.High.value,
        "5": IssueSeverity.Critical.value,
    }

    finding_status_map = {
        "New": IssueStatus.Open,
        "Active": IssueStatus.Open,
        "Fixed": IssueStatus.Closed,
    }

    # Constants for file paths
    ASSETS_FILE = "./artifacts/qualys_total_cloud_assets.jsonl"
    FINDINGS_FILE = "./artifacts/qualys_total_cloud_findings.jsonl"

    def __init__(self, *args, **kwargs):
        """
        Initialize the QualysTotalCloudJSONLIntegration object.

        :param Any *args: Variable positional arguments
        :param Any **kwargs: Variable keyword arguments
        """
        self.type = ScannerIntegrationType.VULNERABILITY
        self.xml_data = kwargs.pop("xml_data", None)
        # Setting a dummy file path to avoid validation errors
        if self.xml_data and "file_path" not in kwargs:
            kwargs["file_path"] = None

        # Apply ScannerVariables settings
        if not kwargs.get("vulnerability_creation"):
            # Check QualysVariables-specific override first
            if hasattr(QualysVariables, "vulnerabilityCreation") and QualysVariables.vulnerabilityCreation:
                kwargs["vulnerability_creation"] = QualysVariables.vulnerabilityCreation
                logger.info(f"Using Qualys-specific vulnerability creation mode: {kwargs['vulnerability_creation']}")
            # Use global ScannerVariables if no Qualys-specific setting
            elif hasattr(ScannerVariables, "vulnerabilityCreation"):
                kwargs["vulnerability_creation"] = ScannerVariables.vulnerabilityCreation
                logger.info(f"Using global vulnerability creation mode: {kwargs['vulnerability_creation']}")

        # Apply SSL verification setting from ScannerVariables
        if not kwargs.get("ssl_verify") and hasattr(ScannerVariables, "sslVerify"):
            kwargs["ssl_verify"] = ScannerVariables.sslVerify
            logger.debug(f"Using SSL verification setting: {kwargs['ssl_verify']}")

        # Apply ScannerVariables.threadMaxWorkers if available
        if not kwargs.get("max_workers") and hasattr(ScannerVariables, "threadMaxWorkers"):
            kwargs["max_workers"] = ScannerVariables.threadMaxWorkers
            logger.debug(f"Using thread max workers: {kwargs['max_workers']}")

        super().__init__(*args, **kwargs)
        # No need to initialize clients, they are inherited from the parent class

    def is_valid_file(self, data: Any, file_path: Union[Path, str]) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Check if the XML data is valid for Qualys Total Cloud.

        :param Any data: XML data to validate
        :param Union[Path, str] file_path: Path to the file (not used in this implementation)
        :return: Tuple of (is_valid, data)
        :rtype: Tuple[bool, Optional[Dict[str, Any]]]
        """
        # This would normally check the file structure, but for XML data we'll assume it's valid
        # if it contains HOST_LIST_VM_DETECTION_OUTPUT
        if not data or not isinstance(data, dict):
            logger.warning("Data is not a dictionary")
            return False, None

        if "HOST_LIST_VM_DETECTION_OUTPUT" not in data:
            logger.warning("Data does not contain HOST_LIST_VM_DETECTION_OUTPUT")
            return False, None

        return True, data

    def find_valid_files(self, path: Union[Path, str]) -> Iterator[Tuple[Union[Path, str], Dict[str, Any]]]:
        """
        Process XML data instead of files on disk.

        :param Union[Path, str] path: Path (not used in this implementation)
        :return: Iterator yielding tuples of (dummy path, XML data)
        :rtype: Iterator[Tuple[Union[Path, str], Dict[str, Any]]]
        """
        if not self.xml_data:
            logger.error("No XML data provided for Qualys integration")
            return

        # Use a dummy file path since we're processing XML data directly
        dummy_path = "qualys_xml_data.xml"
        is_valid, validated_data = self.is_valid_file(self.xml_data, dummy_path)

        if is_valid and validated_data is not None:
            yield dummy_path, validated_data

    def parse_asset(self, file_path: Union[Path, str] = None, data: Dict[str, Any] = None, host=None):
        """
        Parse a single asset from a Qualys host data.

        :param Union[Path, str] file_path: Path to the file (included for compatibility)
        :param Dict[str, Any] data: The parsed data (included for compatibility)
        :param host: XML Element or dictionary representing a host
        :return: IntegrationAsset object
        :rtype: IntegrationAsset
        """
        # Handle the case when the file_path contains the host data (common in tests)
        if isinstance(file_path, dict) and not host and not data:
            host = file_path

        # Use host parameter if provided (for backward compatibility)
        if host is None:
            host = data  # In this implementation, we treat data as the host

        # Handle None input gracefully
        if host is None:
            logger.warning("No host data provided to parse_asset")
            # Generate a placeholder asset with minimal information
            return IntegrationAsset(
                name="Unknown-Qualys-Asset",
                identifier=str(int(time.time())),  # Use timestamp as fallback ID
                asset_type="Server",
                asset_category="IT",
                status=AssetStatus.Active,
                parent_id=self.plan_id,
                parent_module="securityplans",
                notes="Generated for missing Qualys data",
            )

        # Convert XML Element to dict if necessary
        if not isinstance(host, dict) and hasattr(host, "tag"):  # It's an XML Element
            host = self._xml_element_to_dict(host)

        # Process dictionary
        if isinstance(host, dict):
            # Check if we got the full data structure or just a host dictionary
            if "HOST_LIST_VM_DETECTION_OUTPUT" in host:
                # Navigate to the HOST data within the nested structure
                try:
                    host = (
                        host.get("HOST_LIST_VM_DETECTION_OUTPUT", {})
                        .get("RESPONSE", {})
                        .get("HOST_LIST", {})
                        .get("HOST", {})
                    )
                except (AttributeError, KeyError):
                    logger.error("Could not navigate to HOST data in dictionary")
                    raise ValueError("Invalid host data structure")

            # Extract host data from dictionary
            host_id = host.get("ID", "")
            ip = host.get("IP", "")
            dns = host.get("DNS", "")
            os = host.get("OS", "")
            last_scan = host.get("LAST_SCAN_DATETIME", "")
            network_id = host.get("NETWORK_ID", "")

            # Try to get FQDN from DNS_DATA if available
            fqdn = None
            dns_data = host.get("DNS_DATA", {})
            if dns_data:
                fqdn = dns_data.get("FQDN", "")

            asset = IntegrationAsset(
                name=dns or ip or f"QualysAsset-{host_id}",
                identifier=host_id,
                asset_type="Server",
                asset_category="IT",
                ip_address=ip,
                fqdn=fqdn,
                operating_system=os,
                status=AssetStatus.Active,
                external_id=host_id,
                date_last_updated=last_scan,
                mac_address=None,
                vlan_id=network_id,
                notes=f"Qualys Asset ID: {host_id}",
                parent_id=self.plan_id,
                parent_module="securityplans",
            )
            return asset

        # If we got here, we don't know how to handle the data
        logger.error(f"Unexpected host data type: {type(host)}")
        raise ValueError(f"Cannot parse asset from data type: {type(host)}")

    def parse_finding(
        self,
        asset_identifier: str = None,
        data: Dict[str, Any] = None,
        item: Dict[str, Any] = None,
        detection=None,
        host_id=None,
    ):
        """
        Parse a single finding from a Qualys detection.

        :param str asset_identifier: The identifier of the asset this finding belongs to (for compatibility)
        :param Dict[str, Any] data: The asset data (not used in this implementation, for compatibility)
        :param Dict[str, Any] item: The finding data (for compatibility)
        :param detection: XML Element or dict representing a detection
        :param host_id: Host ID this detection belongs to
        :return: IntegrationFinding object
        :rtype: IntegrationFinding
        """
        # For backward compatibility
        detection_to_use = detection if detection is not None else item
        host_id_to_use = host_id if host_id is not None else asset_identifier

        # Handle None input gracefully
        if detection_to_use is None:
            logger.warning("No detection data provided to parse_finding")
            # Use host_id or generate a placeholder if none provided
            if not host_id_to_use:
                host_id_to_use = f"unknown-host-{int(time.time())}"

            # Generate a placeholder finding with minimal information
            return IntegrationFinding(
                title="Unknown Qualys Finding",
                description="No detection data was provided",
                severity=IssueSeverity.Low.value,
                status=IssueStatus.Open,
                plugin_name="QID-unknown",
                plugin_id=self.title,
                asset_identifier=host_id_to_use,
                category="Vulnerability",
                scan_date=self.scan_date or get_current_datetime(),
                external_id=f"unknown-finding-{int(time.time())}",
            )

        # Convert XML Element to dict if necessary
        if not isinstance(detection_to_use, dict) and hasattr(detection_to_use, "tag"):  # It's an XML Element
            detection_to_use = self._xml_element_to_dict(detection_to_use)

        return self._parse_finding_from_dict(detection_to_use, host_id_to_use)

    def _parse_finding_from_dict(self, detection, host_id):
        """
        Parse a finding from a dictionary representation.

        :param detection: Dictionary containing finding data
        :param host_id: Host ID this detection belongs to
        :return: IntegrationFinding object
        """
        # Validate detection is a dictionary
        if not isinstance(detection, dict):
            logger.warning(f"Expected dictionary for detection, got {type(detection)}")
            detection = {}  # Use empty dict to prevent further errors

        # Extract basic finding information
        finding_data = self._extract_basic_finding_data_dict(detection)

        # Get CVE information
        finding_data["cve_id"] = self._extract_cve_id_from_dict(detection)

        # Extract issue data
        self._extract_issue_data_from_dict(detection, finding_data)

        # Build evidence
        finding_data["evidence"] = self._build_evidence(
            finding_data.get("qid", "Unknown"),
            host_id or "unknown-host",
            finding_data.get("first_found", self.scan_date or get_current_datetime()),
            finding_data.get("last_found", self.scan_date or get_current_datetime()),
            finding_data.get("results", NO_RESULTS),
        )

        # Create the finding object
        finding = self._create_finding_object(finding_data, host_id or "unknown-host")

        # Normalize dates for JSON serialization
        self._normalize_finding_dates(finding)

        return finding

    def _extract_basic_finding_data_dict(self, detection: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract basic finding information from dictionary data.

        :param Dict[str, Any] detection: Detection data
        :return: Dictionary with basic finding data
        :rtype: Dict[str, Any]
        """
        if not detection:
            detection = {}  # Ensure we have at least an empty dict

        current_time = self.scan_date or get_current_datetime()

        return {
            "qid": detection.get("QID", "Unknown"),
            "severity": detection.get("SEVERITY", "0"),
            "status": detection.get("STATUS", "New"),
            "first_found": detection.get("FIRST_FOUND_DATETIME", current_time),
            "last_found": detection.get("LAST_FOUND_DATETIME", current_time),
            "unique_id": detection.get("UNIQUE_VULN_ID", f"QID-{detection.get('QID', 'Unknown')}"),
            "results": detection.get("RESULTS", NO_RESULTS),
            "cvss_v3_score": detection.get("CVSS3_BASE"),
            "cvss_v3_vector": detection.get("CVSS3_VECTOR", ""),
            "cvss_v2_score": detection.get("CVSS_BASE"),
            "cvss_v2_vector": detection.get("CVSS_VECTOR", ""),
        }

    def _extract_basic_finding_data_xml(self, detection: Optional[Union[Dict[str, Any], ET.Element]]) -> Dict[str, Any]:
        """
        Deprecated: Convert to dict first then use _extract_basic_finding_data_dict.

        :param Optional[Union[Dict[str, Any], ET.Element]] detection: Detection data as dictionary or XML Element
        :return: Dictionary with basic finding data
        :rtype: Dict[str, Any]
        """
        if detection is None:
            # Return default values if detection is None
            return {
                "qid": "Unknown",
                "severity": "0",
                "status": "New",
                "first_found": self.scan_date,
                "last_found": self.scan_date,
                "unique_id": "Unknown",
                "results": NO_RESULTS,
                "cvss_v3_score": None,
                "cvss_v3_vector": "",
                "cvss_v2_score": None,
                "cvss_v2_vector": "",
            }

        # Convert XML to dict if needed
        if not isinstance(detection, dict) and hasattr(detection, "tag"):
            detection = self._xml_element_to_dict(detection)

        # Use dict extraction method
        return self._extract_basic_finding_data_dict(detection)

    def _extract_cve_id_from_dict(self, detection: Optional[Dict[str, Any]]) -> str:
        """
        Extract CVE ID from dictionary data.

        :param Optional[Dict[str, Any]] detection: Detection data
        :return: CVE ID string
        :rtype: str
        """
        if not detection:
            return ""

        cve_id = ""
        try:
            cve_list = detection.get("CVE_ID_LIST", {})
            if not cve_list:
                return ""

            if not isinstance(cve_list, dict):
                logger.warning(f"Expected dictionary for CVE_ID_LIST, got {type(cve_list)}")
                return ""

            if "CVE_ID" in cve_list:
                cve_data = cve_list.get("CVE_ID", [])
                if isinstance(cve_data, list) and cve_data:
                    cve_id = str(cve_data[0]) if cve_data[0] else ""
                elif isinstance(cve_data, str):
                    cve_id = cve_data
                elif cve_data:
                    # Try to convert to string if it's something else
                    cve_id = str(cve_data)
        except Exception as e:
            logger.warning(f"Error extracting CVE_ID: {str(e)}")

        return cve_id

    def _extract_cve_id_from_xml(self, detection: Optional[Union[Dict[str, Any], ET.Element]]) -> str:
        """
        Deprecated: Convert to dict first then use _extract_cve_id_from_dict.

        :param Optional[Union[Dict[str, Any], ET.Element]] detection: Detection data as dictionary or XML Element
        :return: CVE ID string
        :rtype: str
        """
        if detection is None:
            return ""

        # Convert XML to dict if needed
        if not isinstance(detection, dict) and hasattr(detection, "tag"):
            detection = self._xml_element_to_dict(detection)

        # Use dict extraction method
        return self._extract_cve_id_from_dict(detection)

    def _extract_issue_data_from_dict(self, detection: Optional[Dict[str, Any]], finding_data: Dict[str, Any]) -> None:
        """
        Extract issue data from dictionary and update finding_data in place.

        :param Optional[Dict[str, Any]] detection: Detection data
        :param Dict[str, Any] finding_data: Finding data to update
        :return: None
        """
        if not detection:
            detection = {}

        qid = finding_data.get("qid", "Unknown")
        issue_data = detection.get("ISSUE_DATA", {})

        # Default values
        finding_data["title"] = f"Qualys Vulnerability QID-{qid}"
        finding_data["diagnosis"] = NO_DESCRIPTION
        finding_data["solution"] = NO_REMEDIATION

        # Update with actual values if present
        if issue_data:
            if isinstance(issue_data, dict):
                finding_data["title"] = issue_data.get("TITLE", finding_data["title"])
                finding_data["diagnosis"] = issue_data.get("DIAGNOSIS", finding_data["diagnosis"])
                finding_data["solution"] = issue_data.get("SOLUTION", finding_data["solution"])
            else:
                logger.warning(f"Expected dictionary for ISSUE_DATA, got {type(issue_data)}")

        # Ensure values are strings
        finding_data["title"] = (
            str(finding_data["title"]) if finding_data["title"] else f"Qualys Vulnerability QID-{qid}"
        )
        finding_data["diagnosis"] = str(finding_data["diagnosis"]) if finding_data["diagnosis"] else NO_DESCRIPTION
        finding_data["solution"] = str(finding_data["solution"]) if finding_data["solution"] else NO_REMEDIATION

    def _extract_issue_data_from_xml(
        self, detection: Optional[Union[Dict[str, Any], ET.Element]], finding_data: Dict[str, Any]
    ) -> None:
        """
        Deprecated: Convert to dict first then use _extract_issue_data_from_dict.

        :param Optional[Union[Dict[str, Any], ET.Element]] detection: Detection data as dictionary or XML Element
        :param Dict[str, Any] finding_data: Finding data to update
        :return: None
        """
        if detection is None:
            # Set default values
            qid = finding_data["qid"]
            finding_data["title"] = f"Qualys Vulnerability QID-{qid}"
            finding_data["diagnosis"] = NO_DESCRIPTION
            finding_data["solution"] = NO_REMEDIATION
            return

        # Convert XML to dict if needed
        if not isinstance(detection, dict) and hasattr(detection, "tag"):
            detection = self._xml_element_to_dict(detection)

        # Use dict extraction method
        self._extract_issue_data_from_dict(detection, finding_data)

    def _build_evidence(self, qid: str, host_id: str, first_found: str, last_found: str, results: Optional[str]) -> str:
        """
        Build evidence string from finding data.

        :param str qid: QID identifier
        :param str host_id: Host ID
        :param str first_found: First found datetime
        :param str last_found: Last found datetime
        :param Optional[str] results: Results data
        :return: Formatted evidence string
        :rtype: str
        """
        evidence_parts = [
            f"QID: {qid}",
            f"Host ID: {host_id}",
            f"First Found: {first_found}",
            f"Last Found: {last_found}",
        ]

        if results:
            evidence_parts.append(f"\nResults:\n{results}")

        return "\n".join(evidence_parts)

    def _create_finding_object(self, finding_data: Dict[str, Any], host_id: str) -> IntegrationFinding:
        """
        Create IntegrationFinding object from extracted finding data.

        :param Dict[str, Any] finding_data: Finding data dictionary
        :param str host_id: Host ID
        :return: IntegrationFinding object
        :rtype: IntegrationFinding
        """
        if not finding_data:
            finding_data = {}  # Ensure we have at least an empty dict

        severity_value = self.finding_severity_map.get(finding_data.get("severity", "0"), IssueSeverity.Moderate.value)

        # Get current time for any missing date fields
        current_time = self.scan_date or get_current_datetime()
        qid = finding_data.get("qid", "Unknown")

        return IntegrationFinding(
            title=finding_data.get("title", f"Qualys Vulnerability QID-{qid}"),
            description=finding_data.get("diagnosis", NO_DESCRIPTION),
            severity=severity_value,
            status=self.get_finding_status(finding_data.get("status", "New")),
            cvss_v3_score=finding_data.get("cvss_v3_score"),
            cvss_v3_vector=finding_data.get("cvss_v3_vector", ""),
            cvss_v2_score=finding_data.get("cvss_v2_score"),
            cvss_v2_vector=finding_data.get("cvss_v2_vector", ""),
            plugin_name=f"QID-{qid}",
            plugin_id=self.title,
            asset_identifier=host_id,
            category="Vulnerability",
            cve=finding_data.get("cve_id", ""),
            control_labels=[f"QID-{qid}"],
            evidence=finding_data.get("evidence", "No evidence available"),
            identified_risk=finding_data.get("title", f"Qualys Vulnerability QID-{qid}"),
            recommendation_for_mitigation=finding_data.get("solution", NO_REMEDIATION),
            scan_date=current_time,
            first_seen=finding_data.get("first_found", current_time),
            last_seen=finding_data.get("last_found", current_time),
            external_id=finding_data.get("unique_id", f"QID-{qid}-{host_id}"),
            due_date=issue_due_date(
                severity=severity_value,
                created_date=finding_data.get("first_found", current_time),
                title=self.title,
                config=self.app.config,
            ),
        )

    def _normalize_finding_dates(self, finding):
        """Ensure all dates are strings for JSON serialization."""
        date_fields = ["scan_date", "first_seen", "last_seen", "due_date"]

        for field in date_fields:
            value = getattr(finding, field, None)
            if not isinstance(value, str) and value:
                setattr(finding, field, value.isoformat() if hasattr(value, "isoformat") else str(value))

    def _get_findings_data_from_file(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract findings data from Qualys XML data.

        :param Dict[str, Any] data: The data from the XML
        :return: List of finding items
        :rtype: List[Dict[str, Any]]
        """
        host_list = data.get("HOST_LIST_VM_DETECTION_OUTPUT", {}).get("RESPONSE", {}).get("HOST_LIST")
        hosts = host_list.get("HOST", []) if host_list else []

        if isinstance(hosts, dict):
            hosts = [hosts]

        findings = []
        for host in hosts:
            host_id = host.get("ID", "")
            detection_list = host.get("DETECTION_LIST", {})
            detections = detection_list.get("DETECTION", []) if detection_list else []

            if isinstance(detections, dict):
                detections = [detections]

            for detection in detections:
                detection["host_id"] = host_id  # Add host_id to each detection
                findings.append(detection)

        return findings

    def _build_evidence_from_detection(self, item: Dict[str, Any], host: Dict[str, Any]) -> str:
        """
        Build evidence string from detection data.

        :param Dict[str, Any] item: Detection data
        :param Dict[str, Any] host: Host data
        :return: Formatted evidence string
        :rtype: str
        """
        evidence_parts = [
            f"QID: {item.get('QID', 'Unknown')}",
            f"Host: {host.get('IP', 'Unknown')} ({host.get('DNS', 'Unknown')})",
            f"OS: {host.get('OS', 'Unknown')}",
            f"First Found: {item.get('FIRST_FOUND_DATETIME', 'Unknown')}",
            f"Last Found: {item.get('LAST_FOUND_DATETIME', 'Unknown')}",
        ]

        if item.get("RESULTS"):
            evidence_parts.append(f"\nResults:\n{item.get('RESULTS')}")

        return "\n".join(evidence_parts)

    def _build_remediation(self, item: Dict[str, Any]) -> str:
        """
        Build remediation string from detection data.

        :param Dict[str, Any] item: Detection data
        :return: Formatted remediation string
        :rtype: str
        """
        if item.get("SOLUTION"):
            return item.get("SOLUTION")
        return "No remediation information available."

    def _get_cve_id(self, item: Dict[str, Any]) -> str:
        """
        Extract CVE ID from detection data.

        :param Dict[str, Any] item: Detection data
        :return: CVE ID if available
        :rtype: str
        """
        # Check for CVEs in the item
        if item.get("CVE_ID_LIST", {}).get("CVE_ID"):
            cve_data = item.get("CVE_ID_LIST", {}).get("CVE_ID", [])
            if isinstance(cve_data, list) and cve_data:
                return cve_data[0]
            elif isinstance(cve_data, str):
                return cve_data

        return ""

    def fetch_assets_and_findings(self, file_path: str = None, empty_files: bool = True):
        """
        Fetch assets and findings from Qualys Total Cloud JSONL file or XML data.
        This method orchestrates the process flow based on input type.

        :param str file_path: Path to source file or directory (for compatibility with parent class)
        :param bool empty_files: Whether to empty both output files before writing (for compatibility)
        :return: None or Tuple of (assets_iterator, findings_iterator) for compatibility with parent class
        """
        if file_path:
            self.file_path = file_path
        self.empty_files = empty_files

        self._verify_file_path()
        self._prepare_output_files()

        try:
            if self.xml_data:
                self._process_xml_data()
            else:
                self._process_jsonl_file(file_path, empty_files)

            # For compatibility with parent class that returns iterators
            if self.xml_data:
                assets_iterator = self._yield_items_from_jsonl(self.ASSETS_FILE, IntegrationAsset)
                findings_iterator = self._yield_items_from_jsonl(self.FINDINGS_FILE, IntegrationFinding)
                return assets_iterator, findings_iterator
        except Exception as e:
            logger.error(f"Error fetching assets and findings: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def _verify_file_path(self):
        """Verify that the file path exists if provided."""
        if self.file_path and not os.path.isfile(self.file_path):
            logger.error(f"QualysTotalCloudJSONLIntegration file path does not exist: {self.file_path}")
            raise FileNotFoundError(f"File path does not exist: {self.file_path}")

    def _prepare_output_files(self):
        """Create output directories and clear existing output files."""
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(self.ASSETS_FILE), exist_ok=True)
        os.makedirs(os.path.dirname(self.FINDINGS_FILE), exist_ok=True)

        # Clear any existing output files
        if os.path.exists(self.ASSETS_FILE):
            os.remove(self.ASSETS_FILE)
        if os.path.exists(self.FINDINGS_FILE):
            os.remove(self.FINDINGS_FILE)

    def _process_xml_data(self):
        """Process XML data from string or dictionary format."""
        logger.info("Processing XML data directly")

        if isinstance(self.xml_data, str):
            self._process_xml_string()
        elif isinstance(self.xml_data, dict):
            self._process_xml_dict()
        else:
            logger.error(f"Unsupported XML data type: {type(self.xml_data)}")

    def _process_xml_string(self):
        """Process XML data provided as a string."""
        logger.debug("Parsing XML string data")
        try:
            # Convert XML string to dictionary first, then process it
            xml_dict = self._convert_xml_string_to_dict(self.xml_data)
            self.xml_data = xml_dict  # Replace string with dict for consistent processing
            self._process_xml_dict()  # Use the dict processing pathway
        except Exception as e:
            logger.error(f"Error processing XML string: {str(e)}")
            logger.debug(traceback.format_exc())

    def _convert_xml_string_to_dict(self, xml_string: str) -> Dict[str, Any]:
        """
        Convert an XML string to a dictionary.

        :param str xml_string: XML string to convert
        :return: Dictionary representation of the XML
        :rtype: Dict[str, Any]
        """
        try:
            root = ET.fromstring(xml_string)
            return self._xml_element_to_dict(root)
        except ET.ParseError as e:
            logger.error(f"Error parsing XML: {str(e)}")
            return {}

    def _process_xml_dict(self):
        """Process XML data provided as a dictionary."""
        logger.debug("Using already parsed XML data (dict)")

        # Find all hosts in the XML data dictionary
        hosts_data = self._extract_hosts_from_dict()
        if not hosts_data:
            return

        num_hosts = len(hosts_data)
        logger.info(f"Found {num_hosts} hosts in XML dictionary data")

        # Extract all findings
        all_findings = self._extract_findings_from_hosts(hosts_data)
        num_findings = len(all_findings)
        logger.info(f"Found {num_findings} total findings in XML dictionary data")

        # Process assets and findings
        self._process_dict_assets_and_findings(hosts_data, all_findings)

    def _extract_hosts_from_dict(self):
        """Extract host data from XML dictionary structure."""
        hosts_data = (
            self.xml_data.get("HOST_LIST_VM_DETECTION_OUTPUT", {})
            .get("RESPONSE", {})
            .get("HOST_LIST", {})
            .get("HOST", [])
        )

        # Normalize to ensure hosts_data is always a list
        if isinstance(hosts_data, dict):
            hosts_data = [hosts_data]

        return hosts_data

    @staticmethod
    def _extract_findings_from_hosts(hosts_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract all findings from host data dictionaries.
        :param List[Dict[str, Any]] hosts_data: List of host data dictionaries
        :return: List of findings dictionaries
        :rtype: List[Dict[str, Any]]
        """
        all_findings = []
        for host in hosts_data:
            host_id = host.get("ID", "")
            detections = host.get("DETECTION_LIST", {}).get("DETECTION", [])

            # Normalize to ensure detections is always a list
            if isinstance(detections, dict):
                detections = [detections]

            for detection in detections:
                detection["host_id"] = host_id
                all_findings.append(detection)

        return all_findings

    def _process_dict_assets_and_findings(self, hosts_data, all_findings):
        """Process assets and findings from dictionary data."""
        with open(self.ASSETS_FILE, "w") as assets_file, open(self.FINDINGS_FILE, "w") as findings_file:
            self._write_assets_from_dict(assets_file, hosts_data)
            self._write_findings_from_dict(findings_file, all_findings)

    def _write_assets_from_dict(self, assets_file, hosts_data):
        """Write assets from dictionary data to JSONL file."""
        assets_written = 0
        for host in hosts_data:
            try:
                asset = self.parse_asset(host=host)
                self._write_item(assets_file, asset)
                assets_written += 1
            except Exception as e:
                logger.error(f"Error processing asset: {str(e)}")
                logger.debug(traceback.format_exc())

        logger.info(f"Wrote {assets_written} assets to {self.ASSETS_FILE}")

    def _write_findings_from_dict(self, findings_file, all_findings):
        """Write findings from dictionary data to JSONL file."""
        findings_written = 0
        for finding in all_findings:
            try:
                host_id = finding.get("host_id", "")
                parsed_finding = self.parse_finding(detection=finding, host_id=host_id)
                self._write_item(findings_file, parsed_finding)
                findings_written += 1
            except Exception as e:
                logger.error(f"Error processing finding: {str(e)}")
                logger.debug(traceback.format_exc())

        logger.info(f"Wrote {findings_written} findings to {self.FINDINGS_FILE}")

    def _process_xml_elements(self, hosts):
        """Process XML element hosts and detections with progress tracking."""
        # Convert XML elements to dictionaries first
        hosts_dict = self._convert_xml_elements_to_dict(hosts)
        all_findings = []

        # Extract all findings with host_ids
        for host in hosts_dict:
            host_id = host.get("ID", "")
            detections = host.get("DETECTION_LIST", {}).get("DETECTION", [])

            # Normalize to ensure detections is always a list
            if isinstance(detections, dict):
                detections = [detections]

            # Add host_id to each detection and collect
            for detection in detections:
                detection["host_id"] = host_id
                all_findings.append(detection)

        # Now process using the dictionary methods
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("({task.completed}/{task.total})"),
            TimeElapsedColumn(),
        ) as progress:
            # Setup progress tasks
            asset_task = progress.add_task("[cyan]Processing assets...", total=len(hosts_dict))
            finding_task = progress.add_task("[green]Processing findings...", total=len(all_findings))

            # Process using dictionary methods with progress tracking
            with open(self.ASSETS_FILE, "w") as assets_file, open(self.FINDINGS_FILE, "w") as findings_file:
                self._process_dict_assets_with_progress(hosts_dict, assets_file, progress, asset_task)
                # Use the findings list we extracted instead of trying to extract again
                self._process_findings_list_with_progress(all_findings, findings_file, progress, finding_task)

    def _process_dict_assets_with_progress(self, hosts_dict, assets_file, progress, asset_task):
        """Process assets from dictionaries with progress tracking."""
        assets_written = 0
        host_ids_processed = set()

        for host in hosts_dict:
            progress.update(asset_task, advance=1)
            try:
                host_id = host.get("ID", "")
                if host_id and host_id not in host_ids_processed:
                    asset = self.parse_asset(host=host)
                    self._write_item(assets_file, asset)
                    assets_written += 1
                    host_ids_processed.add(host_id)
            except Exception as e:
                logger.error(f"Error parsing asset: {str(e)}")
                logger.debug(traceback.format_exc())

        logger.info(f"Wrote {assets_written} unique assets to {self.ASSETS_FILE}")

    def _process_findings_list_with_progress(
        self, findings: List[Dict[str, Any]], findings_file: TextIO, progress: Progress, finding_task: TaskID
    ) -> None:
        """
        Process a list of finding dictionaries with progress tracking.

        :param List[Dict[str, Any]] findings: List of finding dictionaries
        :param TextIO findings_file: Open file handle for writing findings
        :param Progress progress: Progress tracker
        :param TaskID finding_task: Task ID for progress tracking
        :return: None
        """
        findings_written = 0
        finding_ids_processed = set()

        for finding in findings:
            progress.update(finding_task, advance=1)

            try:
                host_id = finding.get("host_id", "")
                # Get unique finding ID
                unique_id = self._get_detection_unique_id(finding, host_id)

                if unique_id and unique_id not in finding_ids_processed:
                    parsed_finding = self.parse_finding(detection=finding, host_id=host_id)
                    self._write_item(findings_file, parsed_finding)
                    findings_written += 1
                    finding_ids_processed.add(unique_id)
            except Exception as e:
                logger.error(f"Error parsing finding: {str(e)}")
                logger.debug(traceback.format_exc())

        logger.info(f"Wrote {findings_written} unique findings to {self.FINDINGS_FILE}")

    def _process_jsonl_file(self, file_path: Optional[str] = None, empty_files: bool = True) -> None:
        """
        Process JSONL file using parent class implementation.

        :param Optional[str] file_path: Path to JSONL file to process, defaults to None
        :param bool empty_files: Whether to empty files before processing, defaults to True
        :return: None
        """
        logger.info(f"Processing JSONL file: {self.file_path}")
        super().fetch_assets_and_findings(file_path, empty_files)

    def update_regscale_assets(self, assets_iterator: Iterator[IntegrationAsset]) -> int:
        """
        Update RegScale with assets.

        :param Iterator[IntegrationAsset] assets_iterator: Iterator of assets
        :return: Number of assets created
        :rtype: int
        """
        # Use the parent class implementation
        return super().update_regscale_assets(assets_iterator)

    def _extract_host_and_detections(self, host):
        """Extract host ID and detections from host data.

        :param host: Host data (dict or XML Element)
        :return: Tuple of (host_id, detections)
        """
        # Convert XML to dict if needed
        if not isinstance(host, dict) and hasattr(host, "tag"):
            host = self._xml_element_to_dict(host)

        host_id = host.get("ID", "")
        detections = host.get("DETECTION_LIST", {}).get("DETECTION", [])

        # Normalize to ensure detections is always a list
        if isinstance(detections, dict):
            detections = [detections]

        return host_id, detections

    def _convert_xml_elements_to_dict(self, elements: List[ET.Element]) -> List[Dict[str, Any]]:
        """
        Convert XML elements to a list of dictionaries.

        :param List[ET.Element] elements: List of XML Element objects
        :return: List of dictionaries with the same data
        :rtype: List[Dict[str, Any]]
        """
        result: List[Dict[str, Any]] = []
        for element in elements:
            result.append(self._xml_element_to_dict(element))
        return result

    def _xml_element_to_dict(self, element: Optional[ET.Element]) -> Dict[str, Any]:
        """
        Convert a single XML element to a dictionary with all its data.

        :param Optional[ET.Element] element: XML Element object
        :return: Dictionary with the element's data
        :rtype: Dict[str, Any]
        """
        if element is None:
            return {}

        result: Dict[str, Any] = {}

        # Add attributes
        for key, value in element.attrib.items():
            result[key] = value

        # Add text content if element has no children
        if len(element) == 0:
            text = element.text
            if text is not None and text.strip():
                # If this is a leaf node with text, just return the text
                return text.strip()

        # Add child elements
        for child in element:
            child_data = self._xml_element_to_dict(child)
            tag = child.tag

            # Handle multiple elements with the same tag
            if tag in result:
                if isinstance(result[tag], list):
                    result[tag].append(child_data)
                else:
                    result[tag] = [result[tag], child_data]
            else:
                result[tag] = child_data

        return result

    def _get_detection_unique_id(self, detection: Union[Dict[str, Any], ET.Element], host_id: str) -> str:
        """
        Get a unique identifier for a detection.

        :param Union[Dict[str, Any], ET.Element] detection: Detection data as dictionary or XML Element
        :param str host_id: Host ID
        :return: Unique identifier string
        :rtype: str
        """
        # Convert XML to dict if needed
        if not isinstance(detection, dict) and hasattr(detection, "tag"):
            detection = self._xml_element_to_dict(detection)

        qid = detection.get("QID", "")
        unique_id = detection.get("UNIQUE_VULN_ID", f"{host_id}-{qid}")

        return unique_id

    def get_finding_status(self, status: Optional[str]) -> IssueStatus:
        """
        Convert the Qualys status to a RegScale issue status.

        :param Optional[str] status: The status from Qualys
        :return: RegScale IssueStatus
        :rtype: IssueStatus
        """
        if not status:
            return IssueStatus.Open

        # Normalize the status string to handle case variations
        normalized_status = status.strip().lower() if isinstance(status, str) else ""

        # Map to our status values
        if normalized_status in ("fixed", "closed"):
            return IssueStatus.Closed

        # Default to Open for any unknown status
        return IssueStatus.Open
