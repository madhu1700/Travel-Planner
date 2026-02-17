from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Literal
import uuid
from datetime import datetime, timezone, timedelta
import jwt
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json
from passlib.context import CryptContext

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

JWT_SECRET = os.environ.get('JWT_SECRET', 'travel_planner_secret_key')
JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
JWT_EXPIRATION_HOURS = int(os.environ.get('JWT_EXPIRATION_HOURS', 720))

security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    password_hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserRegister(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TripCriteria(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    location: str
    time_of_arrival: str
    time_of_departure: str
    location_of_stay: str
    check_in_datetime: str
    check_out_datetime: str
    number_of_days: int
    trip_type: Literal["friends", "family", "solo", "couple"]
    trip_vibe: Literal["relaxing", "adventurous", "party", "cultural", "nature", "mix"]
    hectic_level: Literal["very_relaxed", "moderately_relaxed", "moderate", "medium_to_high", "very_hectic"]
    places_preference: Literal["mainstream", "hidden_gems", "balanced"]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TripCriteriaCreate(BaseModel):
    location: str
    time_of_arrival: str
    time_of_departure: str
    location_of_stay: str
    check_in_datetime: str
    check_out_datetime: str
    number_of_days: int
    trip_type: Literal["friends", "family", "solo", "couple"]
    trip_vibe: Literal["relaxing", "adventurous", "party", "cultural", "nature", "mix"]
    hectic_level: Literal["very_relaxed", "moderately_relaxed", "moderate", "medium_to_high", "very_hectic"]
    places_preference: Literal["mainstream", "hidden_gems", "balanced"]

class Itinerary(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trip_id: str
    user_id: str
    itinerary_data: dict
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TokenResponse(BaseModel):
    token: str
    user: dict

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_jwt_token(user_data: dict) -> str:
    payload = {
        'user_id': user_data['id'],
        'email': user_data['email'],
        'exp': datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_jwt_token(token)
    user = await db.users.find_one({'id': payload['user_id']}, {'_id': 0})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    existing_user = await db.users.find_one({'email': user_data.email}, {'_id': 0})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    password_hash = hash_password(user_data.password)
    user_obj = User(
        email=user_data.email,
        name=user_data.name,
        password_hash=password_hash
    )
    
    user_dict = user_obj.model_dump()
    user_dict['created_at'] = user_dict['created_at'].isoformat()
    
    await db.users.insert_one(user_dict)
    
    token = create_jwt_token({
        'id': user_obj.id,
        'email': user_obj.email
    })
    
    return TokenResponse(
        token=token,
        user={
            'id': user_obj.id,
            'email': user_obj.email,
            'name': user_obj.name
        }
    )

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user = await db.users.find_one({'email': credentials.email}, {'_id': 0})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(credentials.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_jwt_token({
        'id': user['id'],
        'email': user['email']
    })
    
    return TokenResponse(
        token=token,
        user={
            'id': user['id'],
            'email': user['email'],
            'name': user['name']
        }
    )

@api_router.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        'id': current_user['id'],
        'email': current_user['email'],
        'name': current_user['name']
    }

@api_router.post("/trips", response_model=TripCriteria)
async def create_trip(trip_data: TripCriteriaCreate, current_user: dict = Depends(get_current_user)):
    trip_dict = trip_data.model_dump()
    trip_obj = TripCriteria(**trip_dict, user_id=current_user['id'])
    
    doc = trip_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.trips.insert_one(doc)
    return trip_obj

@api_router.get("/trips", response_model=List[TripCriteria])
async def get_trips(current_user: dict = Depends(get_current_user)):
    trips = await db.trips.find({'user_id': current_user['id']}, {'_id': 0}).to_list(100)
    for trip in trips:
        if isinstance(trip['created_at'], str):
            trip['created_at'] = datetime.fromisoformat(trip['created_at'])
    return trips

@api_router.post("/trips/{trip_id}/generate-itinerary")
async def generate_itinerary(trip_id: str, current_user: dict = Depends(get_current_user)):
    trip = await db.trips.find_one({'id': trip_id, 'user_id': current_user['id']}, {'_id': 0})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    try:
        chat = LlmChat(
            api_key=os.environ.get('EMERGENT_LLM_KEY'),
            session_id=f"itinerary_{trip_id}",
            system_message="You are an expert travel planner. Generate detailed, realistic day-wise travel itineraries based on user preferences."
        )
        chat.with_model("openai", "gpt-5.2")
        
        prompt = f"""
Create a detailed {trip['number_of_days']}-day travel itinerary for {trip['location']} with the following criteria:

- Arrival: {trip['time_of_arrival']}
- Departure: {trip['time_of_departure']}
- Staying at: {trip['location_of_stay']}
- Check-in: {trip['check_in_datetime']}
- Check-out: {trip['check_out_datetime']}
- Trip type: {trip['trip_type']}
- Trip vibe: {trip['trip_vibe']}
- Hectic level: {trip['hectic_level']}
- Places preference: {trip['places_preference']}

Generate a JSON response with the following structure:
{{
  "days": [
    {{
      "day": 1,
      "date": "Day 1",
      "activities": [
        {{
          "time": "Morning (8:00 AM - 12:00 PM)",
          "title": "Activity title",
          "description": "Detailed description",
          "travel_time": "15 minutes from hotel",
          "tips": "Helpful tips"
        }}
      ]
    }}
  ]
}}

Ensure the itinerary:
1. Respects arrival and departure times
2. Matches the hectic level (more rest for relaxed, packed for hectic)
3. Aligns with trip type (family-friendly, adventurous for friends, romantic for couples, flexible for solo)
4. Reflects the vibe preference
5. Includes realistic travel times
6. Has food recommendations
7. Considers check-in/check-out times

Respond ONLY with valid JSON, no markdown or extra text.
"""
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        try:
            itinerary_data = json.loads(response)
        except json.JSONDecodeError:
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            itinerary_data = json.loads(cleaned_response.strip())
        
        itinerary_obj = Itinerary(
            trip_id=trip_id,
            user_id=current_user['id'],
            itinerary_data=itinerary_data
        )
        
        doc = itinerary_obj.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        
        await db.itineraries.insert_one(doc)
        
        return {
            'id': itinerary_obj.id,
            'trip_id': trip_id,
            'itinerary': itinerary_data
        }
        
    except Exception as e:
        logging.error(f"Error generating itinerary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate itinerary: {str(e)}")

@api_router.get("/trips/{trip_id}/itinerary")
async def get_itinerary(trip_id: str, current_user: dict = Depends(get_current_user)):
    itinerary = await db.itineraries.find_one(
        {'trip_id': trip_id, 'user_id': current_user['id']},
        {'_id': 0}
    )
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    return itinerary

app.include_router(api_router)

app.add_middleware(SessionMiddleware, secret_key=JWT_SECRET)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()