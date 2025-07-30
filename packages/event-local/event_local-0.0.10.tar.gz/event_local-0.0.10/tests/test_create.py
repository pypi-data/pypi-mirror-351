import json
from http import HTTPStatus

from python_sdk_remote.http_response import create_authorization_http_headers
from user_context_remote.user_context import UserContext

# Import the function to be tested
from src.handler import createHandler, getEventByEventIdHandler

user_jwt = UserContext().get_user_jwt()


class TestCreate:
    @staticmethod
    def test_create_valid_input():
        event = {
            "body": json.dumps(
                {
                    "location_id": 0,  # TODO: get_test_location_id
                    "organizers_profile_id": 2,
                    "website_url": "https://example.com",
                    "facebook_event_url": "https://facebook.com/event",
                    "meetup_event_url": "https://meetup.com/event",
                    "registration_url": "https://example.com/register",
                    "isTestData": True,
                    "end_timestamp": None,
                }
            ),
            "headers": create_authorization_http_headers(user_jwt),
        }

        # Call the function
        response = createHandler(event, None)

        # Assert that the response is correct
        assert response["statusCode"] == HTTPStatus.OK.value, response

        read_event = {
            "pathParameters": {"eventId": json.loads(response["body"])["event_id"]},
            "body": json.dumps({"isTestData": True}),
            "headers": create_authorization_http_headers(user_jwt),
        }
        read_response = getEventByEventIdHandler(read_event, None)
        assert read_response["statusCode"] == HTTPStatus.OK.value, read_response

    @staticmethod
    def test_create_invalid_input():
        # Define a mock event with invalid input data
        invalid_event = {
            "body": json.dumps(
                {
                    "location_id": -1,
                    "organizers_profile_id": 2,
                    "website_url": "invalid url",
                    "facebook_event_url": "https://facebook.com/event",
                    "meetup_event_url": "https://meetup.com/event",
                    "registration_url": "https://example.com/register",
                }
            ),
            "headers": create_authorization_http_headers(user_jwt),
        }
        event = invalid_event

        # Call the function
        response = createHandler(event, None)

        # Assert that the response is correct
        assert response["statusCode"] != HTTPStatus.OK.value, response
        assert (
            "Invalid location_id: -1 (type: <class 'int'>)" in response["body"]
        ), response

        # Assert that the cursor did not execute any SQL queries
        # self.mock_cursor.execute.assert_not_called()


if __name__ == "__main__":
    test = TestCreate()

    test.test_create_valid_input()
