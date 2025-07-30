from datetime import datetime, date
import os
import sys
from typing import Dict, Literal, Optional, Union, Any
from fastmcp import FastMCP
from ac_mcp_server.ac_client import (
    list_contacts,
    get_contact,
    create_or_update_contact,
    list_tags,
    get_tag,
    create_contact_tag,
    add_tag_to_contact,
    list_contact_custom_fields,
    get_contact_custom_field,
    create_contact_custom_field,
    create_field_options,
    create_contact_field_relationship,
    list_contact_field_values,
    get_contact_field_value,
    create_contact_field_value,
    update_contact_field_value,
    list_email_activities,
    list_campaigns,
    get_campaign,
    get_campaign_links,
    list_automations,
    list_contact_automations,
    get_contact_automation,
    add_contact_to_automation,
    remove_contact_from_automation,
    list_groups,
    list_lists,
    get_list,
    create_list,
    create_list_group_permission,
    add_contact_to_list,
)
import ac_mcp_server.ac_client as ac_client
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
    ContactFilterField,
    ContactSortField,
    ContactListParams,
    TagSearchOperator,
    TagOrderMethod,
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
    ContactAutomationFilters,
    ContactAutomationDateFilter,
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
)

mcp = FastMCP(
    name="ActiveCampaign",
    instructions="""
This server provides access to their data in ActiveCampaign, a marketing automation and CRM platform.
Customers may refer to ActiveCampagaign as AC. Provide guidance to the user but do not imply that you can take actions that you have not been given tools to do.
""",
    log_level="ERROR",
)

"""
Claude Desktop doesn't support resources, so everything has to be a tool.
"""


@mcp.tool()
def list_contacts(params: ContactListParams) -> ContactList:
    """
    Get contacts with filtering and pagination options

    Parameters:
    - params: ContactListParams object containing:
      - segmentid: Filter by segment ID
      - formid: Filter by form ID
      - listid: Filter by list ID
      - tagid: Filter by tag ID
      - limit: Number of results to return (default 20)
      - offset: Offset for pagination
      - search: Partial string to match in email, first_name, last_name, or account name
      - orders: Dictionary for ordering results by specific fields. Valid fields are:
        "id", "cdate" (created date), "email", "first_name", "last_name", "name" (full name), "score"
        Example: {"email": "ASC"} to sort by email ascending
      - filters: Dictionary for time-based filtering. Valid filters are:
        "created_before", "created_after", "updated_before", "updated_after"
        Values can be strings in ISO format or datetime/date objects
        Example: {"created_after": "2023-01-01", "updated_before": "2023-12-31"}
      - id_greater: Return contacts with ID greater than this (recommended for pagination)
      - seriesid: Filter by series ID
      - waitid: Filter by wait ID
      - status: Contact status (ANY=-1, UNCONFIRMED=0, ACTIVE=1, UNSUBSCRIBED=2, BOUNCED=3)
    """
    return ac_client.list_contacts(params)


@mcp.tool()
def get_contact(contact_id: int) -> SingleContactRecord:
    """Get a contact by ID"""
    return ac_client.get_contact(contact_id)


@mcp.tool()
def create_or_update_contact(params: ContactCreateParams) -> SingleContactRecord:
    """
    Create or update a contact, using the email as the unique identifier
    fieldValues fieldIds can be found or created by using the list_contact_custom_fields and create_contact_custom_field tools.
    Always try to find a similar field name or perstag to the one you want to create, even if it isn't exactly the same. Stop and prompt
    the user if you can't find it to ask if they want to create a new field.
    """
    return ac_client.create_or_update_contact(params)


@mcp.tool()
def list_tags(params: TagListParams) -> TagList:
    """
    List, search, and filter tags

    Parameters:
    - params: TagListParams object containing:
      - search_filters: Dictionary of operators and values to filter tags by name
        Valid operators: "eq", "neq", "lt", "lte", "gt", "gte", "contains", "starts_with"
        Example: {"contains": "lead"} to find tags containing "lead"
      - order_method: How to order results - "weight", "asc", or "desc"
        - weight: Exact matches first, then matches starting with search term, then others
        - asc/desc: Ascending or descending alphabetical order
      - limit: Number of results to return (default 100)
      - offset: Offset for pagination
    """
    return ac_client.list_tags(params)


@mcp.tool()
def get_tag(tag_id: int) -> SingleTagRecord:
    """
    Get a tag by ID

    Parameters:
    - tag_id: The ID of the tag to retrieve
    """
    return ac_client.get_tag(tag_id)


