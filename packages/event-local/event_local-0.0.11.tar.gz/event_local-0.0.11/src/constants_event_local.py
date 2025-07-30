from logger_local.LoggerComponentEnum import LoggerComponentEnum

# TODO We should bring this value from entity_type_view
EVENT_ENTITY_TYPE_ID = 14

EVENT_LOCAL_PYTHON_COMPONENT_ID = 247
EVENT_LOCAL_PYTHON_COMPONENT_NAME = "event-local-restapi-python-serverless"
DEVELOPER_EMAIL = "akiva.s@circ.zone"

EVENTS_LOCAL_CODE_LOGGER_OBJECT = {
    "component_id": EVENT_LOCAL_PYTHON_COMPONENT_ID,
    "component_name": EVENT_LOCAL_PYTHON_COMPONENT_NAME,
    "component_category": LoggerComponentEnum.ComponentCategory.Code.value,
    "developer_email": DEVELOPER_EMAIL,
}
