from src.events_local import EventsLocal
from src.event import Event
from opensearch_local.our_opensearch import OurOpenSearch


# https://opensearch.play1.circ.zone:5601/app/login?
def test_foreach():

    open_search_ingester = OurOpenSearch(buffer_size=5)

    # where = "is_test_data = 1"
    where = "event_id = 1345"
    limit = 10
    function = open_search_ingester.insert

    events_local = EventsLocal(is_test_data=True)

    index_name = "event"

    # select_function = events_local.get_values_dict_list
    select_function = events_local.get_values_dict_list_by_where

    # responses_dict = events_local.foreach(where, limit, function, id_column_name="event_id", index_name=index_name)
    responses_dict = events_local.foreach(where, limit, function, id_column_name="event_id", select_function=select_function, index_name=index_name)

    print(responses_dict, "\n")

    body = {
        "query": {
            "match": {
                "is_test_data": "true"
            }
        }
    }

    # The qeury for the dev tool in dashboard:
    # GET event/_search
    # {
    # "query": {
    #     "match": {
    #     "is_test_data": "true"
    #     }
    # }
    # }

    search_response = open_search_ingester.search(index=index_name, body=body)

    print(search_response)


def test_to_json_from_db():
    events_local = EventsLocal()

    result = events_local.select_by_event_id(202408182100165)
    # result = events_local.select_one_dict_by_where()

    print(result)

    event_one = Event(**result)

    print(event_one)

    assert event_one.get("event_id") == result["event_id"]

    event_json = event_one.to_json_dict()

    assert event_json["kwargs"]["event_id"] == int(result["event_id"])
    assert event_json["kwargs"]["website_url"] == result["website_url"]
    assert event_json["kwargs"]["facebook_event_url"] == result["facebook_event_url"]
    assert event_json["kwargs"]["meetup_event_url"] == result["meetup_event_url"]


if __name__ == '__main__':
    # test_foreach()
    test_to_json_from_db()
