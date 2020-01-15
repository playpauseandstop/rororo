import logging

from aiohttp import web

from rororo import openapi_context, OperationTableDef
from .data import NewPet
from .shortcuts import get_pet_or_404


logger = logging.getLogger(__name__)

# ``OperationTableDef`` is analogue of ``web.RouteTableDef`` but for OpenAPI
# operation handlers
operations = OperationTableDef()


@operations.register("addPet")
async def create_pet(request: web.Request) -> web.Response:
    with openapi_context(request) as context:
        new_pet = NewPet(
            name=context.data["name"], tag=context.data.get("tag")
        )

        pet = new_pet.to_pet(len(request.app["pets"]) + 1)
        request.app["pets"].append(pet)

        return web.json_response(pet.to_dict())


@operations.register("deletePet")
async def delete_pet(request: web.Request) -> web.Response:
    with openapi_context(request) as context:
        pet = get_pet_or_404(
            request.app["pets"], context.parameters.path["id"]
        )
        request.app["pets"] = [
            item for item in request.app["pets"] if item != pet
        ]
        return web.json_response(status=204)


@operations.register("findPets")
async def list_pets(request: web.Request) -> web.Response:
    with openapi_context(request) as context:
        limit = context.parameters.query.get("limit")
        tags = set(context.parameters.query.get("pets") or [])

        found = [
            item
            for item in request.app["pets"]
            if not tags or (tags and item.tag in tags)
        ]

        return web.json_response([item.to_dict() for item in found[:limit]])


@operations.register("find pet by id")
async def retrieve_pet(request: web.Request) -> web.Response:
    with openapi_context(request) as context:
        pet = get_pet_or_404(
            request.app["pets"], context.parameters.path["id"]
        )
        return web.json_response(pet.to_dict())
