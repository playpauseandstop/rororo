import dataclasses

from aiohttp import web
from aiohttp_middlewares.error import error_context

from rororo import openapi_context, OperationTableDef
from .data import NewPet
from .shortcuts import get_pet_or_404


# Instead of using ``web.RouteTableDef`` or similar routing solutions
operations = OperationTableDef()


@operations.register("createPets")
async def create_pet(request: web.Request) -> web.Response:
    with openapi_context(request) as context:
        new_pet = NewPet(
            name=context.data["name"], tag=context.data.get("tag")
        )
        pet = new_pet.to_pet(len(request.app["tags"]) + 1)
        request.app["tags"].append(pet)

    return web.json_response(dataclasses.asdict(pet))


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


async def error(request: web.Request) -> web.Response:
    with error_context(request) as context:
        return web.json_response(
            {"code": context.status, "message": context.message},
            status=context.status,
        )


@operations.register("findPets")
async def list_pets(request: web.Request) -> web.Response:
    with openapi_context(request) as context:
        limit = context.parameters.query.get("limit")
        tags = set(context.parameters.query.get("tags") or [])

        found = [
            item
            for item in request.app["pets"]
            if not tags or (tags and item.tag in tags)
        ]

        return web.json_response(
            [dataclasses.asdict(item) for item in found[:limit]]
        )


@operations.register("find pet by id")
async def retrieve_pet(request: web.Request) -> web.Response:
    with openapi_context(request) as context:
        pet = get_pet_or_404(
            request.app["pets"], context.parameters.path["id"]
        )
        return web.json_response(dataclasses.asdict(pet))
