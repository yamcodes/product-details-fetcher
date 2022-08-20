# Assumption: walmart and amazon have unique ID's (no ID is shared)
# Potential improvement: use class based views to group same-endpoint functionality

from sanic import Sanic
from sanic.response import json
import requests
import json as json_lib
import aiohttp
from models import Details, Favorites
from tortoise.contrib.sanic import register_tortoise

app = Sanic(__name__)
token = "yblyamb829aljfy59"
data = {"details": [], "favorites": {}}


@app.get("/details")
async def get_all_product_details(request):
    return json(await Details.all().values("source_id", "source", "title", "price"))

@app.get("/details/<source:(amazon|walmart)>/<source_id:str>")
async def get_product_details(request, source, source_id):
    # asynchronously get product details from source
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://ebazon-prod.herokuapp.com/ybl_assignment/{source}/{source_id}/{token}") as response:
            res_json = await response.json()
            try:  return json(res_json["data"])
            except KeyError: return json({"description": "Invalid ID", "message": f"Requested ID {source_id} not found"}, status=404)
            
@app.put("/details/<source:(amazon|walmart)>/<source_id:str>")
async def add_product_details(request, source, source_id):
    # get product details
    res = await get_product_details(request, source, source_id)
    # return error if product not found
    if res.status<200 or res.status>=300: return res
    # otherwise, add product
    # response body from bytes to string to json
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
        # add product details to database
        try:
            await Details.create(source_id=source_id, source=source, title=res_title, price=res_price)
            res["description"] = "Successfuly Added Product"
            res["message"] = f"Product with ID {source_id} added"
        # TODO: add error handling for IntegrityError
        except:
            res["description"] = "Product Already Exists"
            res["message"] = f"Product with ID {source_id} already exists"
            status = 409
        data["details"].append({
            "source_id": source_id,
            "title": res_title,
            "price": res_price,
            "source": source,
        })
    return json(res, status=status)

@app.put("/favorites/<source_id:str>")
async def add_to_favorites(request,source_id):
    # get email from request header
    email = request.headers.get("email")
    
    # get favorites from database
    favorites = await Favorites.filter(email=email).values("product__source_id", "product__source", "product__title", "product__price")
    if (await Favorites.filter(email=email, product_id=source_id).first()) is not None:
        return json({"favorites": favorites, "description": "Product Already Exists", "message": f"Product with ID {source_id} already exists in {email}'s favorites"}, status=409)
    try: await Favorites.create(email=email,product_id=source_id)
    # TODO: add error handling for IntegrityError
    except: 
        return json({"description": "Error Adding Product", "message": f"Product with ID {source_id} cannot be added to {email}'s favorites, try adding it to the database first"}, status=404)
    # update favorites list with new product TODO: instead of fetching all the data again, just add the new product to the list
    favorites = await Favorites.filter(email=email).values("product__source_id", "product__source", "product__title", "product__price")
    return json({"favorites": favorites, "description": "Successfuly Added Product", "message": f"Product with ID {source_id} added to favorites"}, status=200)

# connect to sql db
register_tortoise(
    app, db_url=r"sqlite://products.db", modules={"models": ["models"]}, generate_schemas=True
)