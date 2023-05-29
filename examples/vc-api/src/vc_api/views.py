import copy

from aiohttp import web
from pyrsistent import thaw

from rororo import get_validated_data, OperationTableDef
from vc_api.examples import ISSUE_CREDENTIAL_RESPONSE


operations = OperationTableDef()


@operations.register("issueCredential")
async def issue_credential(request: web.Request) -> web.Response:
    """Issues a credential and returns it in the response body."""
    request_data = get_validated_data(request)

    response_data = copy.deepcopy(ISSUE_CREDENTIAL_RESPONSE)
    response_data["verifiableCredential"].update(
        thaw(request_data["credential"])
    )

    return web.json_response(response_data, status=201)