@mcp.tool()
def create_contact_tag(params: TagCreateParams) -> TagCreateResponse:
    """
    Create a new contact tag

    Parameters:
    - params: TagCreateParams object containing:
      - tag: The name of the tag
      - description: Optional description of the tag (default empty string)
    """
    return ac_client.create_contact_tag(params)


@mcp.tool()
def add_tag_to_contact(params: ContactTagParams) -> ContactTagResponse:
    """
    Add a tag to a contact

    Parameters:
    - params: ContactTagParams object containing:
      - contact: The ID of the contact
      - tag: The ID of the tag to add to the contact
    """
    return ac_client.add_tag_to_contact(params)


@mcp.tool()
def list_contact_custom_fields(
    params: ContactCustomFieldListParams,
) -> ContactCustomFieldList:
    """
    List all contact custom fields with pagination options

    Parameters:
    - params: ContactCustomFieldListParams object containing:
      - limit: Number of results to return
      - offset: Offset for pagination
    """
    return ac_client.list_contact_custom_fields(params)


@mcp.tool()
def get_contact_custom_field(field_id: int) -> SingleContactCustomFieldRecord:
    """
    Get a contact custom field by ID

    Parameters:
    - field_id: The ID of the custom field to retrieve
    """
    return ac_client.get_contact_custom_field(field_id)


@mcp.tool()
def create_contact_custom_field(
    params: ContactCustomFieldCreateParams,
) -> ContactCustomFieldCreateResponse:
    """
    Create a contact custom field. Always create field options after creating fields of type "dropdown", "listbox", "radio", or "checkbox".

    Parameters:
    - params: ContactCustomFieldCreateParams object containing:
      - title: The name of the custom field
      - descript: Optional description of the field
      - type: The type of field (e.g., "text", "textarea", "date", "listbox", "radio", "checkbox", "hidden", "datetime")
      - perstag: Optional personalization tag name
      - defval: Optional default value
      - visible: Whether this field is visible in forms
      - ordernum: The order of this field relative to others
    """
    return ac_client.create_contact_custom_field(params)


@mcp.tool()
def create_field_options(params: FieldOptionBulkCreateParams) -> Dict[str, Any]:
    """
    Create options for a dropdown, listbox, radio, or checkbox contact custom field

    Parameters:
    - params: FieldOptionBulkCreateParams object containing a list of:
      - orderid: The order in which to display the option
      - value: The value of the option
      - label: The label to display for the option
      - isdefault: Whether this option is selected by default
      - field: The ID of the custom field these options belong to
    """
    return ac_client.create_field_options(params)


@mcp.tool()
def create_contact_field_relationship(
    params: ContactFieldRelCreateParams,
) -> Dict[str, Any]:
    """
    Associate a contact custom field with a contact list

    Parameters:
    - params: ContactFieldRelCreateParams object containing:
      - relid: The ID of the contact list
      - field: The ID of the custom field
    """
    return ac_client.create_contact_field_relationship(params)


@mcp.tool()
def list_contact_field_values(
    params: ContactFieldValueListParams,
) -> ContactFieldValueList:
    """
    List all contact custom field values

    Parameters:
    - params: ContactFieldValueListParams object containing:
      - filters: Optional dictionary to filter by fieldid conditions (e.g., {"fieldid": 123})
      - limit: Number of results to return
      - offset: Offset for pagination
    """
    return ac_client.list_contact_field_values(params)


@mcp.tool()
def get_contact_field_value(field_value_id: int) -> ContactFieldValueResponse:
    """
    Get a contact custom field value by ID

    Parameters:
    - field_value_id: The ID of the field value to retrieve
    """
    return ac_client.get_contact_field_value(field_value_id)


@mcp.tool()
def create_contact_field_value(
    params: ContactFieldValueCreateParams,
) -> ContactFieldValueResponse:
    """
    Create a contact custom field value. Contact field values can also be set in bulk in the payload to create or update a contact.

    Parameters:
    - params: ContactFieldValueCreateParams object containing:
      - contact: The ID of the contact
      - field: The ID of the custom field
      - value: The value to store in the field. Format depends on field type:
        - text/textarea/hidden: Simple string value
        - dropdown/radio: Exact option value
        - date: "YYYY-MM-DD" format
        - datetime: ISO format "YYYY-MM-DDThh:mm:ssZ"
        - checkbox (multiple): "||Option 1||Option 3||" format
        - checkbox (single): "||Option 2||" format
      - useDefaults: Optional boolean to set default values for required fields on the contact record
    """
    return ac_client.create_contact_field_value(params)


