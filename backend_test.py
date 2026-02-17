import requests
import sys
import json
from datetime import datetime, timedelta

class TravelPlannerAPITester:
    def __init__(self, base_url="https://itinera-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_user_email = f"test_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
        self.test_user_password = "TestPass123!"
        self.test_user_name = "Test User"
        self.trip_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        
        try:
            # Use longer timeout for itinerary generation
            timeout = 120 if 'generate-itinerary' in endpoint else 30
            
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=timeout)

            print(f"   Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_user_registration(self):
        """Test user registration"""
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data={
                "name": self.test_user_name,
                "email": self.test_user_email,
                "password": self.test_user_password
            }
        )
        if success and 'token' in response:
            self.token = response['token']
            self.user_data = response['user']
            print(f"   Registered user: {self.user_data}")
            return True
        return False

    def test_user_login(self):
        """Test user login"""
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data={
                "email": self.test_user_email,
                "password": self.test_user_password
            }
        )
        if success and 'token' in response:
            self.token = response['token']
            self.user_data = response['user']
            print(f"   Logged in user: {self.user_data}")
            return True
        return False

    def test_get_current_user(self):
        """Test get current user endpoint"""
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        return success

    def test_create_trip(self):
        """Test trip creation"""
        # Calculate dates for the trip
        arrival_date = datetime.now() + timedelta(days=30)
        departure_date = arrival_date + timedelta(days=3)
        checkin_date = arrival_date + timedelta(hours=2)
        checkout_date = departure_date - timedelta(hours=2)
        
        trip_data = {
            "location": "Paris, France",
            "time_of_arrival": arrival_date.strftime("%Y-%m-%dT%H:%M"),
            "time_of_departure": departure_date.strftime("%Y-%m-%dT%H:%M"),
            "location_of_stay": "Hotel in Marais District",
            "check_in_datetime": checkin_date.strftime("%Y-%m-%dT%H:%M"),
            "check_out_datetime": checkout_date.strftime("%Y-%m-%dT%H:%M"),
            "number_of_days": 3,
            "trip_type": "couple",
            "trip_vibe": "cultural",
            "hectic_level": "moderate",
            "places_preference": "balanced"
        }
        
        success, response = self.run_test(
            "Create Trip",
            "POST",
            "trips",
            200,
            data=trip_data
        )
        if success and 'id' in response:
            self.trip_id = response['id']
            print(f"   Created trip ID: {self.trip_id}")
            return True
        return False

    def test_get_trips(self):
        """Test get user trips"""
        success, response = self.run_test(
            "Get User Trips",
            "GET",
            "trips",
            200
        )
        if success and isinstance(response, list):
            print(f"   Found {len(response)} trips")
            return True
        return False

    def test_generate_itinerary(self):
        """Test itinerary generation"""
        if not self.trip_id:
            print("❌ No trip ID available for itinerary generation")
            return False
            
        success, response = self.run_test(
            "Generate Itinerary",
            "POST",
            f"trips/{self.trip_id}/generate-itinerary",
            200
        )
        if success and 'itinerary' in response:
            print(f"   Generated itinerary with {len(response['itinerary'].get('days', []))} days")
            return True
        return False

    def test_get_itinerary(self):
        """Test get itinerary"""
        if not self.trip_id:
            print("❌ No trip ID available for getting itinerary")
            return False
            
        success, response = self.run_test(
            "Get Itinerary",
            "GET",
            f"trips/{self.trip_id}/itinerary",
            200
        )
        if success and 'itinerary_data' in response:
            print(f"   Retrieved itinerary data")
            return True
        return False

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        success, response = self.run_test(
            "Invalid Login",
            "POST",
            "auth/login",
            401,
            data={
                "email": "invalid@example.com",
                "password": "wrongpassword"
            }
        )
        return success

    def test_unauthorized_access(self):
        """Test accessing protected endpoint without token"""
        # Temporarily remove token
        original_token = self.token
        self.token = None
        
        success, response = self.run_test(
            "Unauthorized Access",
            "GET",
            "trips",
            401
        )
        
        # Restore token
        self.token = original_token
        return success

def main():
    print("🚀 Starting Travel Planner API Tests")
    print("=" * 50)
    
    tester = TravelPlannerAPITester()
    
    # Test sequence
    tests = [
        ("User Registration", tester.test_user_registration),
        ("User Login", tester.test_user_login),
        ("Get Current User", tester.test_get_current_user),
        ("Create Trip", tester.test_create_trip),
        ("Get User Trips", tester.test_get_trips),
        ("Generate Itinerary", tester.test_generate_itinerary),
        ("Get Itinerary", tester.test_get_itinerary),
        ("Invalid Login", tester.test_invalid_login),
        ("Unauthorized Access", tester.test_unauthorized_access),
    ]
    
    failed_tests = []
    
    for test_name, test_func in tests:
        try:
            if not test_func():
                failed_tests.append(test_name)
        except Exception as e:
            print(f"❌ {test_name} - Exception: {str(e)}")
            failed_tests.append(test_name)
    
    # Print results
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    print(f"Tests run: {tester.tests_run}")
    print(f"Tests passed: {tester.tests_passed}")
    print(f"Tests failed: {len(failed_tests)}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if failed_tests:
        print(f"\n❌ Failed tests: {', '.join(failed_tests)}")
        return 1
    else:
        print("\n✅ All tests passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())