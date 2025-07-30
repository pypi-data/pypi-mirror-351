from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import List, Literal, Optional, Any, Dict, Union
from enum import Enum
from datetime import date, datetime


class ContactAutomationLinks(BaseModel):
    automation: str
    contact: str
    contactGoals: str
    automationLogs: str
    subscriberSeriesEnd: str


class ContactAutomation(BaseModel):
    contact: str
    seriesid: str
    startid: str
    status: str
    batchid: str
    adddate: str
    remdate: str
    timespan: str
    lastblock: str
    lastlogid: str
    lastdate: str
    in_als: str
    completedElements: int
    totalElements: int
    completed: int
    completeValue: int
    links: ContactAutomationLinks
    id: str
    automation: str


class ContactAutomationMeta(BaseModel):
    total: str
    showcase_stats: List[Any] = []


class ContactAutomationList(BaseModel):
    contactAutomations: List[ContactAutomation]
    meta: ContactAutomationMeta


ContactAutomationSortField = Literal[
    "seriesid",
    "adddate",
    "status",
    "lastblock",
    "subscriberid",
    "name",
    "first_name",
    "last_name",
    "email",
    "cdate",
    "score",
    "goal_completion",
]

ContactAutomationFilterField = Literal[
    "seriesid", "adddate", "status", "lastblock", "subscriberid"
]

ContactAutomationDateOperator = Literal["eq", "gt", "gte", "lt", "lte"]


class ContactAutomationDateFilter(BaseModel):
    eq: Optional[Union[str, date, datetime]] = None
    gt: Optional[Union[str, date, datetime]] = None
    gte: Optional[Union[str, date, datetime]] = None
    lt: Optional[Union[str, date, datetime]] = None
    lte: Optional[Union[str, date, datetime]] = None


class ContactAutomationFilters(BaseModel):
    seriesid: Optional[Union[str, int]] = None
    adddate: Optional[Union[str, ContactAutomationDateFilter]] = None
    status: Optional[Union[str, int]] = None
    lastblock: Optional[Union[str, int]] = None
    subscriberid: Optional[Union[str, int]] = None


class ContactAutomationListParams(BaseModel):
    limit: Optional[int] = None
    offset: Optional[int] = None

    filters: Optional[ContactAutomationFilters] = None

    orders: Optional[Dict[ContactAutomationSortField, Literal["ASC", "DESC"]]] = None

    q: Optional[str] = None

    min_time: Optional[int] = None
    max_time: Optional[int] = None

    tags: Optional[List[int]] = Field(None, alias="tags[]")
    g_tagid: Optional[int] = None
    g_tags: Optional[List[int]] = Field(None, alias="g_tags[]")

    lists: Optional[List[int]] = Field(None, alias="lists[]")
    g_listid: Optional[int] = None
    g_lists: Optional[List[int]] = Field(None, alias="g_lists[]")

    g_id: Optional[int] = None
    g_status: Optional[Literal[0, 1]] = None
    g_min_time: Optional[int] = None
    g_max_time: Optional[int] = None

    scoreid: Optional[int] = None

    include: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True, populate_by_alias=True)


class FieldValueLinks(BaseModel):
    owner: str
    field: str


class FieldValue(BaseModel):
    contact: str
    field: str
    value: str
    cdate: Optional[str] = None
    udate: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    links: FieldValueLinks
    id: Optional[str] = None
    owner: Optional[str] = None


class ContactLinks(BaseModel):
    bounceLogs: str
    contactAutomations: str
    contactData: str
    contactGoals: str
    contactLists: str
    contactLogs: str
    contactTags: str
    contactDeals: str
    deals: str
    fieldValues: str
    geoIps: str
    notes: str
    organization: str
    plusAppend: str
    trackingLogs: str
    scoreValues: str
    automationEntryCounts: str


