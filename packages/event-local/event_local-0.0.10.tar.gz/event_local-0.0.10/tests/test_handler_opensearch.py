from src.handler import getEventsFromOpensearch
from tests.opensearch_queries import (
    opensearch_query1, opensearch_query2, opensearch_query3, opensearch_query4, opensearch_query5,
    opensearch_query6, opensearch_query7, opensearch_query8, opensearch_query9, opensearch_query10,
)

queries = [
    opensearch_query1, opensearch_query2, opensearch_query3, opensearch_query4, opensearch_query5,
    opensearch_query6, opensearch_query7, opensearch_query8, opensearch_query9, opensearch_query10,
]


def test_get_events_from_opensearch():
    request_parameters = {
        "langCode": "en",
        "limit": 10,
        "isTestData": True,
    }

    responses = []

    for opensearch_query in queries:

        response = getEventsFromOpensearch(request_parameters, opensearch_query['query'])

        assert response is not None
        assert response["_shards"]["failed"] == 0
        assert response["_shards"]["successful"] > 0
        assert response["_shards"]["total"] == response["_shards"]["successful"] + response["_shards"]["failed"]

        responses.append(response)

    # print(response)

    assert responses[0]["_shards"]["failed"] == 0
    assert responses[0]["_shards"]["successful"] > 0
    assert responses[0]["_shards"]["total"] == response["_shards"]["successful"] + response["_shards"]["failed"]


if __name__ == "__main__":
    test_get_events_from_opensearch()
