# How to View MongoDB Database

## Method 1: Quick View Script (Recommended) ⭐

**Run this anytime to see all data:**
```bash
bash /app/scripts/view_database.sh
```

This shows:
- Database statistics (count of users, trips, itineraries)
- All users (name, email, ID)
- All trips (location, dates, type)
- All itineraries (summary)

---

## Method 2: Interactive MongoDB Shell

**Connect to database:**
```bash
mongosh mongodb://localhost:27017/test_database
```

**Once connected, run these commands:**

### View All Collections
```javascript
show collections
```

### View Users
```javascript
// All users (formatted)
db.users.find().pretty()

// Count users
db.users.countDocuments()

// Find specific user by email
db.users.findOne({email: "user@example.com"})

// Show only names and emails
db.users.find({}, {name: 1, email: 1, _id: 0}).pretty()
```

### View Trips
```javascript
// All trips
db.trips.find().pretty()

// Trips for specific user
db.trips.find({user_id: "USER_ID_HERE"}).pretty()

// Find trips by location
db.trips.find({location: /Paris/i}).pretty()

// Show only key fields
db.trips.find({}, {location: 1, trip_type: 1, trip_vibe: 1, _id: 0}).pretty()
```

### View Itineraries
```javascript
// All itineraries
db.itineraries.find().pretty()

// Specific itinerary
db.itineraries.findOne({trip_id: "TRIP_ID_HERE"})

// Count itineraries
db.itineraries.countDocuments()
```

### Exit MongoDB Shell
```javascript
exit
```

---

## Method 3: One-Line Commands

**Quick queries without entering shell:**

### View all users
```bash
mongosh mongodb://localhost:27017/test_database --quiet --eval "db.users.find().pretty()"
```

### View all trips
```bash
mongosh mongodb://localhost:27017/test_database --quiet --eval "db.trips.find().pretty()"
```

### Count documents
```bash
mongosh mongodb://localhost:27017/test_database --quiet --eval "
  console.log('Users: ' + db.users.countDocuments());
  console.log('Trips: ' + db.trips.countDocuments());
  console.log('Itineraries: ' + db.itineraries.countDocuments());
"
```

### View specific user's trips
```bash
mongosh mongodb://localhost:27017/test_database --quiet --eval "
  const user = db.users.findOne({email: 'user@example.com'});
  if (user) {
    console.log('User:', user.name);
    const trips = db.trips.find({user_id: user.id}).toArray();
    console.log('Trips:', JSON.stringify(trips, null, 2));
  }
"
```

---

## Method 4: Export Data to JSON Files

### Export all collections
```bash
# Export users
mongoexport --uri="mongodb://localhost:27017/test_database" --collection=users --out=/tmp/users.json --jsonArray --pretty

# Export trips
mongoexport --uri="mongodb://localhost:27017/test_database" --collection=trips --out=/tmp/trips.json --jsonArray --pretty

# Export itineraries
mongoexport --uri="mongodb://localhost:27017/test_database" --collection=itineraries --out=/tmp/itineraries.json --jsonArray --pretty

# View exported files
cat /tmp/users.json
cat /tmp/trips.json
cat /tmp/itineraries.json
```

---

## Method 5: Create Custom Query Scripts

### View specific user's complete data
```bash
mongosh mongodb://localhost:27017/test_database --quiet --eval "
  const email = 'user@example.com';
  const user = db.users.findOne({email: email}, {_id: 0});
  
  if (user) {
    console.log('=== USER ===');
    console.log(JSON.stringify(user, null, 2));
    
    const trips = db.trips.find({user_id: user.id}, {_id: 0}).toArray();
    console.log('\\n=== TRIPS (' + trips.length + ') ===');
    trips.forEach(trip => console.log(JSON.stringify(trip, null, 2)));
    
    const itineraries = db.itineraries.find({user_id: user.id}, {_id: 0}).toArray();
    console.log('\\n=== ITINERARIES (' + itineraries.length + ') ===');
    itineraries.forEach(it => console.log('Trip:', it.trip_id, '- Days:', it.itinerary_data.days.length));
  } else {
    console.log('User not found');
  }
"
```

