from typing import Dict

import holidays
from database_mysql_local.generic_crud import GenericCRUD
from logger_local.MetaLogger import MetaLogger

# from location_local.locations_local_crud import LocationsLocal
from .constants_event_local import EVENTS_LOCAL_CODE_LOGGER_OBJECT


# TODO: test
class HolidayLocal(
    GenericCRUD, metaclass=MetaLogger, object=EVENTS_LOCAL_CODE_LOGGER_OBJECT
):
    """HolidayLocal"""

    def __init__(self, is_test_data: bool = False) -> None:
        super().__init__(
            default_schema_name="event",
            default_table_name="event_table",
            default_view_table_name="event_view",
            default_column_name="event_id",
            is_test_data=is_test_data,
        )

    def insert_holiday(
        self, *, date: str, holiday: str, country: str, state: str = None
    ) -> int:
        """Inserts a new holiday and returns the new holiday_id"""

        # location_obj = LocationsLocal()
        # lang_code = "en"
        # all_details = {"coordinate": {"latitude": None, "longitude": None}, "address_local_language": None,
        #                "address_english": None, "neighborhood": None, "county": None, "region": None, "state": state,
        #                "country": country, "postal_code": None, "plus_code": None, "is_approved": False}
        # location_id = location_obj.get_location_ids(all_details, lang_code, True)
        location_id = 3  # TODO
        if self.holiday_exists(
            date=date, holiday=holiday, country=country, state=state
        ):
            event_table_data = {
                "start_timestamp": date,
                "location_id": location_id,
                "website_url": "test for holiday",
            }
            holiday_id = super().insert(data_dict=event_table_data)
            return holiday_id

    def update_holiday(self, *, holiday_id: int, holiday_data: Dict[str, any]) -> None:
        """Updates an existing holiday"""
        event_table_data = {
            "date": holiday_data.get("date"),
            "holiday": holiday_data.get("holiday"),
            "country": holiday_data.get("country"),
            "state": holiday_data.get("state"),
        }
        super().update_by_column_and_value(
            column_value=holiday_id, data_dict=event_table_data
        )

    def get_holiday_by_id(self, holiday_id: int) -> Dict[str, any]:
        """Gets holiday information by holiday_id"""
        holiday_dict = self.select_one_dict_by_column_and_value(column_value=holiday_id)
        return holiday_dict

    def delete_holiday_by_id(self, holiday_id: int) -> None:
        """Deletes a holiday by holiday_id"""
        self.delete_by_column_and_value(column_value=holiday_id)

    def holiday_exists(
        self, *, date: str, holiday: str, country: str, state: str = None
    ) -> bool:
        """Checks if a holiday with the given details already exists in the database"""
        # TODO: fix
        # conditions = {
        #     "date": date,
        #     "holiday": holiday,
        #     "country": country,
        #     "state": state
        # }
        existing_holiday = self.select_one_dict_by_column_and_value(
            view_table_name="event_view", column_name="event_id", column_value="2"
        )
        return existing_holiday is not None

    @staticmethod
    def fetch_holidays(country: str, year: int) -> list:
        """fetch us holidays"""
        holidays_list = sorted(holidays.country_holidays(country, years=year).keys())
        return holidays_list