class ContactDetails(BaseModel):
    cdate: str
    email: str
    phone: Optional[str] = None
    firstName: str
    lastName: str
    orgid: str
    orgname: str
    segmentio_id: str
    bounced_hard: str
    bounced_soft: str
    bounced_date: Optional[str] = None
    ip: str
    ua: Optional[str] = ""
    hash: str
    socialdata_lastcheck: Optional[str] = None
    email_local: str
    email_domain: str
    sentcnt: str
    rating_tstamp: Optional[str] = None
    gravatar: str
    deleted: str
    anonymized: str
    adate: Optional[str] = None
    udate: str
    edate: Optional[str] = None
    deleted_at: Optional[str] = None
    created_utc_timestamp: str
    updated_utc_timestamp: str
    created_timestamp: str
    updated_timestamp: str
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    mpp_tracking: str
    last_click_date: Optional[str] = None
    last_open_date: Optional[str] = None
    last_mpp_open_date: Optional[str] = None
    best_send_hour: Optional[str] = None
    contactAutomations: List[str]
    contactLists: List[str]
    fieldValues: List[FieldValue]
    geoIps: List[str]
    deals: List[str]
    sentiment: Optional[str] = None
    accountContacts: List[str]
    scoreValues: List[Any] = []
    links: ContactLinks
    id: str
    organization: Optional[str] = None


class ContactCreateResponse(BaseModel):
    contact: ContactDetails
    fieldValues: List[FieldValue]


class SingleContactAutomationRecord(BaseModel):
    contactAutomation: ContactAutomation


class ContactAutomationCreateParams(BaseModel):
    contact: int
    automation: int


class ContactAutomationCreateResponse(BaseModel):
    contacts: List[ContactDetails]
    contactAutomation: ContactAutomation


class ContactTagLinks(BaseModel):
    contact: str
    tag: str


class ContactTag(BaseModel):
    cdate: str
    contact: str
    id: str
    links: ContactTagLinks
    tag: str


class ContactTagResponse(BaseModel):
    contactTag: ContactTag


class ContactCreateFieldValues(BaseModel):
    field: int
    value: str


class ContactCreateParams(BaseModel):
    email: str
    firstName: str
    lastName: str
    phone: str
    fieldValues: Optional[List[ContactCreateFieldValues]] = None


class ContactTagParams(BaseModel):
    contact: int
    tag: int


class Tag(BaseModel):
    tagType: str
    tag: str
    description: str
    cdate: str
    id: str


class TagCreateResponse(BaseModel):
    tag: Tag


class TagCreateParams(BaseModel):
    tag: str
    description: str = ""
    tagType: str = "contact"


class TagList(BaseModel):
    tags: List[Tag]


class SingleTagRecord(BaseModel):
    tag: Tag


class SingleContactRecord(BaseModel):
    contactAutomations: List[ContactAutomation]
    contactLists: List[Any] = []
    deals: List[Any] = []
    fieldValues: List[FieldValue]
    geoIps: List[Any] = []
    contact: ContactDetails


class PageInputParams(BaseModel):
    segmentid: Optional[Any] = None
    formid: int = 0
    listid: int = 0
    tagid: int = 0
    limit: int = 20
    offset: int = 0
    search: Optional[str] = None
    sort: Optional[str] = None
    seriesid: int = 0
    waitid: int = 0
    status: int = -1
    forceQuery: int = 0
    cacheid: Optional[str] = None


class ContactListMeta(BaseModel):
    page_input: PageInputParams
    total: str
    sortable: bool


class ContactList(BaseModel):
    scoreValues: List[Any] = []
    contacts: List[ContactDetails] = []
    meta: ContactListMeta


ContactCustomFieldType = Literal[
    "text",
    "textarea",
    "dropdown",
    "checkbox",
    "radio",
    "date",
    "datetime",
    "hidden",
    "listbox",
]


class ContactStatus(Enum):
    ANY = -1
    UNCONFIRMED = 0
    ACTIVE = 1
    UNSUBSCRIBED = 2
    BOUNCED = 3


