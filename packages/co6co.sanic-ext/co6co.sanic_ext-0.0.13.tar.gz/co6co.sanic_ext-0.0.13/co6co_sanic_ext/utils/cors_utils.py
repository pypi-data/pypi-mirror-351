
from sanic_ext import Extend
from sanic import Sanic
import os
from typing import List
try:
    from co6co_sanic_ext.cors import CORS  # The typical way to import sanic-cors
except ImportError:
    # Path hack allows examples to be run without installation.
    import os
    parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
    os.sys.path.insert(0, parentdir)
    from co6co_sanic_ext.cors import CORS

def attach_cors(app:Sanic,resoutce:str=r"/v1/*",methods:List[str]=["GET", "POST", "HEAD", "OPTIONS","DELETE","PATCH","PUT"]):
    #跨域
    """
    POST	Create	        201 (Created),              'Location' header with link to /customers/{id} containing new ID.	404 (Not Found), 409 (Conflict) if resource already exists..
    GET	    Read	        200 (OK),                    list of customers. Use pagination, sorting and filtering to navigate big lists.	200 (OK), single customer. 404 (Not Found), if ID not found or invalid.
    PUT	    Update/Replace	405 (Method Not Allowed),    unless you want to update/replace every resource in the entire collection.	200 (OK) or 204 (No Content). 404 (Not Found), if ID not found or invalid.
    PATCH	Update/Modify	405 (Method Not Allowed),    unless you want to modify the collection itself.	200 (OK) or 204 (No Content). 404 (Not Found), if ID not found or invalid.
    DELETE	Delete	        405 (Method Not Allowed),    unless you want to delete the whole collection—not often desirable.	200 (OK). 404 (Not Found), if ID not found or invalid.
    """
    CORS_OPTIONS = {"resources": resoutce, "origins": "*", "methods": methods} 
    Extend(app, extensions=[CORS], config={"CORS": False, "CORS_OPTIONS": CORS_OPTIONS})

