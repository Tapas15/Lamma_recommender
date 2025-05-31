#!/usr/bin/env python
"""
Simple test for frontend profile pages
"""
import requests
import time
import sys

def test_services():
    """Test if both frontend and backend are running"""
    print('Testing Frontend and Backend Services...')
    
    # Test backend
    try:
        response = requests.get('http://localhost:8000/docs', timeout=5)
        print(f'✅ Backend Status: {response.status_code} - Backend API is running')
        backend_running = True
    except Exception as e:
        print(f'❌ Backend: Not running - {str(e)}')
        backend_running = False
    
    # Test frontend
    try:
        response = requests.get('http://localhost:3000', timeout=5)
        print(f'✅ Frontend Status: {response.status_code} - Next.js frontend is running')
        frontend_running = True
    except Exception as e:
        print(f'❌ Frontend: Not running - {str(e)}')
        frontend_running = False
    
    return backend_running, frontend_running

def test_profile_pages():
    """Test the profile pages we've implemented"""
    print('\nTesting Profile Endpoints...')
    
    profile_routes = [
        '/candidate-profile',
        '/employer-profile', 
        '/dashboard',
        '/employer-candidates'
    ]
    
    results = {}
    for route in profile_routes:
        try:
            response = requests.get(f'http://localhost:3000{route}', timeout=5)
            if response.status_code == 200:
                print(f'✅ {route}: Page loads successfully')
                results[route] = 'success'
            else:
                print(f'⚠️  {route}: Returns {response.status_code}')
                results[route] = f'status_{response.status_code}'
        except Exception as e:
            print(f'❌ {route}: Failed to load - {str(e)}')
            results[route] = 'error'
    
    return results

def main():
    """Main test function"""
    print("=== Frontend Profile Pages Test ===")
    
    # Test services
    backend_ok, frontend_ok = test_services()
    
    if not frontend_ok:
        print("\n❌ Frontend not running. Please start the Next.js development server.")
        print("Run: cd frontend/lnd-nexus && npm run dev")
        return 1
    
    # Test profile pages
    results = test_profile_pages()
    
    # Summary
    total_tests = len(results)
    successful_tests = sum(1 for r in results.values() if r == 'success')
    
    print(f"\n=== Test Summary ===")
    print(f"Total Pages Tested: {total_tests}")
    print(f"Successfully Loading: {successful_tests}")
    print(f"Issues: {total_tests - successful_tests}")
    
    if successful_tests == total_tests:
        print("🎉 All profile pages are working correctly!")
        return 0
    else:
        print("⚠️  Some profile pages have issues. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 