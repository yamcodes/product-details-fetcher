# TODO: add DB
# Assumption: walmart and amazon have unique ID's (no ID is shared)
# Potential improvement: use class based views to group same-endpoint functionality
# TODO: update requirements.txt

from sanic import Sanic
from sanic.response import json
import requests
import json as json_lib
import aiohttp

app = Sanic(__name__)
token = "yblyamb829aljfy59"
data = {"details": [], "favorites": {}}

@app.get("/details")
async def get_all_product_details(request):
    return json(data["details"])

@app.get("/details/<source:(amazon|walmart)>/<source_id:str>")
async def get_product_details(request, source, source_id):
    # asynchronously get product details from source
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://ebazon-prod.herokuapp.com/ybl_assignment/{source}/{source_id}/{token}") as response:
            res_json = await response.json()
            try:  return json(res_json["data"])
            except KeyError: return json({"description": "Invalid ID", "message": f"Requested ID {source_id} not found"}, status=404)
            
@app.put("/details/<source:(amazon|walmart)>/<source_id:str>")
async def add_product(request, source, source_id):
    # get product details
    res = await get_product(request, source, source_id)
    # return error if product not found
    if res.status<200 or res.status>=300: return res
    # otherwise, add product
    res_data = json_lib.loads(res.body.decode('utf-8'))
    res_title = res_data["title"]
    res_price = res_data["price"]
    status = 200
    
    # spin up a dictionary based on the res_data, to add a description and a message and return it
    res = {"data": res_data}
    # check if item id already exists in the data list and return an appropriate message
    if source_id in [e["source_id"] for e in data["details"]]:
        res["description"] = "Product Already Exists"
        res["message"] = f"Product with ID {source_id} already exists"
        status = 409
    else:
        data["details"].append({
            "source_id": source_id,
            "title": res_title,
            "price": res_price,
            "source": source,
        })
        res["description"] = "Successfuly Added Product"
        res["message"] = f"Product with ID {source_id} added"
    return json(res, status=status)

@app.put("/favorites/<source_id:str>")
async def add_to_favorites(request,source_id):
    # get email from request header
    email = request.headers.get("email")
    # check if id exists in data["details"]. If not, return error
    item = None
    for e in data["details"]:
        if source_id == e["source_id"]:
            item = e
            break
    if item is None: return json({"description": "Invalid ID", "message": f"Requested ID {source_id} not found"}, status=404)
    # check if email exists in data["favorites"]. If not, create a new entry in data["favorites"]
    if email not in data["favorites"]: data["favorites"][email] = []
    status = 200
    res = {"details": data["favorites"][email]}
    # check if item id already exists in the user's favorites list and return an appropriate message
    if source_id in [e["source_id"] for e in data["favorites"][email]]: 
        status = 409
        res["description"] = "Product Already in Favorites"
        res["message"] = f"Product with ID {source_id} already exists in favorites"
    else:
        data["favorites"][email].append({
            "source_id": source_id,
            "source": item["source"],
            "title": item["title"],
            "price": item["price"]
        })
        res["description"] = "Successfuly Added to Favorites"
        res["message"] = f"Product with ID {source_id} added to favorites"
    return json(res,status=status)