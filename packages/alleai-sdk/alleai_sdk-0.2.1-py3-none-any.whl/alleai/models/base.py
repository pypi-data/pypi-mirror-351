from typing import Callable

class BaseModel:
    def __init__(self, make_request: Callable, requestFormData: Callable = None):
        self._make_request = make_request
        self._requestFormData = requestFormData
    

        
