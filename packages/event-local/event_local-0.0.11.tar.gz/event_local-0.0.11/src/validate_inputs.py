from database_mysql_local.generic_crud import GenericCRUD
from database_mysql_local.table_columns import table_columns
from python_sdk_remote.utilities import validate_url

event_table_columns = table_columns["event_table"]


# Note: if you shange those messages, update the tests accordingly
class ValidateInputs(GenericCRUD):
    def __init__(self, is_test_data: bool = False) -> None:
        super().__init__(
            default_schema_name="event",
            default_column_name="event_id",
            default_table_name="event_table",
            default_view_table_name="event_view",
            is_test_data=is_test_data,
        )

    def validate_location_id(self, location_id: int) -> None:
        if location_id is None or not isinstance(location_id, int) or location_id < 0:
            raise ValueError(
                f"Invalid location_id: {location_id} (type: {type(location_id)})"
            )
        _location_id = self.select_one_value_by_column_and_value(
            schema_name="location",
            view_table_name="location_view",
            select_clause_value="location_id",
            column_name="location_id",
            column_value=location_id,
        )
        if _location_id is None:
            raise ValueError(
                f"Invalid location_id: {location_id} (not found in location.location_view)"
            )

    def validate_organizers_profile_id(self, organizers_profile_id: int) -> None:
        if (
            not organizers_profile_id
            or not isinstance(organizers_profile_id, int)
            or organizers_profile_id <= 0
        ):
            raise ValueError(
                f"Invalid organizers_profile_id: {organizers_profile_id} (type: {type(organizers_profile_id)})"
            )
        _organizers_profile_id = self.select_one_value_by_column_and_value(
            schema_name="profile",
            view_table_name="profile_view",
            select_clause_value="profile_id",
            column_name="profile_id",
            column_value=organizers_profile_id,
        )
        if _organizers_profile_id is None:
            raise ValueError(
                f"Invalid organizers_profile_id: {organizers_profile_id} (not found in profile.profile_view)"
            )

    def validate_input_dict(self, input_dict: dict) -> None:
        location_id = input_dict.get("location_id")
        organizers_profile_id = input_dict.get("organizers_profile_id")
        website_url = input_dict.get("website_url")
        facebook_event_url = input_dict.get("facebook_event_url")
        meetup_event_url = input_dict.get("meetup_event_url")
        registration_url = input_dict.get("registration_url")
        # TODO: allowed_keys = [...] and set(input_dict.keys()) == set(allowed_keys)
        self.validate_location_id(location_id)
        self.validate_organizers_profile_id(organizers_profile_id)

        if website_url and not validate_url(website_url):
            raise ValueError(f"Invalid input: website_url - {website_url}")
        if facebook_event_url and not validate_url(facebook_event_url):
            raise ValueError(
                f"Invalid input: facebook_event_url - {facebook_event_url}"
            )
        if meetup_event_url and not validate_url(meetup_event_url):
            raise ValueError(f"Invalid input: meetup_event_url - {meetup_event_url}")
        if registration_url and not validate_url(registration_url):
            raise ValueError(f"Invalid input: registration_url - {registration_url}")

        for key in list(input_dict):
            if key not in event_table_columns:
                input_dict.pop(key)

    # TODO Move this function to database-mysql-python-package and make it generic for all tables using Entity enum
    def validate_id(self, entity_id: int, schema: str = "event") -> None:
        try:
            entity_id = int(entity_id)
            if entity_id < 0:
                raise ValueError
        except ValueError:
            raise ValueError(f"Invalid {schema}_id: {entity_id}")
        assert ";" not in schema  # Prevent SQL Injection
        # value = self.select_one_value_by_column_and_value(
        value = self.select_one_value_by_where(
            schema_name=schema,
            view_table_name=schema + "_view",
            select_clause_value=schema + "_id",
            where="event_id = %s",
            params=(entity_id,),
        )
        if value is None:
            raise ValueError(
                f"Invalid {schema}_id: {entity_id} (not found in {schema}.{schema}_view)"
            )
