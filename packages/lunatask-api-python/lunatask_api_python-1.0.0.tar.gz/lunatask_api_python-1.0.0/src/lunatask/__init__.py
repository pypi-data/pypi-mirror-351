"""A Lunatask API for Python.

For additional details about Lunatask's API:
<https://lunatask.app/api/overview>

Example:
```py
import lunatask

LUNATASK_API_TOKEN = "your token goes here"

api = lunatask.api.LunataskAPI(LUNATASK_API_TOKEN)
result = api.ping()
```
"""
