import json
from http import HTTPStatus

from python_sdk_remote.http_response import create_authorization_http_headers
from user_context_remote.user_context import UserContext

from src.events_local import EventsLocal
from src.handler import updateHandler

user_jwt = UserContext().get_user_jwt()


class TestUpdate:
    @staticmethod
    def test_update_valid_input():
        event = {
            "pathParameters": {"eventId": EventsLocal().get_test_event_id()},
            "body": json.dumps(
                {
                    "location_id": 2,  # TODO: get test id everywhere.
                    "organizers_profile_id": 2,
                    "website_url": "https://example.com",
                    "facebook_event_url": "https://facebook.com/event",
                    "meetup_event_url": "https://meetup.com/event",
                    "registration_url": "https://example.com/register",
                }
            ),
            "headers": create_authorization_http_headers(user_jwt),
        }

        # Call the function
        response = updateHandler(event, None)

        # Assert that the response is correct
        assert response["statusCode"] == HTTPStatus.OK.value
        assert response["body"] == json.dumps({"message": "Event updated successfully"})

        # Ensure error without headers
        event.pop("headers")
        response = updateHandler(event, None)
        assert response["statusCode"] == HTTPStatus.OK.value, response

    @staticmethod
    def test_update_invalid_input():
        # Define a mock event with invalid input data
        invalid_event = {
            "pathParameters": {"eventId": "1"},
            "body": json.dumps(
                {
                    "location_id": 0,
                    "organizers_profile_id": 2,
                    "website_url": "invalid url",
                    "facebook_event_url": "https://facebook.com/event",
                    "meetup_event_url": "https://meetup.com/event",
                    "registration_url": "https://example.com/register",
                }
            ),
        }
        # Call the function
        response = updateHandler(invalid_event, None)

        # Assert that the response is correct
        assert response["statusCode"] != HTTPStatus.OK.value
        assert "error" in response["body"]


if __name__ == "__main__":
    test = TestUpdate()
    test.test_update_valid_input()
    # test.test_update_invalid_input()
