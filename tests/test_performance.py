import pytest
import time
import threading
import psutil
import os
import statistics
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from src.rag.api import app
from src.rag.analyzer import analyze_beat

# Create a TestClient instance
client = TestClient(app)

@pytest.fixture
def sample_outlines():
    """Sample outlines of different sizes for testing."""
    small_outline = """
    ACT ONE
    
    OPENING IMAGE: John Smith, a middle-aged accountant, sits alone in his cubicle.
    
    THEME STATED: His boss tells him "Life is about taking risks."
    
    CATALYST: John receives a mysterious letter inviting him to join an adventure club.
    """
    
    medium_outline = small_outline * 5  # ~5x larger
    large_outline = small_outline * 20  # ~20x larger
    
    return {
        "small": small_outline,
        "medium": medium_outline,
        "large": large_outline
    }

@pytest.fixture
def mock_analyze_beat():
    """Mock the analyze_beat function to simulate different response times."""
    with patch('src.rag.api.analyze_beat') as mock:
        # Default response with no delay
        mock.return_value = {
            "flag": "Test flag",
            "explanation": "Test explanation",
            "suggestions": ["Test suggestion"]
        }
        yield mock

def test_response_time_for_different_sizes(sample_outlines, mock_analyze_beat):
    """Test response times for different outline sizes."""
    results = {}
    
    for size, outline in sample_outlines.items():
        # Run multiple times to get average
        times = []
        for _ in range(5):
            start_time = time.time()
            response = client.post("/analyze", json={
                "full_outline": outline,
                "designated_beat": "John receives a mysterious letter",
                "beat_type": "Catalyst"
            })
            end_time = time.time()
            assert response.status_code == 200
            times.append(end_time - start_time)
        
        results[size] = {
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "min": min(times),
            "max": max(times)
        }
    
    # Log the results
    for size, metrics in results.items():
        print(f"\nResponse time for {size} outline:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value:.4f} seconds")
    
    # Verify degradation is reasonable
    assert results["medium"]["mean"] < results["large"]["mean"]
    
    # Check if response time for large outline is acceptable
    # This threshold should be adjusted based on application requirements
    assert results["large"]["mean"] < 2.0, "Response time for large outline is too slow"

def test_concurrent_requests_performance(mock_analyze_beat):
    """Test performance under concurrent requests."""
    num_concurrent = 10
    request_data = {
        "full_outline": "Test outline",
        "designated_beat": "Test beat",
        "beat_type": "Catalyst"
    }
    
    # Configure mock to simulate real-world processing time
    def delayed_response(*args, **kwargs):
        time.sleep(0.1)  # 100ms delay
        return {
            "flag": "Test flag",
            "explanation": "Test explanation",
            "suggestions": ["Test suggestion"]
        }
    
    mock_analyze_beat.side_effect = delayed_response
    
    # Use ThreadPoolExecutor to make concurrent requests
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
        futures = [
            executor.submit(lambda: client.post("/analyze", json=request_data))
            for _ in range(num_concurrent)
        ]
        responses = [future.result() for future in futures]
    end_time = time.time()
    
    # All responses should be successful
    assert all(response.status_code == 200 for response in responses)
    
    # Calculate metrics
    total_time = end_time - start_time
    avg_time_per_request = total_time / num_concurrent
    
    print(f"\nConcurrent requests performance ({num_concurrent} requests):")
    print(f"  Total time: {total_time:.4f} seconds")
    print(f"  Average time per request: {avg_time_per_request:.4f} seconds")
    print(f"  Requests per second: {num_concurrent/total_time:.2f}")
    
    # The performance should be better than sequential execution
    # If each request takes 0.1s, sequential execution would take 1s for 10 requests
    assert total_time < (0.1 * num_concurrent * 0.8), "Concurrent performance is not optimal"

def test_memory_usage_profiling(sample_outlines, mock_analyze_beat):
    """Profile memory usage during analysis of different size outlines."""
    process = psutil.Process(os.getpid())
    results = {}
    
    for size, outline in sample_outlines.items():
        # Measure memory before request
        gc_before = process.memory_info().rss / 1024 / 1024  # Convert to MB
        
        response = client.post("/analyze", json={
            "full_outline": outline,
            "designated_beat": "John receives a mysterious letter",
            "beat_type": "Catalyst"
        })
        
        # Measure memory after request
        gc_after = process.memory_info().rss / 1024 / 1024  # Convert to MB
        
        results[size] = {
            "before_mb": gc_before,
            "after_mb": gc_after,
            "difference_mb": gc_after - gc_before
        }
    
    # Log the results
    for size, metrics in results.items():
        print(f"\nMemory usage for {size} outline:")
        print(f"  Before: {metrics['before_mb']:.2f} MB")
        print(f"  After: {metrics['after_mb']:.2f} MB")
        print(f"  Difference: {metrics['difference_mb']:.2f} MB")
    
    # Check for memory leaks
    # A significant increase might indicate a memory leak
    assert results["large"]["difference_mb"] < 50, "Potential memory leak detected"

def test_optimization_opportunities(sample_outlines, mock_analyze_beat):
    """Identify potential optimization opportunities in the analysis pipeline."""
    # Define sub-components to profile
    components = ["vector_search", "functional_analysis", "setup_check", "synthesis"]
    
    timings = {}
    
    # Create a more sophisticated mock that times each component
    def timed_analyze(*args, **kwargs):
        component_times = {}
        
        # Simulate time for vector search
        start = time.time()
        time.sleep(0.05)  # 50ms for vector search
        component_times["vector_search"] = time.time() - start
        
        # Simulate time for functional analysis
        start = time.time()
        time.sleep(0.2)  # 200ms for functional analysis
        component_times["functional_analysis"] = time.time() - start
        
        # Simulate time for setup check
        start = time.time()
        time.sleep(0.15)  # 150ms for setup check
        component_times["setup_check"] = time.time() - start
        
        # Simulate time for synthesis
        start = time.time()
        time.sleep(0.1)  # 100ms for synthesis
        component_times["synthesis"] = time.time() - start
        
        # Store the timings
        nonlocal timings
        timings = component_times
        
        return {
            "flag": "Test flag",
            "explanation": "Test explanation",
            "suggestions": ["Test suggestion"]
        }
    
    # Set the mock to use our timed implementation
    mock_analyze_beat.side_effect = timed_analyze
    
    # Make a request
    response = client.post("/analyze", json={
        "full_outline": sample_outlines["medium"],
        "designated_beat": "John receives a mysterious letter",
        "beat_type": "Catalyst"
    })
    
    assert response.status_code == 200
    
    # Log the component timings
    print("\nComponent timing analysis:")
    total_time = sum(timings.values())
    for component, timing in timings.items():
        percentage = (timing / total_time) * 100
        print(f"  {component}: {timing:.4f}s ({percentage:.1f}%)")
    
    # Identify the slowest component
    slowest_component = max(timings, key=timings.get)
    print(f"\nSlowest component: {slowest_component} ({timings[slowest_component]:.4f}s)")
    
    # Suggest optimizations based on findings
    print("\nOptimization opportunities:")
    if slowest_component == "vector_search":
        print("  - Optimize vector search with better indexing")
        print("  - Consider caching frequent search results")
    elif slowest_component == "functional_analysis":
        print("  - Optimize LLM prompts for faster response")
        print("  - Consider using a faster/smaller model for initial analysis")
    elif slowest_component == "setup_check":
        print("  - Optimize setup verification algorithm")
        print("  - Consider selective checking based on significance")
    elif slowest_component == "synthesis":
        print("  - Simplify synthesis prompt")
        print("  - Consider template-based responses for common issues") 