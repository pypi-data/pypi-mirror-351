from datetime import date, datetime
from enum import Enum
import os
import sys
import requests
from typing import Dict, Any, Literal, Optional
from fastmcp.exceptions import ToolError
from ac_mcp_server.types import (
    ContactCreateParams,
    ContactList,
    ContactTagResponse,
    SingleContactRecord,
    SingleTagRecord,
    TagCreateParams,
    ContactTagParams,
    Tag,
    TagCreateResponse,
    TagList,
    ContactCustomFieldCreateParams,
    ContactCustomFieldCreateResponse,
    ContactCustomFieldList,
    SingleContactCustomFieldRecord,
    FieldOptionBulkCreateParams,
    ContactFieldRelCreateParams,
    ContactStatus,
    ContactListParams,
    TagListParams,
    ContactCustomFieldListParams,
    ContactFieldValueCreateParams,
    ContactFieldValueUpdateParams,
    ContactFieldValueResponse,
    ContactFieldValueList,
    ContactFieldValueListParams,
    EmailActivityListParams,
    EmailActivityList,
    CampaignListParams,
    CampaignList,
    SingleCampaignRecord,
    CampaignLinkList,
    AutomationListParams,
    AutomationList,
    ContactAutomationListParams,
    ContactAutomationList,
    SingleContactAutomationRecord,
    ContactAutomationCreateParams,
    ContactAutomationCreateResponse,
    GroupListParams,
    GroupList,
    ListListParams,
    ListList,
    SingleListRecord,
    ListCreateParams,
    ListCreateResponse,
    ListGroupPermissionParams,
    ListGroupPermissionResponse,
    ContactListUpdateParams,
    ContactListResponse,
    ListUpdateParams,
    ListUpdateResponse,
)
from ac_mcp_server.utils import get_package_info
from pydantic import BaseModel


def _get_headers(api_token: str) -> Dict[str, str]:
    PACKAGE_NAME, PACKAGE_VERSION = get_package_info()
    return {
        "Api-Token": api_token,
        "User-Agent": f"{PACKAGE_NAME}-{PACKAGE_VERSION}",
    }


