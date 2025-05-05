from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from bson import ObjectId

from database import link_collection, link_helper
from models import LinkSchema, UpdateLinkModel, LinkDB

app = FastAPI()

# Add CORS middleware to allow frontend requests
origins = [
    "*", # Allow all origins for simplicity in development. Restrict in production.
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CRUD Operations ---

# CREATE
@app.post("/links/", response_description="Add new link", response_model=LinkDB)
async def create_link(link: LinkSchema = Body(...)):
    link_dict = jsonable_encoder(link)
    new_link = await link_collection.insert_one(link_dict)
    created_link = await link_collection.find_one({"_id": new_link.inserted_id})
    if created_link:
        return link_helper(created_link)
    raise HTTPException(status_code=400, detail="Link could not be created")

# READ (All)
@app.get("/links/", response_description="List all links", response_model=List[LinkDB])
async def list_links():
    links = []
    async for link in link_collection.find():
        links.append(link_helper(link))
    return links

# READ (Single) - Optional but good practice
@app.get("/links/{id}", response_description="Get a single link", response_model=LinkDB)
async def show_link(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail=f"Invalid ObjectId: {id}")
    link = await link_collection.find_one({"_id": ObjectId(id)})
    if link is not None:
        return link_helper(link)
    raise HTTPException(status_code=404, detail=f"Link {id} not found")

# UPDATE - Optional but good practice
@app.put("/links/{id}", response_description="Update a link", response_model=LinkDB)
async def update_link(id: str, link_data: UpdateLinkModel = Body(...)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail=f"Invalid ObjectId: {id}")

    link_update = {k: v for k, v in link_data.model_dump(exclude_unset=True).items() if v is not None}

    if len(link_update) >= 1:
        update_result = await link_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": link_update}
        )

        if update_result.modified_count == 1:
            updated_link = await link_collection.find_one({"_id": ObjectId(id)})
            if updated_link is not None:
                return link_helper(updated_link)

    # Check if the link exists even if no update was performed
    existing_link = await link_collection.find_one({"_id": ObjectId(id)})
    if existing_link is not None:
        return link_helper(existing_link) # Return existing if no update or data was same

    raise HTTPException(status_code=404, detail=f"Link {id} not found")

# DELETE - Optional but good practice
@app.delete("/links/{id}", response_description="Delete a link")
async def delete_link(id: str):
    # Print the ID for debugging
    print(f"Attempting to delete link with ID: {id}")
    
    try:
        # Check if the ID is a valid ObjectId
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail=f"Invalid ObjectId: {id}")
            
        # Find the link first to verify it exists
        link = await link_collection.find_one({"_id": ObjectId(id)})
        if link is None:
            raise HTTPException(status_code=404, detail=f"Link {id} not found")
            
        # Delete the link
        delete_result = await link_collection.delete_one({"_id": ObjectId(id)})
        print(f"Delete result: {delete_result.deleted_count} document(s) deleted")

        # Return a success response
        return {"message": f"Link with ID {id} deleted successfully"}
        
    except HTTPException as he:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise he
    except Exception as e:
        print(f"Error in delete_link: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Add a root endpoint for basic check
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Link API"}


