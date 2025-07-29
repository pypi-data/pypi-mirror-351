import json


async def test_get_example(jp_fetch):
    # When
    response = await jp_fetch("contentgen", "get-example")

    # Then
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == {
        "data": "This is /contentgen/get-example endpoint!"
    }