# MongoDB library

Sync:
- https://pypi.org/project/pymongo/
- https://www.mongodb.com/resources/languages/pymongo-tutorial (coding practices are not the best but API examples are good)

Async:
- Adding async: https://www.mongodb.com/docs/languages/python/pymongo-driver/current/reference/migration/#migrate-from-pymongo
- Async reference API: https://pymongo.readthedocs.io/en/4.19.0/api/pymongo/asynchronous/index.html
    - https://pymongo.readthedocs.io/en/4.19.0/api/pymongo/asynchronous/mongo_client.html
- Async tutorial: https://www.mongodb.com/docs/languages/python/pymongo-driver/current/integrations/fastapi-integration/

Databases and collections are created automatically when finding, inserting, etc.

Testing:
- https://fastapi.tiangolo.com/tutorial/testing/#using-testclient
- https://fastapi.tiangolo.com/advanced/async-tests/
- https://anyio.readthedocs.io/en/stable/testing.html
- https://github.com/florimondmanca/asgi-lifespan#usage
- https://docs.pytest.org/en/stable/how-to/fixtures.html

Run tests (inside container):
```bash
uv run pytest
```