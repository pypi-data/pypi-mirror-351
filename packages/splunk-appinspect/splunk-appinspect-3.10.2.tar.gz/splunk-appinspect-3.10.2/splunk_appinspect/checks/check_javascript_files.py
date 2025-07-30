# Copyright 2019 Splunk Inc. All rights reserved.

"""
### JavaScript file standards
"""

import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING

import lxml.etree as et

import splunk_appinspect
from splunk_appinspect.constants import Tags
from splunk_appinspect.regex_matcher import (
    ConfEndpointMatcher,
    JSTelemetryEndpointMatcher,
    JSTelemetryMetricsMatcher,
    JSUDPCommunicationMatcher,
    JSWeakEncryptionMatcher,
)
from splunk_appinspect.telemetry_configuration_file import TelemetryConfigurationFile

if TYPE_CHECKING:
    from splunk_appinspect import App
    from splunk_appinspect.reporter import Reporter


logger = logging.getLogger(__name__)


@splunk_appinspect.tags(Tags.SPLUNK_APPINSPECT, Tags.CLOUD, Tags.MANUAL)
def check_for_weak_encryption_and_hashing_in_javascript(app: "App", reporter: "Reporter") -> None:
    """Check if any weak encryption in JavaScript"""
    matcher = JSWeakEncryptionMatcher()
    for result, file_path, lineno in matcher.match_results_iterator(app.app_dir, app.iterate_files(types=[".js"])):
        reporter_output = (
            "The following line will be inspected during code review."
            f" Match: {result}"
            f" File: {file_path}"
            f" Line: {lineno}"
        )
        reporter.manual_check(reporter_output, file_path, lineno)

    if not matcher.has_valid_files:
        reporter_output = "No JavaScript files found."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags(Tags.SPLUNK_APPINSPECT, Tags.CLOUD, Tags.MANUAL)
def check_for_udp_communication_in_javascript(app: "App", reporter: "Reporter") -> None:
    """Check if the app contains udp communication in JavaScript files."""
    matcher = JSUDPCommunicationMatcher()
    for result, file_path, lineno in matcher.match_results_iterator(app.app_dir, app.iterate_files(types=[".js"])):
        reporter_output = (
            "The following line will be inspected during code review."
            f" Match: {result}"
            f" File: {file_path}"
            f" Line: {lineno}"
        )
        reporter.manual_check(reporter_output, file_path, lineno)

    if not matcher.has_valid_files:
        reporter_output = "No JavaScript files found."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags(Tags.SPLUNK_APPINSPECT, Tags.CLOUD, Tags.MANUAL)
def check_for_stored_xss_in_javascript(app: "App", reporter: "Reporter") -> None:
    """Check if possible stored xss in JavaScript"""

    # setup.xml -> read conf -> src(covered in reflected xss)
    # FIXME: check stored xss dynamically
    if app.file_exists("default", "setup.xml"):
        setup_full_filepath = app.get_filename("default", "setup.xml")

        try:
            root = et.parse(str(setup_full_filepath))
        except et.ParseError:
            root = et.parse(str(setup_full_filepath), parser=et.XMLParser(recover=True))
        except Exception as error:
            logger.error("unexpected code error: %s", str(error))
            raise

        conf_endpoints = [b.attrib["endpoint"].split("/")[-1] for b in root.iter("block") if "endpoint" in b.attrib]
        if conf_endpoints:
            matcher = ConfEndpointMatcher()
            for result, file_path, lineno in matcher.match_results_iterator(
                app.app_dir,
                app.iterate_files(types=[".js", ".html"]),
                regex_option=re.IGNORECASE,
            ):
                if [endpoint for endpoint in conf_endpoints if endpoint in result]:
                    reporter_output = (
                        "Please manually check the configurations in setup.xml. "
                        "Stored configurations that accept user input might be processed in JavaScript code,"
                        " which poses a potential stored XSS threat."
                        f" Match: {result}"
                        f" File: {file_path}"
                        f" Line: {lineno}"
                    )
                    reporter.manual_check(reporter_output, file_path, lineno)
    else:
        reporter_output = "`default/setup.xml` does not exist. The stored xss check is not applicable"
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
def check_telemetry_endpoint_usage_in_javascript(app: "App", reporter: "Reporter") -> None:
    """Check that app does not use REST endpoint to collect and send telemetry data."""

    telemetry_config = TelemetryConfigurationFile()
    if not telemetry_config.check_allow_list(app):
        matcher = JSTelemetryEndpointMatcher()

        # also covered the python file search in this check
        # for simplicity, does not separate this part to check_python_files.py
        for result, file_path, lineno in matcher.match_results_iterator(
            app.app_dir, app.iterate_files(types=[".js", ".py"])
        ):
            reporter.fail(
                "The telemetry-metric REST endpoint usage is prohibited in order to protect from "
                "sending sensitive information. Consider using logging. "
                "See: https://dev.splunk.com/enterprise/docs/developapps/addsupport/logging/loggingsplunkextensions/."
                f" Match: {result}",
                file_path,
                lineno,
            )

        if not matcher.has_valid_files:
            reporter_output = "No JavaScript files found."
            reporter.not_applicable(reporter_output)

    else:
        # This app is authorized for telemetry check. Pass it.
        pass


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
def check_for_telemetry_metrics_in_javascript(app: "App", reporter: "Reporter") -> None:
    """Check for usages of telemetry metrics in JavaScript"""

    telemetry_config = TelemetryConfigurationFile()
    if not telemetry_config.check_allow_list(app):
        matcher = JSTelemetryMetricsMatcher()
        for result, file_path, lineno in matcher.match_results_iterator(app.app_dir, app.iterate_files(types=[".js"])):
            reporter_output = (
                "The telemetry operations are not permitted in order to protect from sending sensitive information. "
                "Consider using logging. "
                "See: https://dev.splunk.com/enterprise/docs/developapps/addsupport/logging/loggingsplunkextensions/."
                f" Match: {result}"
            )
            reporter.fail(reporter_output, file_path, lineno)

        if not matcher.has_valid_files:
            reporter_output = "No JavaScript files found."
            reporter.not_applicable(reporter_output)

    else:
        # This app is authorized for telemetry check. Pass it.
        pass