ContactSortField = Literal[
    "id", "cdate", "email", "first_name", "last_name", "name", "score"
]

ContactFilterField = Literal[
    "created_before", "created_after", "updated_before", "updated_after"
]

EmailActivityFilterField = Literal["subscriberid", "fieldid"]

EmailActivitySortField = Literal["subscriberid", "fieldid", "tstamp", "id"]


class ContactListParams(BaseModel):
    segmentid: Optional[int] = None
    formid: Optional[int] = None
    listid: Optional[int] = None
    tagid: Optional[int] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    search: Optional[str] = None
    orders: Optional[Dict[ContactSortField, Literal["ASC", "DESC"]]] = None
    filters: Optional[Dict[ContactFilterField, Union[str, datetime, date]]] = None
    id_greater: Optional[int] = None
    seriesid: Optional[int] = None
    waitid: Optional[int] = None
    status: Optional[ContactStatus] = None


TagSearchOperator = Literal[
    "eq", "neq", "lt", "lte", "gt", "gte", "contains", "starts_with"
]

TagOrderMethod = Literal["weight", "asc", "desc"]


class TagListParams(BaseModel):
    search_filters: Optional[Dict[TagSearchOperator, str]] = Field(
        None, alias="filters[search]"
    )
    order_method: Optional[TagOrderMethod] = Field(None, alias="orders[search]")
    limit: Optional[int] = None
    offset: Optional[int] = None

    model_config = ConfigDict(populate_by_name=True, populate_by_alias=True)


class ContactCustomFieldListParams(BaseModel):
    limit: Optional[int] = None
    offset: Optional[int] = None

    model_config = ConfigDict(populate_by_name=True, populate_by_alias=True)


class FieldOption(BaseModel):
    orderid: int
    value: str
    label: str
    isdefault: bool = False
    field: str
    id: Optional[str] = None
    cdate: Optional[str] = None
    udate: Optional[str] = None
    links: Optional[Dict[str, str]] = None


class ContactCustomField(BaseModel):
    title: str
    descript: Optional[str] = None
    type: ContactCustomFieldType
    perstag: Optional[str] = None
    group: Optional[int] = None
    show_in_list: bool = True
    rows: int = 0
    cols: int = 0
    visible: bool = True
    ordernum: int = 0
    defval: Optional[str] = None
    id: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    cdate: Optional[str] = None
    udate: Optional[str] = None
    options: Optional[List[FieldOption]] = None
    relations: Optional[List[Any]] = None
    links: Optional[Dict[str, str]] = None


class ContactCustomFieldCreateParams(BaseModel):
    title: str
    type: ContactCustomFieldType
    perstag: Optional[str] = None
    descript: Optional[str] = None
    defval: Optional[str] = None
    visible: Optional[Literal[0, 1]] = None
    ordernum: Optional[int] = None


class ContactCustomFieldCreateResponse(BaseModel):
    field: ContactCustomField


class FieldOptionCreateParams(BaseModel):
    orderid: int
    value: str
    label: str
    isdefault: bool = False
    field: str


class FieldOptionBulkCreateParams(BaseModel):
    fieldOptions: List[FieldOptionCreateParams]


class ContactFieldRelCreateParams(BaseModel):
    relid: int
    field: str


class ContactCustomFieldList(BaseModel):
    fields: List[ContactCustomField]
    meta: Optional[Dict[str, Any]] = None
    fieldOptions: List[FieldOption] = []
    fieldRels: List[Any] = []


class SingleContactCustomFieldRecord(BaseModel):
    field: ContactCustomField


class ContactFieldValueCreateParams(BaseModel):
    contact: int
    field: int
    value: str
    useDefaults: Optional[bool] = None


class ContactFieldValueUpdateParams(BaseModel):
    value: str
    useDefaults: Optional[bool] = None


