import unittest
import json
from http import HTTPStatus
from python_sdk_remote.http_response import create_authorization_http_headers
from user_context_remote.user_context import UserContext
# from language_remote import lang_code

from src.handler import getEventByEventIdHandler, EventsLocal


user_jwt = UserContext().get_user_jwt()


class TestRead(unittest.TestCase):
    def test_read_valid_input(self):
        # Set up the mock event and connection
        event = {  # TODO Please make sure it will work in any database/environment
            "pathParameters": {
                "eventId": EventsLocal().get_test_event_id(),
            },
            "headers": create_authorization_http_headers(user_jwt),
        }

        # Call the function
        response = getEventByEventIdHandler(event, None)

        # Assert that the response is correct
        assert response["statusCode"] == HTTPStatus.OK.value, response
        select_clause = "event_id, location_id, organizers_profile_id, website_url, facebook_event_url, meetup_event_url, registration_url"
        assert all(
            key in json.loads(response["body"]) for key in select_clause.split(", ")
        ), response

    def test_read_invalid_event_id(self):
        # Define a mock event with an invalid event ID
        invalid_event = {
            "pathParameters": {"eventId": "invalid"},
            "headers": create_authorization_http_headers(user_jwt),
        }

        # Call the function
        response = getEventByEventIdHandler(invalid_event, None)

        # Assert that the response is correct
        # TODO change Magic number to enum/const
        assert response["statusCode"] != HTTPStatus.OK.value
        assert "Invalid event_id: invalid" in response["body"]

    def test_read_event_not_found(self):
        # Set up the mock event and connection
        event = {
            "pathParameters": {"eventId": "0"},
            "headers": create_authorization_http_headers(user_jwt),
        }

        # Call the function
        response = getEventByEventIdHandler(event, None)

        # Assert that the response is correct
        assert response["statusCode"] != HTTPStatus.OK.value, response
        assert "error" in response["body"], response

    @staticmethod
    def test_get_number_of_events():
        events_local = EventsLocal()
        current_number_of_events = events_local.get_number_of_events()
        sql_statement = "SELECT COUNT(*) FROM event.event_view"
        events_local.cursor.execute(sql_statement=sql_statement)
        number_of_events_from_sql = events_local.cursor.fetchone()[0]
        assert current_number_of_events == number_of_events_from_sql


# Call
if __name__ == "__main__":
    unittest.main()

# test_read1=test_read()
# test_read1.setUp()
# test_read1.test_read_valid_input()
