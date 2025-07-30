# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Deprecated features from Splunk Enterprise 10.0.0

The following features should not be supported in Splunk 10.0.0 or later. For more, see [Deprecated features](https://docs.splunk.com/Documentation/Splunk/10.0.0/ReleaseNotes/Deprecatedfeatures) and [Changes for Splunk App developers](https://docs.splunk.com/Documentation/Splunk/10.0.0/Installation/ChangesforSplunkappdevelopers).
"""

import logging
from typing import TYPE_CHECKING, Any, Generator

import splunk_appinspect
from splunk_appinspect.check_messages import WarningMessage
from splunk_appinspect.checks import Check, CheckConfig
from splunk_appinspect.constants import Tags

if TYPE_CHECKING:
    from splunk_appinspect import App
    from splunk_appinspect.checks import CheckMessage
    from splunk_appinspect.custom_types import ConfigurationProxyType

logger = logging.getLogger(__name__)


class CheckOutdatedSSLTLS(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_for_outdated_ssl_tls",
                description="Connections using ssl3, tls1.0, tls1.1 are deprecated since Splunk 10.0 due to "
                "the OpenSSL dependency being updated to 3.0. Only valid TSL/SSL version is tls1.2.",
                depends_on_config=CheckOutdatedSSLTLS.CONFIGS_TO_CHECK,
                tags=(
                    Tags.SPLUNK_APPINSPECT,
                    Tags.CLOUD,
                    Tags.FUTURE,
                    Tags.PRIVATE_APP,
                    Tags.PRIVATE_CLASSIC,
                    Tags.PRIVATE_VICTORIA,
                    Tags.MIGRATION_VICTORIA,
                ),
            )
        )

    CONFIGS_TO_CHECK = [
        "alert_actions",
        "authentication",
        "indexes",
        "inputs",
        "outputs",
        "savedsearches",
        "server",
        "web",
    ]

    SSL_OPTION_NAMES = ["sslVersions", "sslVersionsForClient"]
    SSL_OPTION_PATTERNS = [".sslVersions", ".sslVersionsForClient"]

    def check_config(
        self,
        app: splunk_appinspect.App,
        config: "ConfigurationProxyType",
    ) -> Generator["CheckMessage", Any, None]:
        for config_name in self.CONFIGS_TO_CHECK:
            config_file = config[config_name]
            if not config_file:
                continue
            for section in config_file.sections():
                for option in section.options.values():
                    if option.name in self.SSL_OPTION_NAMES or any(
                        option.name.endswith(pattern) for pattern in self.SSL_OPTION_PATTERNS
                    ):
                        yield WarningMessage(
                            "The Splunk platform supports TLS 1.2 as default. Please ensure your app’s configuration "
                            "is indicating TLS 1.2 only - TLS 1.0, TLS 1.1 are deprecated and SSL 3, "
                            "TLS 1.3 are not supported.",
                            file_name=option.get_relative_path(),
                            line_number=option.get_line_number(),
                        )