class ContactFieldValueResponse(BaseModel):
    fieldValue: FieldValue


class ContactFieldValueList(BaseModel):
    fieldValues: List[FieldValue]
    meta: Optional[Dict[Literal["total"], int]] = None


class ContactFieldValueListParams(BaseModel):
    filters: Optional[Dict[Literal["fieldid"], int]] = None
    limit: Optional[int] = None
    offset: Optional[int] = None

    model_config = ConfigDict(populate_by_name=True, populate_by_alias=True)


class EmailActivityListParams(BaseModel):
    limit: Optional[int] = None
    offset: Optional[int] = None
    orders: Optional[Dict[EmailActivitySortField, Literal["ASC", "DESC"]]] = None
    filters: Optional[Dict[EmailActivityFilterField, str]] = None

    model_config = ConfigDict(populate_by_name=True, populate_by_alias=True)


class EmailActivity(BaseModel):
    subscriberid: str
    userid: str
    d_id: str
    account: Optional[str] = None
    reltype: str
    relid: str
    from_name: Optional[str] = None
    fromAddress: Optional[str] = None
    toAddress: Optional[str] = None
    ccAddress: Optional[str] = None
    subject: Optional[str] = None
    message: Optional[str] = None
    messageHtml: Optional[str] = None
    tstamp: str
    sentiment: Optional[str] = None
    files: Optional[Any] = None
    connectionid: Optional[str] = None
    messageid: Optional[str] = None
    series_id: Optional[str] = None
    subscriber_series_id: Optional[str] = None
    automation_name: Optional[str] = None
    service_provider: Optional[str] = None
    links: Dict[str, str]
    id: str
    contact: str
    deal: Optional[str] = None
    user: str
    reference: Optional[Dict[str, str]] = None


class EmailActivityList(BaseModel):
    emailActivities: List[EmailActivity]
    meta: Optional[Dict[Literal["total"], int]] = None


class CampaignLink(BaseModel):
    campaignid: str
    messageid: str
    link: str
    name: str
    ref: str
    tracked: str
    links: Dict[str, str]
    id: str
    campaign: str
    message: Optional[str] = None


class CampaignLinkList(BaseModel):
    links: List[CampaignLink]


class Campaign(BaseModel):
    type: str
    userid: str
    segmentid: str
    bounceid: str
    realcid: str
    sendid: str
    threadid: str
    seriesid: str
    formid: str
    basetemplateid: str
    visible: str
    cdate: str
    name: str
    sdate: Optional[str] = None
    status: str
    public: str
    lastsent: Optional[str] = None
    lastopened: Optional[str] = None
    reply2: Optional[str] = None
    priority: Optional[str] = None
    links: Dict[str, str]
    id: str
    user: str


class CampaignList(BaseModel):
    campaigns: List[Campaign]
    meta: Optional[Dict[str, Any]] = None


CampaignType = Literal[
    "single",
    "recurring",
    "split",
    "responder",
    "reminder",
    "special",
    "activerss",
    "text",
]

CampaignSortField = Literal["sdate", "mdate", "ldate", "status"]

CampaignStatus = Literal[
    "drafts",  # 0
    "scheduled",  # 1
    "currently-sending",  # 2
    "paused",  # 3
    "stopped",  # 4
    "complete",  # 5
    "disabled",  # 6
    "pending-review",  # 7
    "determining-winner",  # special case
]

CampaignStatusValue = Literal[0, 1, 2, 3, 4, 5, 6, 7]

CampaignExactFilterField = Literal[
    "subscriberid", "willrecur", "seriesid", "type", "label_name", "list_id"
]

CampaignPartialFilterField = Literal["name", "id", "status"]


class CampaignFilterField(BaseModel):
    type: Optional[CampaignType] = None
    list_id: Optional[int] = None
    automation: Optional[bool] = None
    willrecur: Optional[bool] = None
    seriesid: Optional[str] = None
    label_name: Optional[str] = None
    name: Optional[str] = None
    id: Optional[int] = None
    status: Optional[str] = None