@mcp.tool()
def update_contact_field_value(
    field_value_id: int, params: ContactFieldValueUpdateParams
) -> ContactFieldValueResponse:
    """
    Update a contact custom field value

    Parameters:
    - field_value_id: The ID of the field value to update
    - params: ContactFieldValueUpdateParams object containing:
      - value: The new value for the field. Format depends on field type:
        - text/textarea/hidden: Simple string value
        - dropdown/radio: Exact option value
        - date: "YYYY-MM-DD" format
        - datetime: ISO format "YYYY-MM-DDThh:mm:ssZ"
        - checkbox (multiple): "||Option 1||Option 3||" format
        - checkbox (single): "||Option 2||" format
      - useDefaults: Optional boolean to set default values for required fields on the contact record
    """
    return ac_client.update_contact_field_value(field_value_id, params)


@mcp.tool()
def list_email_activities(params: EmailActivityListParams) -> EmailActivityList:
    """
    List email activities from ActiveCampaign.

    For best results, only single records should be requested rather than running the call unfiltered.

    Parameters:
    - params: EmailActivityListParams object containing:
      - limit: Optional number of results to return
      - offset: Optional offset for pagination
      - orders: Optional dictionary for ordering results by specific fields. Valid fields are:
        "subscriberid", "fieldid", "tstamp", "id" - subscriberid is a contact id
        Example: {"tstamp": "DESC"} to sort by timestamp descending
      - filters: Optional dictionary for filtering by specific fields. Valid filters are:
        "subscriberid", "fieldid"
        Example: {"subscriberid": "1641"} to filter by subscriber ID
    """
    return ac_client.list_email_activities(params)


@mcp.tool()
def list_campaigns(params: CampaignListParams) -> CampaignList:
    """
    List all campaigns from ActiveCampaign with comprehensive filtering options.

    Parameters:
    - params: CampaignListParams object containing:
      - limit: Optional number of results to return
      - offset: Optional offset for pagination
      - orders: Optional dictionary for ordering results by specific fields. Valid fields are:
        "sdate" (scheduled send date), "mdate" (modifed date), "ldate" (last sent date), "status"
        Example: {"sdate": "DESC"} to sort by scheduled send date descending
      - filters: Optional CampaignFilterField object containing:
        - type: Campaign type ("single", "recurring", "split", "responder", "reminder", "special", "activerss", "text")
        - list_id: Filter by specific list ID
        - automation: Filter by automation flag
        - willrecur: Filter by recurring campaign flag
        - seriesid: Filter by series ID
        - label_name: Filter by label name
        - name: Filter by campaign name (partial match)
        - id: Filter by campaign ID
        - status: Filter by comma-separated list of status integers (e.g., "1,2,3")
      - Boolean filters:
        - has_message: Filter for campaigns with messages
        - has_message_content: Filter for campaigns with message content
        - has_form: Filter for campaigns with forms
      - Other filters:
        - campaignListing: Filter by campaign listing ID
        - status: Filter by campaign status name ("drafts", "scheduled", "currently-sending", etc.)
        - excludeTypes: Comma-separated list of campaign types to exclude
    """
    return ac_client.list_campaigns(params)


@mcp.tool()
def get_campaign(campaign_id: int) -> SingleCampaignRecord:
    """
    Get a campaign by ID from ActiveCampaign.

    Parameters:
    - campaign_id: The ID of the campaign to retrieve
    """
    return ac_client.get_campaign(campaign_id)


@mcp.tool()
def get_campaign_links(campaign_id: int) -> CampaignLinkList:
    """
    Retrieve links associated with a campaign from ActiveCampaign.

    Parameters:
    - campaign_id: The ID of the campaign to retrieve links for
    """
    return ac_client.get_campaign_links(campaign_id)


