from aiohttp import web
from vc_api.examples import ISSUE_CREDENTIAL_RESPONSE

from rororo import OperationTableDef


operations = OperationTableDef()


@operations.register("issueCredential")
async def issue_credential(request: web.Request) -> web.Response:
    """Issues a credential and returns it in the response body."""
    return web.json_response(ISSUE_CREDENTIAL_RESPONSE, status=201)