class CampaignListParams(BaseModel):
    limit: Optional[int] = None
    offset: Optional[int] = None
    orders: Optional[Dict[CampaignSortField, Literal["ASC", "DESC"]]] = None
    filters: Optional[CampaignFilterField] = None

    has_message: Optional[bool] = None
    has_message_content: Optional[bool] = None
    has_form: Optional[bool] = None
    campaignListing: Optional[int] = None
    status: Optional[CampaignStatus] = None
    excludeTypes: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True, populate_by_alias=True)


class SingleCampaignRecord(BaseModel):
    campaign: Campaign


class AutomationLinks(BaseModel):
    campaigns: str
    contactGoals: str
    contactAutomations: str
    blocks: str
    goals: str
    sms: str
    sitemessages: str


class Automation(BaseModel):
    name: str
    cdate: str
    mdate: str
    userid: str
    status: str
    entered: str
    exited: str
    hidden: str
    defaultscreenshot: str
    screenshot: str
    links: AutomationLinks
    id: str


class AutomationMeta(BaseModel):
    total: str
    starts: List[Dict[str, str]]
    filtered: bool
    smsLogs: List[Any] = []


class AutomationList(BaseModel):
    automations: List[Automation]
    meta: AutomationMeta


AutomationSortField = Literal[
    "name",
    "status",
    "entered",
    "cdate",
    "mdate",
    "revisions",
]


class AutomationFilterField(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    ids: Optional[str] = None
    tag: Optional[int] = None
    triggers: Optional[str] = None
    actions: Optional[str] = None
    label_name: Optional[str] = None


class AutomationListParams(BaseModel):
    limit: Optional[int] = None
    offset: Optional[int] = None

    filters: Optional[AutomationFilterField] = None
    orders: Optional[Dict[AutomationSortField, Literal["ASC", "DESC"]]] = None

    label: Optional[int] = None
    search: Optional[str] = None
    active: Optional[bool] = None
    has_message: Optional[bool] = None

    enhance: Optional[bool] = None

    model_config = ConfigDict(populate_by_name=True, populate_by_alias=True)


class GroupLinks(BaseModel):
    userGroups: str
    groupLimit: str
    dealGroupGroups: str
    listGroups: str
    addressGroups: str
    automationGroups: str


class GroupRecord(BaseModel):
    title: str
    descript: Optional[str] = None
    id: str


class GroupMeta(BaseModel):
    total: str


class GroupList(BaseModel):
    groups: List[GroupRecord]
    meta: GroupMeta


class GroupListParams(BaseModel):
    limit: Optional[int] = None
    offset: Optional[int] = None

    model_config = ConfigDict(populate_by_name=True, populate_by_alias=True)


class ListLinks(BaseModel):
    contactGoalLists: str
    user: str
    addressLists: str


class ListRecord(BaseModel):
    stringid: str
    userid: str
    name: str
    cdate: str
    p_use_tracking: str
    p_use_analytics_read: str
    p_use_analytics_link: str
    p_use_twitter: str
    p_use_facebook: str
    p_embed_image: str
    p_use_captcha: str
    send_last_broadcast: str
    private: str
    analytics_domains: Optional[str] = None
    analytics_source: str
    analytics_ua: str
    twitter_token: str
    twitter_token_secret: str
    facebook_session: Optional[str] = None
    carboncopy: Optional[str] = None
    subscription_notify: Optional[str] = None
    unsubscription_notify: Optional[str] = None
    require_name: str
    get_unsubscribe_reason: str
    to_name: str
    optinoptout: str
    sender_name: str
    sender_addr1: str
    sender_addr2: str
    sender_city: str
    sender_state: str
    sender_zip: str
    sender_country: str
    sender_phone: str
    sender_url: str
    sender_reminder: str
    fulladdress: str
    optinmessageid: str
    optoutconf: str
    deletestamp: Optional[str] = None
    udate: Optional[str] = None
    links: ListLinks
    id: str
    user: str


class ListMeta(BaseModel):
    total: str


class ListList(BaseModel):
    lists: List[ListRecord]
    meta: ListMeta


ListFilterChannelType = Literal["email", "sms", "all"]
ListSortDirection = Literal["ASC", "DESC"]
ListNameOrderSetting = Literal["ASC", "DESC", "weight"]


class ListFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)

    name: Optional[str] = None
    list_id: Optional[str] = Field(None, alias="id")
    channel: Optional[ListFilterChannelType] = None
    userid_single: Optional[int] = Field(None, alias="userid")
    userid_array: Optional[List[int]] = Field(None, alias="userid[]")
    created_timestamp: Optional[Union[str, date, datetime]] = None
    active_subscribers: Optional[int] = None

    @model_validator(mode="after")
    def check_userid_fields(self) -> "ListFilters":
        if self.userid_single is not None and self.userid_array is not None:
            raise ValueError(
                "Cannot set both 'userid' (single) and 'userid[]' (array) filters."
            )
        return self


