import os
import itkdb
import jwt
import pandas as pd
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from .ReadSpec import getSpec, getSpecList

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

app = FastAPI()

# Model for authentication input
class AuthInput(BaseModel):
    access_code1: str = Field(default=None,examples=["access_code1"])
    access_code2: str = Field(default=None,examples=["access_code2"])

# Model for authentication output
class AuthOutput(BaseModel):
    access_token: str = Field(default=None,examples=["access_token"])
    token_type: str = Field(default="bearer",examples=["bearer"])

# Model for the input of parameters
class SpecDataInput(BaseModel):
    project: str = Field(default=None,examples=["P"])
    componentType: str = Field(default=None,examples=["PCB"])
    testType: str = Field(default=None,examples=["METROLOGY"])
    stage: str = Field(default=None,examples=["PCB_RECEPTION"])
    parameter: Optional[str] = Field(default=None,examples=["BOW1"])

# Model for the output of parameters
class SpecDataOutput(BaseModel):
    project: Optional[str] = None
    componentType: Optional[str] = None
    testType: Optional[str] = None
    stage: Optional[str] = None
    parameter: List[str] = None
    specList: Dict[str, Dict[str, Any]] = None
    

#################
### Functions ###
#################


def Authenticate(access_code1: str, access_code2: str):
    user = itkdb.core.User(access_code1=access_code1, access_code2=access_code2)
    try:
        user.authenticate()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="Authentication failed")
        return None
    return access_code1


def Create_Token(access_code1: str):
    expire = datetime.utcnow() + timedelta(minutes=os.getenv("TOKEN_DURATION"))
    payload = {
        "access_code1": access_code1,
        "exp": expire
    }
    
    token = jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
    return token


def get_api_key(authorization: str = Depends(api_key_header)):
    # Check if token is present in header (Authorization = Bearer <token>)
    if authorization is None:
        raise HTTPException(status_code=403, detail="No token")
    return authorization


#################
### ENDPOINTS ###
#################


### Redirect to swagger
@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")


### Authentication
@app.post("/auth")
async def auth(kwargs: AuthInput):
    kwargs_dict=kwargs.dict()

    # authenticate
    Authenticate(kwargs_dict["access_code1"], kwargs_dict["access_code2"])

    # create token
    token = Create_Token(kwargs_dict["access_code1"])

    # output structure
    output = AuthOutput(
        access_token=token,
        token_type="bearer"
    )

    return output


### Single specification retrieval
@app.post("/spec")
async def specRetrieval(kwargs: SpecDataInput, token: str = Depends(get_api_key)):
    kwargs_dict=kwargs.dict()
    
    # gatekeeping
    user = itkdb.core.User(access_code1=kwargs_dict["access_code1"], access_code2=kwargs_dict["access_code2"])
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        ac1: str = payload.get("access_code1")
        if ac1 is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="Authentication failed")
    
    # function
    query = getSpec(**kwargs_dict)

    # output structure
    output = SpecDataOutput(
        project=kwargs_dict["project"],
        componentType=kwargs_dict["componentType"],
        testType=kwargs_dict["testType"],
        stage=kwargs_dict["stage"],
        parameter=[query["parameter"]],
        specList={query["parameter"]:query["spec"]}
    )

    return output


### Multiple specifications retrieval
@app.post("/speclist")
async def specListRetrieval(kwargs: SpecDataInput, token: str = Depends(get_api_key)):
    kwargs_dict=kwargs.dict()

    # gatekeeping
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        ac1: str = payload.get("access_code1")
        if ac1 is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="Invalid token")

    # function
    query = getSpecList(**kwargs_dict)

    # output structure
    output = SpecDataOutput(
        project=kwargs_dict["project"],
        componentType=kwargs_dict["componentType"],
        testType=kwargs_dict["testType"],
        stage=kwargs_dict["stage"],
        parameter=query["parameter"],
        specList={x : y | {"associatedParam": []} for x, y in zip(query["parameter"], query["spec"])}
    )
    return output


# Example endpoint to read modules
@app.get("/modules")
def read_modules():
    csv_folder_path = "/spec_files"

    if not os.path.exists(csv_folder_path):
        raise HTTPException(status_code=404, detail="CSV files not found")
    try:
        df = pd.read_csv(csv_folder_path)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Example endpoint to read a specific module by ID
@app.get("/modules/{module_id}")
def read_module(module_id: int):
    # treating the module id input
    if module_id[-4:] != ".csv":
        module_id = module_id + ".csv"

    # csv file path if the working directory is the root of the project
    csv_file_path = f"/spec_files/{module_id}"

    if not os.path.exists(csv_file_path):
        raise HTTPException(status_code=404, detail="CSV file not found")
    try:
        df = pd.read_csv(csv_file_path)
        if module_id >= len(df) or module_id < 0:
            raise HTTPException(status_code=404, detail="Module ID not found")
        return df.iloc[module_id].to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


### Health check
@app.get("/health")
async def health_check():
    return {"status": "ok"}


### Help
@app.get("/help")
def help():
    return {
        "message": "Welcome to itk-spec",
        "endpoints": {
            "/spec": {
                "method": "POST",
                "description": "Get specification for a single parameter",
                "parameters": {
                    "project": "Project name",
                    "componentType": "Component type",
                    "testType": "Test type",
                    "stage": "Stage",
                    "parameter": "Parameter"
                }
            },
            "/speclist": {
                "method": "POST",
                "description": "Get specifications for multiple parameters",
                "parameters": {
                    "project": "Project name",
                    "componentType": "Component type",
                    "testType": "Test type",
                    "stage": "Stage",
                }
            },
            "/health": {
                "method": "GET",
                "description": "Check for API server status",
            },
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")