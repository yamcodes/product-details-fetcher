# TODO: add DB
# TODO: create a separate get function for a product and use it in favorites PUT
# TODO: favorites GET
# TODO: determine whether to use source in favorites or not
0
from sanic import Sanic
from sanic.response import json
from enum import Enum
import requests

app = Sanic(__name__)
token = "yblyamb829aljfy59"

data = {"details": [], "favorites": {}}

@app.put("/details/<source:(amazon|walmart)>/<source_id:str>")
async def hello_world(request, source, source_id):
    response = requests.get(f"https://ebazon-prod.herokuapp.com/ybl_assignment/{source}/{source_id}/{token}")
    res = response.json()
    try:  res_data = res["data"]
    except KeyError: return json({"description": "Invalid ID", "message": f"Requested ID {source_id} not found"}, status=404)
    res_title = res_data["title"]
    res_price = res_data["price"]
    item = {
        "source_id": source_id,
        "title": res_title,
        "price": res_price,
        "source": source,
    }
    status = 200
    # check if item id already exists in the data list
    if source_id in [e["source_id"] for e in data["details"]]:
        res["description"] = "Product Already Exists"
        res["message"] = f"Product with ID {source_id} already exists"
        status = 409
    else:
        data["details"].append(item)
        res["description"] = "Successfuly Added Product"
        res["message"] = f"Product with ID {source_id} added"
    return json(res, status=status)

@app.get("/details")
async def get_details(request):
    return json(data["details"])

@app.put("/favorites/<source_id:str>")
async def add_to_favorites(request,source_id):
    # get email from request header
    email = request.headers.get("email")
    # check if id exists in data["details"]
    item = None
    for e in data["details"]:
        if source_id == e["source_id"]:
            item = e
            break
    if item is None: return json({"description": "Invalid ID", "message": f"Requested ID {source_id} not found"}, status=404)
    if email not in data["favorites"]: data["favorites"][email] = []
    status = 200
    res = {"favorites": data["favorites"][email]}
    item = {
        "source_id": source_id,
        "source": item["source"],
        "title": item["title"],
        "price": item["price"]
    }
    if source_id in [e["source_id"] for e in data["favorites"][email]]: 
        status = 409
        res["description"] = "Product Already in Favorites"
        res["message"] = f"Product with ID {source_id} already exists in favorites"
    else:
        data["favorites"][email].append(item)
        res["description"] = "Successfuly Added to Favorites"
        res["message"] = f"Product with ID {source_id} added to favorites"
    return json(res,status=status)