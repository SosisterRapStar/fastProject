from typing import Union, Annotated

from fastapi import FastAPI, Path, Query, Body
from pydantic import BaseModel, Field
from enum import Enum



app = FastAPI()