# Copyright 2024 Splunk Inc. All rights reserved.

"""
### Universal Configuration Console standards
"""
import json
import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator

import yaml

from splunk_appinspect.check_messages import CheckMessage, FailMessage, NotApplicableMessage, WarningMessage
from splunk_appinspect.checks import Check, CheckConfig
from splunk_appinspect.constants import Tags

if TYPE_CHECKING:
    from splunk_appinspect.app import App

report_display_order = 50
logger = logging.getLogger(__name__)


class GlobalConfigReader(ABC):
    def __init__(self, path: Path):
        self.path = path

    @abstractmethod
    def read_file(self) -> dict:
        pass


class JsonGlobalConfigReader(GlobalConfigReader):
    def read_file(self) -> dict:
        with open(self.path, "r") as file:
            return json.load(file)


class YamlGlobalConfigReader(GlobalConfigReader):
    def read_file(self) -> dict:
        with open(self.path, "r") as file:
            return yaml.safe_load(file)


class CheckForUCCFrameworkVersion(Check):
    BUILD_PATH = Path("appserver", "static", "js", "build")

    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_for_ucc_framework_version",
                description="Check UCC framework version.",
                tags=(Tags.SPLUNK_APPINSPECT,),
            )
        )

    @Check.depends_on_files(
        basedir=[BUILD_PATH],
        names=["globalConfig.json", "globalConfig.yaml"],
        not_applicable_message="No UCC framework found.",
    )
    def check_for_ucc_framework_version(self, app: "App", path_in_app: str) -> Generator[CheckMessage, Any, None]:
        full_filepath = app.get_filename(path_in_app)
        reader = self._get_data_reader(full_filepath)
        try:
            data = reader.read_file()
        except Exception as e:
            yield FailMessage(f"Failed to process file: {e}. File: {path_in_app}", file_name=path_in_app)
            return

        ucc_version = yield from self._get_ucc_version(data)

        if not ucc_version:
            yield NotApplicableMessage("No version found in globalConfig file.")
            return

        yield WarningMessage(f"UCC framework usage detected. version = {ucc_version}.")

    @staticmethod
    def _get_ucc_version(data):
        metadata = data.get("meta")
        if not metadata:
            yield NotApplicableMessage("No metadata section found in globalConfig file.")
            return
        ucc_version = metadata.get("_uccVersion")
        return ucc_version

    @staticmethod
    def _get_data_reader(path_in_app: Path) -> GlobalConfigReader:
        if path_in_app.suffix == ".json":
            reader = JsonGlobalConfigReader(path_in_app)
        else:
            reader = YamlGlobalConfigReader(path_in_app)
        return reader
