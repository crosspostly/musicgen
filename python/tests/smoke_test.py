"""
Simple smoke test for DiffRhythm service
"""

import sys
import os

# Add services directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services'))

def test_engine_creation():
    """Test that engine can be created"""
    try:
        from diffrhythm_service import DiffRhythmEngine
        engine = DiffRhythmEngine()
        assert engine is not None
        assert hasattr(engine, 'device')
        assert hasattr(engine, 'model_cache_dir')
        print("✅ DiffRhythmEngine creation test passed")
        return True
    except Exception as e:
        print(f"❌ DiffRhythmEngine creation test failed: {e}")
        return False

def test_job_store_operations():
    """Test basic job store operations"""
    try:
        from diffrhythm_service import JobStore, GenerationRequest
        
        store = JobStore()
        
        # Create job
        request = GenerationRequest(
            prompt="Test prompt",
            durationSeconds=30,
            language="en"
        )
        
        job_id = store.create_job(request)
        assert job_id is not None
        
        # Get job
        job = store.get_job(job_id)
        assert job is not None
        assert job.request_data == request
        assert job.status == "pending"
        
        # Update job
        store.update_job(job_id, progress=50, message="Processing")
        updated_job = store.get_job(job_id)
        assert updated_job.progress == 50
        assert updated_job.message == "Processing"
        
        print("✅ Job store operations test passed")
        return True
    except Exception as e:
        print(f"❌ Job store operations test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Running Python DiffRhythm smoke tests...\n")
    
    tests_passed = 0
    total_tests = 2
    
    if test_engine_creation():
        tests_passed += 1
    
    if test_job_store_operations():
        tests_passed += 1
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All smoke tests passed!")
        sys.exit(0)
    else:
        print("💥 Some tests failed!")
        sys.exit(1)