@mcp.tool()
def list_automations(params: AutomationListParams) -> AutomationList:
    """
    List all automations from ActiveCampaign with comprehensive filtering and ordering options.

    Parameters:
    - params: AutomationListParams object containing:
      - limit: Optional number of results to return
      - offset: Optional offset for pagination
      - filters: Optional AutomationFilterField object containing:
        - name: Filter by automation name (partial match)
        - status: Filter by exact status (1 - active, 2 - inactive)
        - ids: Comma-separated list of automation IDs
        - tag: Tag ID to filter by
        - triggers: Comma-separated list of start trigger types
        - actions: Comma-separated list of action block types
        - label_name: Filter by label/folder name
      - orders: Optional dictionary for ordering results by specific fields. Valid fields are:
        "name", "status", "entered (number of contacts that have entered the automation)", "cdate" (created date), "mdate" (modified date), "revisions"
        Example: {"name": "ASC", "cdate": "DESC"} to sort by name ascending, then created date descending
      - label: Filter by label/folder ID (integer)
      - search: String search in automation name
      - active: Filter by active status (true/false)
      - has_message: Filter automations that have messages (true/false)
      - enhance: Add enhanced data including blocks, goals, campaigns, counts, and labels (true/false)
    """
    return ac_client.list_automations(params)


@mcp.tool()
def list_contact_automations(
    params: ContactAutomationListParams,
) -> ContactAutomationList:
    """
    Get information about automation runs, for use when a user wants to know more about which automations a contact was in, which contacts went through which automation,
     or just generally more information about how an automation performs.

    Parameters:
    - params: ContactAutomationListParams object containing:
      - limit: Optional number of results to return
      - offset: Optional offset for pagination
      - filters: Optional ContactAutomationFilters object containing:
        - seriesid: Filter by automation ID (exact match)
        - adddate: Filter by date added (string or ContactAutomationDateFilter object with eq/gt/gte/lt/lte operators)
        - status: Filter by status (1 - autlmation in progress, 2 - automation has completed/ended)
        - subscriberid: Filter by contact ID (exact match)
      - orders: Optional dictionary for ordering results by specific fields. Valid fields are:
        "seriesid", "adddate", "status", "lastblock", "subscriberid", "name", "first_name", "last_name", "email", "cdate", "score", "goal_completion"
        Example: {"name": "ASC", "adddate": "DESC"} to sort by contact name ascending, then date added descending
      - q: Search term across contact fields (email, first_name, last_name, customer_acct_name, phone)
      - min_time: Filter by minimum timespan in automation (seconds)
      - max_time: Filter by maximum timespan in automation (seconds, 0 for immediately completed)
      - tags: List of tag IDs to filter by
      - g_tags: Goal-specific tag filter (list of tag IDs)
      - lists: List of list IDs to filter by
      - g_lists: Goal-specific list filter (list of list IDs)
      - g_id: Filter by goal ID
      - g_status: Goal completion status (0=incomplete, 1=complete)
      - g_min_time: Minimum goal completion time (seconds)
      - g_max_time: Maximum goal completion time (seconds)
      - scoreid: Score ID (required for score-based ordering)
      - include: Include related models in response
    """
    return ac_client.list_contact_automations(params)


@mcp.tool()
def get_contact_automation(contact_automation_id: int) -> SingleContactAutomationRecord:
    """
    Retrieve a specific contact automation record by ID.

    This provides detailed information about a specific automation run for a contact,
    including status, progress, completion details, and timing information.

    Parameters:
    - contact_automation_id: The ID of the contact automation record to retrieve
    """
    return ac_client.get_contact_automation(contact_automation_id)


@mcp.tool()
def add_contact_to_automation(
    params: ContactAutomationCreateParams,
) -> ContactAutomationCreateResponse:
    """
    Add a contact to an automation.

    This will start the automation for the specified contact. The contact will begin
    at the first step of the automation sequence.

    Parameters:
    - params: ContactAutomationCreateParams object containing:
      - contact: The ID of the contact to add to the automation
      - automation: The ID of the automation to add the contact to
    """
    return ac_client.add_contact_to_automation(params)


@mcp.tool()
def remove_contact_from_automation(contact_automation_id: int) -> Dict[str, Any]:
    """
    Remove a contact from an automation.

    This will stop the automation for the contact and remove them from the automation sequence.
    The contact will no longer receive any further communications from this automation.

    Parameters:
    - contact_automation_id: The ID of the contact automation record to remove/delete
    """
    return ac_client.remove_contact_from_automation(contact_automation_id)


@mcp.tool()
def list_groups(params: GroupListParams) -> GroupList:
    """
    List all user groups from ActiveCampaign.

    This tool is essential for list management workflows as it provides the available groups
    that can be associated with lists. When creating a new list, you must assign it to a group
    for it to be visible in the ActiveCampaign user interface.

    Parameters:
    - params: GroupListParams object containing:
      - limit: Optional number of results to return
      - offset: Optional offset for pagination
    """
    return ac_client.list_groups(params)


