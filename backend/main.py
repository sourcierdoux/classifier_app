from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uuid
from typing import List

from config import settings
from models import (
    RunClassifierRequest,
    TestResult,
    TestSummary,
    TestStatus,
)
from storage import storage

# Import your existing classifier function here
# from your_module import run_classifier

app = FastAPI(title=settings.app_name, version=settings.app_version)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# In-memory storage for active tests (you might want to use Redis for production)
active_tests = {}


def run_classifier_background(test_id: str, request: RunClassifierRequest):
    """
    Background task to run the classifier.
    This is where you'll integrate your existing run_classifier function.
    """
    test = storage.get_test(test_id)
    if not test:
        return

    try:
        # Update status to running
        test.status = TestStatus.RUNNING
        test.started_at = datetime.now()
        storage.save_test(test)

        # TODO: Replace this with your actual run_classifier function
        # Example:
        # from your_classifier import run_classifier
        # results = run_classifier(
        #     source_path=request.source_path,
        #     out_path=request.out_path,
        #     mode=request.mode.value,
        #     use_filter=request.use_filter,
        #     async_mode=request.async_mode,
        #     max_concurrency=request.max_concurrency
        # )

        # For now, simulate success
        import time
        time.sleep(2)  # Simulate processing

        # Update test with results
        test.status = TestStatus.COMPLETED
        test.completed_at = datetime.now()
        # test.total_emails = results.get('total_emails', 0)
        # test.processed_emails = results.get('processed_emails', 0)
        # test.sr_positive = results.get('sr_positive', 0)
        # test.sr_negative = results.get('sr_negative', 0)
        # test.category_breakdown = results.get('category_breakdown', {})

        # Mock data for demonstration
        test.total_emails = 100
        test.processed_emails = 100
        test.sr_positive = 35
        test.sr_negative = 65

        storage.save_test(test)

    except Exception as e:
        # Update status to failed
        test.status = TestStatus.FAILED
        test.completed_at = datetime.now()
        test.error_message = str(e)
        storage.save_test(test)


@app.post("/api/tests/run", response_model=TestResult)
async def run_test(request: RunClassifierRequest, background_tasks: BackgroundTasks):
    """
    Start a new classification test.
    """
    # Create test record
    test_id = str(uuid.uuid4())
    test = TestResult(
        test_id=test_id,
        status=TestStatus.PENDING,
        source_path=request.source_path,
        out_path=request.out_path,
        mode=request.mode,
        use_filter=request.use_filter,
        async_mode=request.async_mode,
        max_concurrency=request.max_concurrency,
        created_at=datetime.now(),
    )

    # Save test
    storage.save_test(test)

    # Run classifier in background
    background_tasks.add_task(run_classifier_background, test_id, request)

    return test


@app.get("/api/tests", response_model=List[TestSummary])
async def get_tests():
    """
    Get all test history.
    """
    return storage.get_all_tests()


@app.get("/api/tests/{test_id}", response_model=TestResult)
async def get_test(test_id: str):
    """
    Get details of a specific test.
    """
    test = storage.get_test(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return test


@app.delete("/api/tests/{test_id}")
async def delete_test(test_id: str):
    """
    Delete a test from history.
    """
    test = storage.get_test(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    storage.delete_test(test_id)
    return {"message": "Test deleted successfully"}


@app.get("/api/config")
async def get_config():
    """
    Get application configuration for frontend.
    """
    return {
        "default_mode": settings.default_mode,
        "default_use_filter": settings.default_use_filter,
        "default_async_mode": settings.default_async_mode,
        "default_max_concurrency": settings.default_max_concurrency,
        "max_concurrency_limit": settings.max_concurrency_limit,
        "allowed_file_types": settings.allowed_file_types,
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
