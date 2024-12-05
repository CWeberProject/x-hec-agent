import os
from typing import Union
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from dotenv import load_dotenv
import phospho
from mistralai import Mistral

api_key = os.environ["MISTRAL_API_KEY"]
model = "pixtral-12b-latest"

client = Mistral(api_key)
app = FastAPI()

phospho.init(
    api_key=os.getenv("PHOSPHO_API_KEY"), 
    project_id="9c2b674fd8eb4db2a6b15309af2b0ade"
)

bearer = HTTPBearer()

def get_api_key(authorization: HTTPAuthorizationCredentials = Depends(bearer)) -> str:
    # Parse credentials
    api_key_token = authorization.credentials

    if api_key_token != os.getenv("MY_SECRET_KEY"):
        raise HTTPException(status_code=401, detail="Invalid token")

class Message(BaseModel):
    message: str

@app.get("/")
def read_root():
    return {"Hello": "PLB!"}

@app.post("/message")
def send_message(request: Message):
    messages = [
        {
                "type": "text",
                "text": request.message
            },
            {
                "type": "image_url",
                "image_url": "https://media.licdn.com/dms/image/v2/D4E03AQGfDYTXsA2KXA/profile-displayphoto-shrink_800_800/profile-displayphoto-shrink_800_800/0/1726654931091?e=1738800000&v=beta&t=HR1psPvn7_W3Z1QeZNCFgYLyUtSDdNYkDzJdFcfA3i0"
            }
    ]
    
    completion = client.chat.complete(
        model=model,
        messages=messages
    )
    
    answer = completion.choices[0].message.content
    phospho.log(input=request.message, output=answer)
    return {"answer": answer}

@app.post("/message-secure")
def send_message_secure(request: Message, api_key: str = Depends(get_api_key)):
    messages = [
        {"role": "system", "content": "You are Bruno Martinaud. Talk about your experience with OpenAI."},
        {"role": "user", "content": request.message}
    ]
    
    completion = client.chat.complete(
        model=model,
        messages=messages
    )
    
    answer = completion.choices[0].message.content
    return {"answer": answer}