@mcp.tool()
def list_lists(params: ListListParams) -> ListList:
    """
    List all lists from ActiveCampaign with filtering and pagination options.

    This tool allows you to retrieve and filter lists in your ActiveCampaign account.
    Lists are used to organize contacts and manage email campaigns.

    Parameters:
    - params: ListListParams object containing:
      - limit: Optional number of results to return (default 20)
      - offset: Optional offset for pagination
      - filters: Optional dictionary for filtering by list name. Structure:
        {"name": {"operator": "value"}}

        Available operators:
        - "eq": Exact match
        - "neq": Not equal
        - "lt": Less than
        - "lte": Less than or equal
        - "gt": Greater than
        - "gte": Greater than or equal
        - "contains": Contains substring
        - "starts_with": Starts with substring

        Example: {"name": {"contains": "newsletter"}} to find lists containing "newsletter"

    Returns:
    - ListList object containing:
      - lists: List of ListRecord objects with detailed list information
      - meta: Metadata including total count

    Usage:
    Use this tool to browse available lists, search for specific lists by name,
    or get an overview of your list organization before creating new lists or
    managing existing ones.
    """
    return ac_client.list_lists(params)


@mcp.tool()
def get_list(list_id: int) -> SingleListRecord:
    """
    Retrieve a single list by ID from ActiveCampaign.

    This tool fetches detailed information about a specific list, including all
    configuration settings, tracking options, and metadata.

    Parameters:
    - list_id: The ID of the list to retrieve
    """
    return ac_client.get_list(list_id)


@mcp.tool()
def create_list(params: ListCreateParams) -> ListCreateResponse:
    """
    Create a new list in ActiveCampaign.

    This tool creates a new list for organizing contacts and managing email campaigns.

    Parameters:
    - params: ListCreateParams object containing:
      - name: Required name of the list
      - channel: Optional channel type ("sms" or "email", default: "email")
      - sender_url: Required sender URL for compliance
      - sender_reminder: Required reminder text for subscribers
      - send_last_broadcast: Optional flag for sending last broadcast (default: 0)
      - carboncopy: Optional carbon copy email address
      - subscription_notify: Optional email for subscription notifications
      - unsubscription_notify: Optional email for unsubscription notifications

    Usage:
    Use this tool to create new lists for organizing contacts. Consider using
    list_groups() to see available groups if you want to associate the new list
    with a group for better organization using create_list_group_permission().

    Note: For a list to be visible in the ActiveCampaign user interface for non-administrators,
    it may need to be associated with a user group.
    """
    return ac_client.create_list(params)


@mcp.tool()
def create_list_group_permission(
    params: ListGroupPermissionParams,
) -> ListGroupPermissionResponse:
    """
    Associate a list with a user group for enhanced organization and visibility.

    This tool creates a list group permission, which associates a specific list with a user group
    in ActiveCampaign. This association enables group-based permissions and makes lists visible
    in the appropriate sections of the ActiveCampaign interface.

    Parameters:
    - params: ListGroupPermissionParams object containing:
      - list: The ID of the list to associate with the group
      - group: The ID of the group to associate with the list

    Note: This is typically used after creating a list to ensure it appears in the correct
    sections of the ActiveCampaign interface for the appropriate user groups.
    """
    return ac_client.create_list_group_permission(params)


@mcp.tool()
def add_contact_to_list(params: ContactListUpdateParams) -> ContactListResponse:
    """
    Subscribe a contact to a list or update their subscription status.

    This tool allows you to add a contact to a list with a specific status, enabling
    contact list management and subscription control. Use this to subscribe contacts
    to lists for email campaigns and marketing automation.

    Parameters:
    - params: ContactListUpdateParams object containing:
      - contact: The ID of the contact to add to the list
      - list: The ID of the list to add the contact to
      - status: The subscription status for the contact:
        - 1 = Active (subscribed)
        - 2 = Unsubscribed
        - 0 = Unconfirmed

    Important Notes:
    - Setting status from unsubscribed (2) to active (1) may require additional confirmation
    - Use status 1 for normal subscription workflows
    - Status 0 is used for double opt-in processes
    - The contact and list must already exist in ActiveCampaign

    Use Cases:
    - Subscribe new contacts to marketing lists
    - Update subscription status for existing contacts
    """
    return ac_client.add_contact_to_list(params)


def main():
    mcp.run()
