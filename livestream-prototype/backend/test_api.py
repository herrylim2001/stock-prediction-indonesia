"""
API Testing Script untuk LiveStream Prototype
Run this script untuk test semua API endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000/api"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_response(response):
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except:
        print(response.text)

def test_health_check():
    print_section("Health Check")
    response = requests.get("http://localhost:5000/")
    print_response(response)

def test_get_talents():
    print_section("GET All Talents")
    response = requests.get(f"{BASE_URL}/talents")
    print_response(response)
    return response.json().get('data', [])

def test_get_talent_by_id(talent_id):
    print_section(f"GET Talent by ID: {talent_id}")
    response = requests.get(f"{BASE_URL}/talents/{talent_id}")
    print_response(response)

def test_update_talent(talent_id):
    print_section(f"UPDATE Talent: {talent_id}")
    data = {
        "bio": "Updated bio via API test"
    }
    response = requests.put(
        f"{BASE_URL}/talents/{talent_id}",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    print_response(response)

def test_update_talent_status(talent_id, status):
    print_section(f"UPDATE Talent Status: {talent_id} -> {status}")
    data = {"status": status}
    response = requests.put(
        f"{BASE_URL}/talents/{talent_id}/status",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    print_response(response)

def test_get_livestreams():
    print_section("GET All Active Livestreams")
    response = requests.get(f"{BASE_URL}/livestreams")
    print_response(response)
    return response.json().get('data', [])

def test_create_livestream(talent_id):
    print_section(f"CREATE Livestream for Talent: {talent_id}")
    data = {
        "talent_id": talent_id,
        "title": "Test Livestream via API"
    }
    response = requests.post(
        f"{BASE_URL}/livestreams",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    print_response(response)
    return response.json().get('data', {}).get('id') if response.status_code == 201 else None

def test_add_like(livestream_id):
    print_section(f"ADD Like to Livestream: {livestream_id}")
    response = requests.post(f"{BASE_URL}/livestreams/{livestream_id}/like")
    print_response(response)

def test_send_gift(livestream_id, amount):
    print_section(f"SEND Gift to Livestream: {livestream_id} (Amount: {amount})")
    data = {"amount": amount}
    response = requests.post(
        f"{BASE_URL}/livestreams/{livestream_id}/gift",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    print_response(response)

def test_end_livestream(livestream_id):
    print_section(f"END Livestream: {livestream_id}")
    response = requests.post(f"{BASE_URL}/livestreams/{livestream_id}/end")
    print_response(response)

def test_get_stats():
    print_section("GET Platform Statistics")
    response = requests.get(f"{BASE_URL}/stats")
    print_response(response)

def run_all_tests():
    print("\n" + "🎬"*30)
    print("  LiveStream API Testing Script")
    print("🎬"*30)

    try:
        # 1. Health Check
        test_health_check()
        time.sleep(1)

        # 2. Get all talents
        talents = test_get_talents()
        time.sleep(1)

        if talents and len(talents) > 0:
            # 3. Get first talent
            first_talent_id = talents[0]['id']
            test_get_talent_by_id(first_talent_id)
            time.sleep(1)

            # 4. Update talent
            test_update_talent(first_talent_id)
            time.sleep(1)

            # 5. Get livestreams
            livestreams = test_get_livestreams()
            time.sleep(1)

            # 6. Create new livestream if talent is not already live
            offline_talent = next((t for t in talents if t['status'] == 'offline'), None)
            if offline_talent:
                new_livestream_id = test_create_livestream(offline_talent['id'])
                time.sleep(1)

                if new_livestream_id:
                    # 7. Add likes
                    for i in range(3):
                        test_add_like(new_livestream_id)
                        time.sleep(0.5)

                    # 8. Send gifts
                    test_send_gift(new_livestream_id, 10)
                    time.sleep(1)
                    test_send_gift(new_livestream_id, 50)
                    time.sleep(1)

                    # 9. Get stats
                    test_get_stats()
                    time.sleep(1)

                    # 10. End livestream
                    test_end_livestream(new_livestream_id)
                    time.sleep(1)

            # 11. Final stats
            test_get_stats()

        print("\n" + "✅"*30)
        print("  All Tests Completed!")
        print("✅"*30 + "\n")

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to server!")
        print("Make sure the backend server is running on http://localhost:5000")
        print("\nStart the server with:")
        print("  cd backend")
        print("  python app.py")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    run_all_tests()