def _generate_query_param_value(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    return value


def _generate_query_params(params: BaseModel) -> Dict[str, Any]:
    query_params = {}
    param_dict = params.model_dump(exclude_none=True, by_alias=True)
    for key, value in param_dict.items():
        if isinstance(value, dict):
            for dict_key, dict_value in value.items():
                if isinstance(dict_value, dict):
                    for nested_key, nested_value in dict_value.items():
                        query_params[f"{key}[{dict_key}][{nested_key}]"] = (
                            _generate_query_param_value(nested_value)
                        )
                else:
                    query_params[f"{key}[{dict_key}]"] = _generate_query_param_value(
                        dict_value
                    )
        else:
            query_params[key] = _generate_query_param_value(value)
    return query_params


def call_ac_api(
    endpoint: str,
    method: Literal["GET", "POST", "PUT", "DELETE"] = "GET",
    data: Dict[str, Any] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    base_url = os.environ.get("AC_API_URL")
    api_token = os.environ.get("AC_API_TOKEN")

    url = f"{base_url}{endpoint}"
    headers = _get_headers(api_token)

    if not base_url:
        raise ToolError(
            "AC_API_URL environment variable is not set. Please configure the ActiveCampaign API URL."
        )

    if not api_token:
        raise ToolError(
            "AC_API_TOKEN environment variable is not set. Please configure your ActiveCampaign API token."
        )

    try:
        if data:
            response = requests.request(
                method, url, headers=headers, json=data, params=params
            )
        else:
            response = requests.request(method, url, headers=headers, params=params)

        response.raise_for_status()

        return response.json()
    except requests.exceptions.ConnectionError:
        raise ToolError(
            f"Failed to connect to ActiveCampaign API at {url}. Please check your network connection and API URL."
        )
    except requests.exceptions.Timeout:
        raise ToolError(
            f"Request to ActiveCampaign API timed out. The server might be experiencing high load."
        )
    except requests.exceptions.HTTPError as err:
        status_code = err.response.status_code
        try:
            error_message = str(err.response.json())
        except ValueError:
            error_message = str(err)

        if status_code == 401:
            raise ToolError(
                "Authentication failed. Please check your ActiveCampaign API token."
            )
        elif status_code == 403:
            raise ToolError(
                "Access forbidden. Your API token doesn't have permission to perform this action."
            )
        elif status_code == 404:
            raise ToolError(
                f"Resource not found at {endpoint}. Please check the endpoint path."
            )
        elif status_code == 429:
            raise ToolError("Rate limit exceeded. Please try again later.")
        elif 400 <= status_code < 500:
            raise ToolError(f"Client error: {error_message}")
        elif 500 <= status_code < 600:
            raise ToolError(
                f"Server error: {error_message}. The ActiveCampaign server might be experiencing issues."
            )
        else:
            raise ToolError(f"HTTP error: {error_message}")
    except ValueError:
        raise ToolError(
            f"Invalid JSON response from ActiveCampaign API. The response couldn't be parsed. Raw response: {response.text}"
        )
    except Exception as e:
        raise ToolError(f"Unexpected error when calling ActiveCampaign API: {str(e)}")


def list_contacts(filters: ContactListParams) -> ContactList:
    query_params = _generate_query_params(filters)
    return call_ac_api("/api/3/contacts", params=query_params)


def get_contact(contact_id: int) -> SingleContactRecord:
    return call_ac_api(f"/api/3/contacts/{contact_id}")


def create_or_update_contact(params: ContactCreateParams) -> SingleContactRecord:
    data = {"contact": params.model_dump(exclude_none=True)}
    return call_ac_api("/api/3/contact/sync", method="POST", data=data)


def list_tags(params: TagListParams) -> TagList:
    query_params = _generate_query_params(params)
    return call_ac_api("/api/3/tags", params=query_params)


def get_tag(tag_id: int) -> SingleTagRecord:
    return call_ac_api(f"/api/3/tags/{tag_id}")


def create_contact_tag(params: TagCreateParams) -> TagCreateResponse:
    data = {"tag": params.model_dump(exclude_none=True)}
    return call_ac_api("/api/3/tags", method="POST", data=data)


def add_tag_to_contact(params: ContactTagParams) -> ContactTagResponse:
    data = {"contactTag": {"contact": str(params.contact), "tag": str(params.tag)}}
    return call_ac_api("/api/3/contactTags", method="POST", data=data)


def list_contact_custom_fields(
    params: ContactCustomFieldListParams,
) -> ContactCustomFieldList:
    query_params = _generate_query_params(params)
    return call_ac_api("/api/3/fields", params=query_params)


def get_contact_custom_field(field_id: int) -> SingleContactCustomFieldRecord:
    return call_ac_api(f"/api/3/fields/{field_id}")


def create_contact_custom_field(
    params: ContactCustomFieldCreateParams,
) -> ContactCustomFieldCreateResponse:
    data = {"field": params.model_dump(exclude_none=True)}
    return call_ac_api("/api/3/fields", method="POST", data=data)


def create_field_options(params: FieldOptionBulkCreateParams) -> Dict[str, Any]:
    data = params.model_dump(exclude_none=True)
    return call_ac_api("/api/3/fieldOption/bulk", method="POST", data=data)


def create_contact_field_relationship(
    params: ContactFieldRelCreateParams,
) -> Dict[str, Any]:
    data = {"fieldRel": params.model_dump(exclude_none=True)}
    return call_ac_api("/api/3/fieldRels", method="POST", data=data)


def list_contact_field_values(
    params: ContactFieldValueListParams,
) -> ContactFieldValueList:
    query_params = _generate_query_params(params)
    return call_ac_api("/api/3/fieldValues", params=query_params)


def get_contact_field_value(field_value_id: int) -> ContactFieldValueResponse:
    return call_ac_api(f"/api/3/fieldValues/{field_value_id}")


def create_contact_field_value(
    params: ContactFieldValueCreateParams,
) -> ContactFieldValueResponse:
    use_defaults = params.useDefaults
    params.useDefaults = None
    data = {"fieldValue": params.model_dump(exclude_none=True)}

    if use_defaults is not None:
        data["useDefaults"] = use_defaults

    return call_ac_api("/api/3/fieldValues", method="POST", data=data)


def update_contact_field_value(
    field_value_id: int, params: ContactFieldValueUpdateParams
) -> ContactFieldValueResponse:
    data = {"fieldValue": {"value": params.value}}

    if params.useDefaults is not None:
        data["useDefaults"] = params.useDefaults

    return call_ac_api(f"/api/3/fieldValues/{field_value_id}", method="PUT", data=data)


def list_email_activities(params: EmailActivityListParams) -> EmailActivityList:
    """
    List email activities from ActiveCampaign.
    Note: For best results, only single records should be requested rather than running unfiltered.
    """
    query_params = _generate_query_params(params)
    return call_ac_api("/api/3/emailActivities", params=query_params)


def list_campaigns(params: CampaignListParams) -> CampaignList:
    """
    List all campaigns from ActiveCampaign.
    """
    query_params = _generate_query_params(params)
    return call_ac_api("/api/3/campaigns", params=query_params)


def get_campaign(campaign_id: int) -> SingleCampaignRecord:
    return call_ac_api(f"/api/3/campaigns/{campaign_id}")


def get_campaign_links(campaign_id: int) -> CampaignLinkList:
    return call_ac_api(f"/api/3/campaigns/{campaign_id}/links")


def list_automations(params: AutomationListParams) -> AutomationList:
    """
    List all automations from ActiveCampaign.
    """
    query_params = _generate_query_params(params)
    return call_ac_api("/api/3/automations", params=query_params)


def list_contact_automations(
    params: ContactAutomationListParams,
) -> ContactAutomationList:
    """
    List all automations a contact is in.
    """
    query_params = _generate_query_params(params)
    return call_ac_api("/api/3/contactAutomations", params=query_params)


def get_contact_automation(contact_automation_id: int) -> SingleContactAutomationRecord:
    """
    Retrieve a specific contact automation record by ID.
    """
    return call_ac_api(f"/api/3/contactAutomations/{contact_automation_id}")


def add_contact_to_automation(
    params: ContactAutomationCreateParams,
) -> ContactAutomationCreateResponse:
    """
    Add a contact to an automation.
    """
    data = {"contactAutomation": params.model_dump(exclude_none=True)}
    return call_ac_api("/api/3/contactAutomations", method="POST", data=data)


def remove_contact_from_automation(contact_automation_id: int) -> Dict[str, Any]:
    """
    Remove a contact from an automation.
    """
    return call_ac_api(
        f"/api/3/contactAutomations/{contact_automation_id}", method="DELETE"
    )


def list_groups(params: GroupListParams) -> GroupList:
    """
    List all user groups from ActiveCampaign.
    Required for determining available groups when creating lists.
    """
    query_params = _generate_query_params(params)
    return call_ac_api("/api/3/groups", params=query_params)


def list_lists(params: ListListParams) -> ListList:
    """
    List all lists from ActiveCampaign with filtering and pagination options.
    """
    query_params = _generate_query_params(params)
    return call_ac_api("/api/3/lists", params=query_params)


def get_list(list_id: int) -> SingleListRecord:
    """
    Retrieve a single list by ID from ActiveCampaign.
    """
    return call_ac_api(f"/api/3/lists/{list_id}")


def create_list(params: ListCreateParams) -> ListCreateResponse:
    data = {"list": params.model_dump(exclude_none=True)}
    return call_ac_api("/api/3/lists", method="POST", data=data)


def update_list(list_id: int, params: ListUpdateParams) -> ListUpdateResponse:
    data = {"list": params.model_dump(exclude_none=True)}
    return call_ac_api(f"/api/3/lists/{list_id}", method="PUT", data=data)


def create_list_group_permission(
    params: ListGroupPermissionParams,
) -> ListGroupPermissionResponse:
    data = {"listGroup": {"listid": params.list, "groupid": params.group}}
    return call_ac_api("/api/3/listGroups", method="POST", data=data)


def add_contact_to_list(params: ContactListUpdateParams) -> ContactListResponse:
    data = {"contactList": params.model_dump(exclude_none=True)}
    return call_ac_api("/api/3/contactLists", method="POST", data=data)
