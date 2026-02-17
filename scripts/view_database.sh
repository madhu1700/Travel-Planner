#!/bin/bash
# MongoDB Database Viewer Script
# Usage: bash /app/scripts/view_database.sh

echo "=========================================="
echo "   TRAVEL PLANNER DATABASE VIEWER"
echo "=========================================="
echo ""

# Database connection
DB_URI="mongodb://localhost:27017/test_database"

echo "📊 DATABASE STATISTICS"
echo "----------------------------------------"
mongosh $DB_URI --quiet --eval "
  console.log('Database: test_database');
  console.log('Users: ' + db.users.countDocuments());
  console.log('Trips: ' + db.trips.countDocuments());
  console.log('Itineraries: ' + db.itineraries.countDocuments());
"

echo ""
echo "👥 ALL USERS"
echo "----------------------------------------"
mongosh $DB_URI --quiet --eval "
  db.users.find({}).forEach(user => {
    console.log('---');
    console.log('ID: ' + user.id);
    console.log('Name: ' + user.name);
    console.log('Email: ' + user.email);
    console.log('Created: ' + user.created_at);
    console.log('Password Hash: ' + user.password_hash.substring(0, 30) + '...');
  });
"

echo ""
echo "✈️ ALL TRIPS"
echo "----------------------------------------"
mongosh $DB_URI --quiet --eval "
  db.trips.find({}).forEach(trip => {
    console.log('---');
    console.log('ID: ' + trip.id);
    console.log('User: ' + trip.user_id);
    console.log('Location: ' + trip.location);
    console.log('Days: ' + trip.number_of_days);
    console.log('Type: ' + trip.trip_type + ' | Vibe: ' + trip.trip_vibe);
    console.log('Arrival: ' + trip.time_of_arrival);
    console.log('Departure: ' + trip.time_of_departure);
  });
"

echo ""
echo "📋 ALL ITINERARIES"
echo "----------------------------------------"
mongosh $DB_URI --quiet --eval "
  db.itineraries.find({}).forEach(itinerary => {
    console.log('---');
    console.log('ID: ' + itinerary.id);
    console.log('Trip ID: ' + itinerary.trip_id);
    console.log('User ID: ' + itinerary.user_id);
    console.log('Days in itinerary: ' + itinerary.itinerary_data.days.length);
    console.log('Created: ' + itinerary.created_at);
  });
"

echo ""
echo "=========================================="
echo "Done! Run this script anytime to view data"
echo "=========================================="
