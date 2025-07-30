#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Functions used to interact with RegScale API"""

# standard imports
import json
import os
import re
import warnings
from typing import Any, Optional
from urllib.parse import urljoin

from requests import JSONDecodeError

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import convert_to_string, error_and_exit, get_file_name, get_file_type
from regscale.models import Data
from regscale.models.regscale_models.modules import Modules

logger = create_logger()


def send_email(_: Api, __: str, payload: dict) -> bool:
    """
    Function to use the RegScale email API and send an email, returns bool on whether API call was successful

    :param Api _: API object
    :param str __: RegScale URL of instance
    :param dict payload: email payload
    :return: Boolean if RegScale api was successful
    :rtype: bool
    """
    warnings.warn(
        "This function is deprecated and will be removed in a future release. Use Email().send instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    from regscale.models import Email

    email = Email(**payload)
    # use the api to post the dict payload passed
    return email.send() is not None


def update_regscale_config(str_param: str, val: Any, app: Application = None) -> str:
    """
    Update config in init.yaml

    :param str str_param: config parameter to update
    :param Any val: config parameter value to update
    :param Application app: Application object, defaults to None
    :return: Verification message
    :rtype: str
    """
    if not app:
        app = Application()
    config = app.config
    # update config param
    # existing params will be overwritten, new params will be added
    config[str_param] = val
    # write the changes back to file
    app.save_config(config)
    logger.debug(f"Parameter '{str_param}' set to '{val}'.")
    return "Config updated"


def create_regscale_assessment(_: str, new_assessment: dict, __: Api) -> Optional[int]:
    """
    Function to create a new assessment in RegScale and returns the new assessment's ID

    :param str _: RegScale instance URL to create the assessment
    :param dict new_assessment: API assessment payload
    :param Api __: API object
    :return: New RegScale assessment ID
    :rtype: int
    """
    warnings.warn(
        "This function is deprecated and will be removed in a future release. Use Assessment().create.id instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    from regscale.models import Assessment

    new_assessment = Assessment(**new_assessment)
    if created_assessment := new_assessment.create():
        return created_assessment.id
    return None


def check_module_id(parent_id: int, parent_module: str) -> bool:
    """
    Verify object exists in RegScale

    :param int parent_id: RegScale parent ID
    :param str parent_module: RegScale module
    :return: True or False if the object exists in RegScale
    :rtype: bool
    """
    api = Api()
    modules = Modules()
    key = (list(modules.dict().keys())[list(modules.dict().values()).index(parent_module)]) + "s"

    body = """
    query {
        NAMEOFTABLE(take: 50, skip: 0) {
          items {
            id
          },
          pageInfo {
            hasNextPage
          }
          ,totalCount
        }
    }""".replace(
        "NAMEOFTABLE", key
    )

    items = api.graph(query=body)

    if parent_id in set(obj["id"] for obj in items[key]["items"]):
        return True
    return False


def verify_provided_module(module: str) -> None:
    """
    Function to check the provided module is a valid RegScale module and will display the acceptable RegScale modules

    :param str module: desired module
    :rtype: None
    """
    if module not in Modules().api_names():
        Modules().to_table()
        error_and_exit("Please provide an option from the Accepted Value column.")


def get_all_from_module(api: Api, module: str, timeout: int = 300) -> list[dict]:
    """
    Function to retrieve all records for the provided Module in RegScale via GraphQl

    :param Api api: API object
    :param str module: RegScale Module, accepts issues, assessments, and risks
    :param int timeout: Timeout for the API call, defaults to 300 seconds
    :return: list of objects from RegScale API of the provided module
    :rtype: list[dict]
    """
    original_timeout = api.timeout
    # adjust timeout to the provided timeout if it is greater than the default
    api.timeout = max(timeout, original_timeout)

    regscale_data = []
    if module == "assessments":
        from regscale.models.regscale_models.assessment import Assessment

        all_assessments = Assessment().fetch_all_assessments(api.app)
        regscale_data = [assessment.dict() for assessment in all_assessments]
    elif module == "issues":
        from regscale.models.regscale_models.issue import Issue

        all_issues = Issue().fetch_all_issues(api.app)
        regscale_data = [issue.dict() for issue in all_issues]
    elif module == "risks":
        from regscale.models.regscale_models.risk import Risk

        all_risks = Risk().fetch_all_risks()
        regscale_data = [risk.dict() for risk in all_risks]
    else:
        logger.warning(
            "%s is not a valid module.\nPlease provide a valid module: issues, assessments, or risks.",
            module,
        )
    return regscale_data


def format_control(control: str) -> str:
    """Convert a verbose control id to a regscale friendly control id,
        e.g. AC-2 (1) becomes ac-2.1
             AC-2(1) becomes ac-2.1

    :param str control: Verbose Control
    :return: RegScale friendly control
    :rtype: str
    """
    # Define a regular expression pattern to match the parts of the string
    pattern = r"^([A-Z]{2})-(\d+)\s?\((\d+)\)$"

    # Use re.sub() to replace the matched parts of the string with the desired format
    new_string = re.sub(pattern, r"\1-\2.\3", control)

    return new_string.lower()  # Output: ac-2.1


def get_user(_: Api, user_id: str) -> dict:
    """
    Function to get the provided user_id from RegScale via API

    :param Api _: API Object
    :param str user_id: the RegScale user's GUID
    :return: Dictionary containing the user's information
    :rtype: dict
    """
    warnings.warn(
        "This function is deprecated and will be removed in a future release. Use User.get_user_by_id() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    from regscale.models import User

    user = User.get_user_by_id(user_id)
    return user.dict()


def get_threats(_: Api) -> list[dict]:
    """
    Function to get all threats from RegScale via GraphQL

    :param Api _: API Object
    :return: List containing threat descriptions
    :rtype: list[dict]
    """
    warnings.warn(
        "This function is deprecated and will be removed in a future release. Use Threat.fetch_all_threats() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    from regscale.models import Threat

    threats = Threat.fetch_all_threats()
    return [threat.dict() for threat in threats] or []


def create_new_data_submodule(
    parent_id: int, parent_module: str, file_path: str, raw_data: dict = None, is_file: bool = True
) -> Optional[dict]:
    """
    Function to create a new data record in the data submodule in RegScale

    :param int parent_id: RegScale parent ID to associate the data record
    :param str parent_module: RegScale parent module to associate the data record
    :param str file_path: Path to the file to read and upload
    :param dict raw_data: Raw data to upload, defaults to None
    :param bool is_file: Boolean to indicate if the file is a file or a directory, defaults to True
    :return: dictionary of the posted data or None if the API call was unsuccessful
    :rtype: Optional[dict]
    """
    if is_file:
        # check if the file exists
        if not os.path.isfile(file_path):
            error_and_exit(f"Unable to upload file because the file does not exist: {file_path}")

        with open(file_path, "r", encoding="utf-8") as in_file:
            raw_data = in_file.read()
        data_source = get_file_name(file_path)
        data_type = get_file_type(file_path)[1:].upper()
    else:
        data_source = raw_data["source"] if "source" in raw_data else ""
        data_type = raw_data["type"] if "type" in raw_data else "JSON"

    new_data = Data(
        dataSource=data_source,
        dataType=data_type,
        rawData=raw_data,
        parentId=parent_id,
        parentModule=parent_module,
    )
    if isinstance(raw_data, dict):
        # Create a string
        new_data.rawData = json.dumps(raw_data)
    # post the data to RegScale
    if new_data.create():
        return new_data.dict()
    return None


def create_properties(
    _: Api,
    data: dict,
    parent_id: int,
    parent_module: str,
    __: Optional[int] = 3,
    label: Optional[str] = None,
) -> bool:
    """
    Create a list of properties and upload them to RegScale for the provided asset

    :param Api _: API Object to post the data in RegScale
    :param dict data: Dictionary of data to parse and create properties from
    :param int parent_id: ID to create properties for
    :param str parent_module: Parent module to create properties for
    :param Optional[int] __: Number of times to retry the API call if it fails, defaults to 3
    :param Optional[str] label: Label to use for the properties, defaults to None
    :return: If batch update was successful
    :rtype: bool
    """
    from regscale.models import Property

    warnings.warn(
        "This function is deprecated and will be removed in a future release. Use Property.batch_create() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    properties: list = []
    for key, value in data.items():
        # evaluate the value and convert it to a string
        value = convert_to_string(value)
        prop = Property(
            key=key,
            value=value or "NULL",
            label=label or None,
            parentId=parent_id,
            parentModule=parent_module,
        )
        properties.append(prop)

    new_props = Property.batch_create(properties)
    return len(new_props) > 0
