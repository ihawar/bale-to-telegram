from tortoise import Tortoise

async def run(path: str):
    TORTOISE_ORM = {
    "connections": {
        "default": f"sqlite://{path}",
    },
    "apps": {
        "models": {
            "models": ["db.models"],
            "default_connection": "default",
            "migrations": "db.migrations",
        },
    },
}
    context = await Tortoise.init(
        TORTOISE_ORM
    )
    await Tortoise.generate_schemas()

    return context
