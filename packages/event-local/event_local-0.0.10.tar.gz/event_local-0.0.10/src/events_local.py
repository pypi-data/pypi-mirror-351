# TODO Can we use event-local package instead of this file

# TOOD Can we delete GenericCRUD?
from database_mysql_local.generic_crud import DEFAULT_SQL_SELECT_LIMIT  # , GenericCRUD
from database_mysql_local.generic_crud_ml import GenericCRUDML
from location_local.locations_local_crud import LocationsLocal
from logger_local.MetaLogger import MetaLogger
from .constants_event_local import EVENTS_LOCAL_CODE_LOGGER_OBJECT, EVENT_ENTITY_TYPE_ID
from .validate_inputs import ValidateInputs
from language_remote import lang_code
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.


# OLD class EventsLocal(GenericCRUD, metaclass=MetaLogger, object=EVENTS_LOCAL_CODE_LOGGER_OBJECT):
class EventsLocal(
    GenericCRUDML, metaclass=MetaLogger, object=EVENTS_LOCAL_CODE_LOGGER_OBJECT
):

    def __init__(self, is_test_data: bool = False) -> None:
        super().__init__(
            default_schema_name="event",
            default_column_name="event_id",
            default_table_name="event_table",
            default_view_table_name="event_view",
            default_view_with_deleted_and_test_data="event_general_with_deleted_and_test_data_view",
            is_test_data=is_test_data,
        )
        self.validate_inputs = ValidateInputs(is_test_data=is_test_data)

        # TODO: use dependency injection in future versions
        # vector_db = []
        # vector_db[0] = OpenSearchIngester(is_test_data=is_test_data)
        # vector_db[1] = PGvector(is_test_data=is_test_data)
        # moved to genereic_crud

    # TODO: test
    def select_all_events(
        self, lang_code_str: lang_code.LangCode, limit: int = None
    ) -> list:
        """Returns all the rows in the event_table"""
        limit = limit or 10000
        # TODO If we don't have result int the profile preferred language, we should bring the English version
        # TODO If event has multiple names we should bring the one which is_main = TRUE
        sql_query = f"""
            SELECT event.event_id         AS 'event_id',
                   {EVENT_ENTITY_TYPE_ID} AS 'item_type_id',
                   event.location_id,
                   event.organizers_profile_id,
                   event.website_url,
                   event.facebook_event_url,
                   event.meetup_event_url,
                   event_ml.title
            FROM event.event_view AS event
                     LEFT JOIN event.event_ml_view AS event_ml ON event.event_id = event_ml.event_id
                AND event_ml.lang_code = %s
            LIMIT {limit}"""
        self.cursor.execute(sql_query, (lang_code_str.value,))
        columns = (
            "event_id, item_type_id, location_id, organizers_profile_id, website_url, "
            "facebook_event_url, meetup_event_url, title"
        )
        events_dict = self.convert_multi_to_dict(self.cursor.fetchall(), columns)
        return events_dict

    def select_events_by_title(self, title: str, limit: int = None) -> list:
        """Returns all the events that have the given title"""
        limit = limit or DEFAULT_SQL_SELECT_LIMIT
        events_list = self.select_multi_dict_by_column_and_value(
            view_table_name="event_ml_view",
            column_name="title",
            column_value=title,
            limit=limit,
        )
        return events_list

    # TODO: test
    def select_events_by_profile_id(self, profile_id: int, limit: int = None) -> list:
        """Returns all the events that are related to the given profile_id"""
        self.validate_inputs.validate_id(profile_id, schema="profile")
        limit = limit or DEFAULT_SQL_SELECT_LIMIT
        # TODO: should we move this to a view?
        sql_query = f"""
        WITH EventCommonGroups AS (
            SELECT event.event_id,
                   event_ml.title,
                   {EVENT_ENTITY_TYPE_ID}        AS item_type,
                   COUNT(group_profile.group_id) AS common_group_count
            FROM event.event_view AS event
                     LEFT JOIN
                 event.event_ml_view AS event_ml ON event.event_id = event_ml.event_id
                     LEFT JOIN
                 event_group.event_group_view AS event_group ON event.event_id = event_group.event_id
                     LEFT JOIN
                 group_profile.group_profile_view AS group_profile
                 ON event_group.group_id = group_profile.group_id AND
                    group_profile.profile_id = %s
            GROUP BY event.event_id, event_ml.title
        )

        SELECT event.event_id,
               event.location_id,
               event.organizers_profile_id,
               event.website_url,
               event.facebook_event_url,
               event.meetup_event_url,
               event.registration_url,
               EventCommonGroups.title,
               EventCommonGroups.item_type,
               EventCommonGroups.common_group_count,
               event_location.location_id AS event_location_id,
               (COALESCE(1 / ST_Distance(
                       event_location.coordinate, COALESCE(location_profile.coordinate, event_location.coordinate)), 0)) AS distance_rank,
               (COALESCE(1 / ST_Distance(
                       event_location.coordinate, COALESCE(location_profile.coordinate, event_location.coordinate)), 0)) +
                        COALESCE(EventCommonGroups.common_group_count / 5, 0)               AS final_rank
        FROM EventCommonGroups
                 LEFT JOIN
             event.event_view AS event ON EventCommonGroups.event_id = event.event_id
                 LEFT JOIN
             (SELECT event_location.event_id,
                     event_location.location_id,
                     location.coordinate
              FROM event_location.event_location_view AS event_location
                       LEFT JOIN location.location_view AS location ON event_location.location_id = location.location_id) AS event_location
             ON event.event_id = event_location.event_id
                 LEFT JOIN
             (SELECT location_profile.location_id,
                     location.coordinate,
                     location_profile.profile_id
              FROM location_profile.location_profile_view AS location_profile
                       LEFT JOIN location.location_view AS location ON location_profile.location_id = location.location_id
              ORDER BY location_profile.start_timestamp DESC
              LIMIT 1) AS location_profile ON location_profile.profile_id = %s
                 LEFT JOIN
             location.location_view AS location ON location.location_id = location_profile.location_id
        ORDER BY final_rank DESC
        LIMIT {limit};
        """

        self.cursor.execute(sql_query, (profile_id, profile_id))
        columns = (
            "event.event_id, eventlocation_id, eventorganizers_profile_id, eventwebsite_url, "
            "eventfacebook_event_url, eventmeetup_event_url, eventregistration_url, title, item_type, "
            "common_group_count, event_location_id, distance_rank, final_rank"
        )
        events_dict = self.convert_multi_to_dict(self.cursor.fetchall(), columns)

        return events_dict

    def select_by_event_id(self, event_id: int) -> dict:
        """Returns the event row with the given event_id"""
        self.validate_inputs.validate_id(event_id)
        # TODO add support to event-external
        # select_clause = "event_id, location_id, organizers_profile_id, website_url, facebook_event_url, meetup_event_url, registration_url"
        select_clause = "*"
        event = self.select_one_dict_by_column_and_value(
            column_value=event_id, select_clause_value=select_clause
        )
        return event

    def insert_event_data(self, event_data: dict) -> int:
        """Inserts a row into the event_table and returns the id of the inserted row"""
        self.validate_inputs.validate_input_dict(input_dict=event_data)
        event_id = self.insert(data_dict=event_data)
        # for v_db in self.vector_db:
        #     v_db.insert(data_dict=event_data)
        return event_id

    def update_by_event_id(self, event_id: int, event_data: dict) -> int:
        """Updates the event row with the given event_id"""
        self.validate_inputs.validate_id(event_id)
        self.validate_inputs.validate_input_dict(input_dict=event_data)
        amount_of_events_updated = self.update_by_column_and_value(
            column_value=event_id, data_dict=event_data
        )
        return amount_of_events_updated

    def delete_by_event_id(self, event_id: int) -> int:
        """Deletes the event row with the given event_id"""
        self.validate_inputs.validate_id(event_id)
        amount_of_events_deleted = self.delete_by_column_and_value(
            column_value=event_id
        )
        return amount_of_events_deleted

    def get_test_event_id(self) -> int:
        location_id = LocationsLocal().get_test_location_id()
        test_event_id = super().get_test_entity_id(
            schema_name="event",
            view_name="event_view",
            entity_name="event",
            insert_function=self.insert,
            insert_kwargs={"location_id": location_id},
        )
        return test_event_id

    # Utilities
    def merge_event_ml_entities(
        self, entity_id1: int, entity_id2: int, main_entity_ml_id: int
    ):
        super().merge_ml_entities(
            entity_id1=entity_id1,
            entity_id2=entity_id2,
            main_entity_ml_id=main_entity_ml_id,
        )

    def merge_event_entities(
        self,
        entity_id1: int,
        entity_id2: int,
    ):
        super().merge_entities(entity_id1=entity_id1, entity_id2=entity_id2)

    # Metrics

    # Used by platform-metrics
    # TODO Should be used by event-metrics
    def get_number_of_events(self) -> int:
        sql_statement = "SELECT COUNT(*) FROM event.event_table"
        self.cursor.execute(sql_statement=sql_statement)
        number_of_events = self.cursor.fetchone()[0]
        return number_of_events