class ListOrders(BaseModel):
    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)
    name: Optional[ListNameOrderSetting] = None
    id: Optional[ListSortDirection] = None
    channel: Optional[ListSortDirection] = None
    userid: Optional[ListSortDirection] = None
    created_timestamp: Optional[ListSortDirection] = None
    active_subscribers: Optional[ListSortDirection] = None


class ListListParams(BaseModel):
    limit: Optional[int] = None
    offset: Optional[int] = None
    filters: Optional[ListFilters] = None
    orders: Optional[ListOrders] = None

    model_config = ConfigDict(populate_by_name=True, populate_by_alias=True)


class SingleListRecord(BaseModel):
    list: ListRecord


class ListGroupPermissionParams(BaseModel):
    list: int
    group: int


class ListGroupPermissionResponse(BaseModel):
    listGroup: Dict[str, Any]


class ListCreateParams(BaseModel):
    name: str
    channel: Optional[Literal["email", "sms"]] = "email"
    sender_url: str = None
    sender_reminder: str = None
    send_last_broadcast: Optional[int] = 0
    carboncopy: Optional[str] = ""
    subscription_notify: Optional[str] = ""
    unsubscription_notify: Optional[str] = ""


class ListCreateResponse(BaseModel):
    list: ListRecord


class ListUpdateParams(BaseModel):
    name: str = None
    sender_url: str = None
    sender_reminder: str = None
    send_last_broadcast: Optional[int] = 0
    carboncopy: Optional[str] = ""
    subscription_notify: Optional[str] = ""
    unsubscription_notify: Optional[str] = ""


class ListUpdateResponse(BaseModel):
    list: ListRecord


class ContactListUpdateParams(BaseModel):
    contact: int
    list: int
    status: int


class ContactListLinks(BaseModel):
    automation: Optional[str] = None
    list: str
    contact: str
    form: Optional[str] = None
    autosyncLog: Optional[str] = None
    campaign: Optional[str] = None
    unsubscribeAutomation: Optional[str] = None
    message: Optional[str] = None


class ContactListRecord(BaseModel):
    contact: str
    list: str
    form: Optional[str] = None
    seriesid: str
    sdate: str
    status: int
    responder: str
    sync: str
    unsubreason: str
    campaign: Optional[str] = None
    message: Optional[str] = None
    first_name: str
    last_name: str
    ip4Sub: str
    sourceid: str
    autosyncLog: Optional[str] = None
    ip4_last: str
    ip4Unsub: str
    unsubscribeAutomation: Optional[str] = None
    links: ContactListLinks
    id: str
    automation: Optional[str] = None


class ContactListResponse(BaseModel):
    contacts: List[ContactDetails]
    contactList: ContactListRecord
