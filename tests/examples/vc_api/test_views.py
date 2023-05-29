import copy

import pytest

from vc_api.app import create_app
from vc_api.examples import ISSUE_CREDENTIAL_REQUEST, ISSUE_CREDENTIAL_RESPONSE


@pytest.mark.parametrize(
    "issuer",
    (
        pytest.param(
            None,
            marks=pytest.mark.xfail(
                reason="Does not support object type and oneOf of other (string) type",
                strict=True,
            ),
        ),
        {"id": "did:key:z6MkjRagNiMu91DduvCvgEsqLZDVzrJzFrwahc4tXLt9DoHd"},
    ),
)
async def test_issue_credential(aiohttp_client, issuer):
    """Should support credential issuer might as a string or an object."""
    # Prepare request & response data, by default use issuer as string
    request_data = copy.deepcopy(ISSUE_CREDENTIAL_REQUEST)
    response_data = copy.deepcopy(ISSUE_CREDENTIAL_RESPONSE)
    if issuer:
        request_data["credential"] |= {"issuer": issuer}
    response_data["verifiableCredential"] |= request_data["credential"]

    # Perform request and check that everything works well
    client = await aiohttp_client(create_app())
    response = await client.post(
        "/credentials/issue",
        json=request_data,
        headers={"Authorization": "Bearer XYZ"},
    )
    assert response.status == 201, await response.text()
    assert await response.json() == response_data
