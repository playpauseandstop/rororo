from vc_api.app import create_app
from vc_api.examples import ISSUE_CREDENTIAL_REQUEST, ISSUE_CREDENTIAL_RESPONSE


async def test_issue_credential(aiohttp_client):
    client = await aiohttp_client(create_app())
    response = await client.post(
        "/credentials/issue",
        json=ISSUE_CREDENTIAL_REQUEST,
        headers={"Authorization": "Bearer XYZ"},
    )
    assert response.status == 201, await response.text()
    assert await response.json() == ISSUE_CREDENTIAL_RESPONSE
