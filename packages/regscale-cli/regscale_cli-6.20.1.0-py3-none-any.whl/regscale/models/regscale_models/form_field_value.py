#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Model for Custom Fields in the application"""

import logging
from typing import Any, List, Optional, Dict

from pydantic import ConfigDict, Field

from regscale.models.regscale_models.regscale_model import RegScaleModel

logger = logging.getLogger(__name__)


class FormFieldValue(RegScaleModel):
    _module_slug = "formFieldValue"
    formFieldName: Optional[str] = None
    formFieldId: Optional[int] = None
    data: Optional[str] = Field(default=None, alias="fieldValue")

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the CustomFieldData model.
            record id is the recordId like cases id or change id
            formId is the tab_id from the module calls
        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            post_save_form_fields="/api/{model_slug}/saveFormFields/{recordId}/{moduleName}",
            get_field_value="/api/{model_slug}/getFieldValues/{recordId}/{moduleName}/{formId}",
        )

    @staticmethod
    def filter_dict_keys(data: Dict[str, Any], allowed_fields: List[str]) -> Dict[str, Any]:
        """
        Return a new dictionary containing only the keys from allowed_fields.

        :param data: The original dictionary.
        :param allowed_fields: A list of keys to keep in the dictionary.
        :return: A new dictionary with only the allowed keys.
        """
        return {key: value for key, value in data.items() if key in allowed_fields}

    @classmethod
    def save_custom_data(cls, record_id: int, module_name: str, data: List[Any]) -> bool:
        """
        Save custom data for a record
        :param record_id: record id
        :param module_name: module name
        :param data: data to save
        :return: list of custom fields
        """
        fields = ["formFieldId", "data"]

        # Suppose data is a list of Pydantic model instances.
        # First, convert each instance to a dict.
        data_dicts = [d.dict() for d in data]

        # Now, filter each dictionary so that only the keys in `fields` remain.
        filtered_data = [cls.filter_dict_keys(item, fields) for item in data_dicts]

        result = cls._get_api_handler().post(
            endpoint=cls.get_endpoint("post_save_form_fields").format(
                model_slug=cls.get_module_slug(), recordId=record_id, moduleName=module_name
            ),
            data=filtered_data,
        )
        if result and result.ok:
            return True
        else:
            cls.log_response_error(response=result)
            return False

    @classmethod
    def get_field_values(cls, record_id: int, module_name: str, form_id: int) -> List["FormFieldValue"]:
        """
        Get custom data for a record
        :param record_id: record id
        :param module_name: module name
        :param form_id: form id
        :return: list of custom fields
        """
        result = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_field_value").format(
                model_slug=cls.get_module_slug(), recordId=record_id, moduleName=module_name, formId=form_id
            )
        )
        if result and result.ok:
            return [cls(**o) for o in result.json()]
        else:
            cls.log_response_error(response=result)
            return []