### View detailed itinerary
```bash
mongosh mongodb://localhost:27017/test_database --quiet --eval "
  const itinerary = db.itineraries.findOne({}, {_id: 0});
  if (itinerary) {
    console.log('=== ITINERARY DETAILS ===');
    console.log('Trip ID:', itinerary.trip_id);
    console.log('Total Days:', itinerary.itinerary_data.days.length);
    console.log('\\nDay-by-Day Breakdown:');
    itinerary.itinerary_data.days.forEach(day => {
      console.log('\\n--- Day', day.day, '---');
      console.log('Date:', day.date || 'N/A');
      console.log('Activities:', day.activities.length);
      day.activities.forEach((activity, i) => {
        console.log('  ' + (i+1) + '.', activity.time, '-', activity.title);
      });
    });
  }
"
```

---

## Method 6: Using Python (Programmatic Access)

Create a script to query database:

```python
# /app/scripts/view_db.py
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import json

async def view_database():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.test_database
    
    print("=== USERS ===")
    users = await db.users.find({}, {"_id": 0}).to_list(100)
    print(json.dumps(users, indent=2, default=str))
    
    print("\n=== TRIPS ===")
    trips = await db.trips.find({}, {"_id": 0}).to_list(100)
    print(json.dumps(trips, indent=2, default=str))
    
    client.close()

asyncio.run(view_database())
```

Run it:
```bash
python /app/scripts/view_db.py
```

---

## Method 7: Via API (For Frontend Integration)

You already have these API endpoints:

```bash
# Get current user info (requires auth token)
curl -X GET "https://itinera-2.preview.emergentagent.com/api/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get all trips for logged-in user
curl -X GET "https://itinera-2.preview.emergentagent.com/api/trips" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get specific itinerary
curl -X GET "https://itinera-2.preview.emergentagent.com/api/trips/TRIP_ID/itinerary" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Method 8: Add Admin Dashboard (Optional)

Want a web UI to view database? I can create an admin page:
- View all users
- View all trips
- View all itineraries
- Search and filter
- Delete records

Just say "create admin dashboard" and I'll build it!

---

## Useful MongoDB Queries Cheatsheet

### Search
```javascript
// Case-insensitive search
db.users.find({name: /test/i})

// Multiple conditions
db.trips.find({trip_type: "solo", number_of_days: {$gte: 3}})

// Search by date range
db.trips.find({created_at: {$gte: "2026-01-01"}})
```

### Update
```javascript
// Update user name
db.users.updateOne({email: "user@example.com"}, {$set: {name: "New Name"}})

// Update trip
db.trips.updateOne({id: "TRIP_ID"}, {$set: {location: "New Location"}})
```

### Delete
```javascript
// Delete specific user
db.users.deleteOne({email: "user@example.com"})

// Delete all trips for a user
db.trips.deleteMany({user_id: "USER_ID"})

// Delete ALL data (careful!)
db.users.deleteMany({})
db.trips.deleteMany({})
db.itineraries.deleteMany({})
```

### Aggregation
```javascript
// Count trips per user
db.trips.aggregate([
  {$group: {_id: "$user_id", count: {$sum: 1}}},
  {$sort: {count: -1}}
])

// Most popular destinations
db.trips.aggregate([
  {$group: {_id: "$location", count: {$sum: 1}}},
  {$sort: {count: -1}},
  {$limit: 5}
])
```

---

## Quick Reference Card

| Task | Command |
|------|---------|
| View all data | `bash /app/scripts/view_database.sh` |
| Connect to DB | `mongosh mongodb://localhost:27017/test_database` |
| View users | `db.users.find().pretty()` |
| View trips | `db.trips.find().pretty()` |
| Count records | `db.users.countDocuments()` |
| Export to JSON | `mongoexport --uri="..." --collection=users --out=users.json` |
| Exit shell | `exit` |

---

## Database Location

- **Host**: localhost
- **Port**: 27017
- **Database Name**: test_database
- **Collections**: users, trips, itineraries

---

Need help with a specific query? Just ask!
