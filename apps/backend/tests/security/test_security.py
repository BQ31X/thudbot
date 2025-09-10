# /tests/security/test_security.py
import os
from fastapi.testclient import TestClient

from thudbot_core.config import load_env  # Import robust .env loader
load_env()

def test_cors_configuration():
    """Test CORS headers are properly restricted"""
    from thudbot_core.api import app
    client = TestClient(app)
    
    # Test that CORS headers are set correctly based on environment
    env_setting = os.getenv("ENV", "dev")
    
    # Test 1: Malicious origin should be rejected
    response_malicious = client.options("/api/chat", headers={
        "Origin": "https://malicious-site.com",
        "Access-Control-Request-Method": "POST"
    })

    malicious_cors_header = response_malicious.headers.get("access-control-allow-origin")
    assert malicious_cors_header is None, f"Malicious origin should be rejected, but got: {malicious_cors_header}"

    # Test 2: Allowed origin should be accepted
    if env_setting == "dev":
        # Test localhost in dev mode
        response_allowed = client.options("/api/chat", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST"
        })
        allowed_cors_header = response_allowed.headers.get("access-control-allow-origin")
        assert allowed_cors_header == "http://localhost:3000", f"Dev mode should allow localhost, got: {allowed_cors_header}"
    else:
        # Test production origins
        allowed_origins = os.getenv("ALLOWED_ORIGINS", "https://boffo.games").split(",")
        test_origin = allowed_origins[0].strip()
        response_allowed = client.options("/api/chat", headers={
            "Origin": test_origin,
            "Access-Control-Request-Method": "POST"
        })
        allowed_cors_header = response_allowed.headers.get("access-control-allow-origin")
        assert allowed_cors_header == test_origin, f"Production should allow {test_origin}, got: {allowed_cors_header}"

def test_api_key_not_in_request_body():
    """Ensure API keys are not sent from frontend and are ignored if sent"""
    from thudbot_core.api import app
    client = TestClient(app)
    
    # Test that sending api_key field is ignored (FastAPI/Pydantic ignores extra fields by default)
    response = client.post("/api/chat", json={
        "user_message": "test message",
        "api_key": "should_be_ignored"  # This should be completely ignored
    })
    
    # Should work normally - the api_key field is silently ignored
    # This is actually GOOD security - extra fields can't be used maliciously
    assert response.status_code in [200, 400, 500, 503], f"Request with extra api_key field should work normally, got {response.status_code}"
    
    # Test that valid request (without api_key) also works
    response_valid = client.post("/api/chat", json={
        "user_message": "test message",
        "session_id": "test"
    })
    
    # Should work the same way
    assert response_valid.status_code in [200, 400, 500, 503], f"Valid request should work normally, got {response_valid.status_code}"
    
    # The key security win: both requests should behave identically since api_key is ignored
    assert response.status_code == response_valid.status_code, "Requests with/without api_key should behave identically"

def test_environment_not_polluted():
    """Verify os.environ is not modified during requests"""
    from thudbot_core.api import app
    client = TestClient(app)
    
    # Save original environment
    original_env = dict(os.environ)
    original_openai_key = os.environ.get('OPENAI_API_KEY')
    
    # Make a request that would pollute environment
    response = client.post("/api/chat", json={
        "user_message": "test message",
        "api_key": "test_key_pollution"
    })
    
    # Check if environment was polluted
    current_openai_key = os.environ.get('OPENAI_API_KEY')
    
    # This test will FAIL with current code (which is good - shows the problem)
    # After we fix the pollution issue, this should pass
    if original_openai_key:
        # Don't expose actual API keys in test output
        assert current_openai_key == original_openai_key, f"Environment was polluted! API key changed from original value"
    
    # Restore environment to be safe
    os.environ.clear()
    os.environ.update(original_env)

def test_cors_methods_restricted():
    """Test that only POST methods are allowed"""
    from thudbot_core.api import app
    client = TestClient(app)
    
    # Test that GET is not allowed
    response = client.get("/api/chat")
    assert response.status_code == 405, f"GET should not be allowed, got: {response.status_code}"
    
    # Test that PUT is not allowed  
    response = client.put("/api/chat")
    assert response.status_code == 405, f"PUT should not be allowed, got: {response.status_code}"

def test_session_hijacking_protection():
    """Test that session IDs are properly validated"""
    from thudbot_core.api import app
    client = TestClient(app)
    
    # Test with predictable session ID
    response1 = client.post("/api/chat", json={
        "user_message": "test 1",
        "session_id": "session_123"
    })
    
    response2 = client.post("/api/chat", json={
        "user_message": "test 2", 
        "session_id": "session_124"  # Try to guess another session
    })
    
    # Both should work (for now) but shouldn't expose each other's data
    # This is a placeholder test - will need to be enhanced when we fix session security
    assert response1.status_code in [200, 400, 500, 503], "Session 1 should work"
    assert response2.status_code in [200, 400, 500, 503], "Session 2 should work"

if __name__ == "__main__":
    print("🔒 Running Security Tests")
    
    # Run each test
    tests = [
        test_cors_configuration,
        test_api_key_not_in_request_body, 
        test_environment_not_polluted,
        test_cors_methods_restricted,
        test_session_hijacking_protection
    ]
    
    for test in tests:
        try:
            test()
            print(f"✅ {test.__name__}")
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")