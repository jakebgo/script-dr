#!/usr/bin/env python
"""
Performance Test Runner for Script Doctor

This script runs the performance tests and generates a comprehensive report
with the results, including charts and recommendations.
"""

import os
import sys
import subprocess
import datetime
import json
from pathlib import Path

# Add parent directory to path to allow importing from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_performance_tests():
    """Run the performance tests and capture the output."""
    print("\n=== Running Performance Tests ===\n")
    
    # Create output directory if it doesn't exist
    output_dir = Path("output/performance_reports")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Run the tests with pytest
    result = subprocess.run(
        ["pytest", "tests/test_performance.py", "-v"],
        capture_output=True,
        text=True
    )
    
    # Parse the test output to extract performance data
    test_output = result.stdout
    
    return test_output

def parse_response_time_results(output):
    """Parse response time results from test output."""
    response_times = {}
    in_response_time_section = False
    current_size = None
    
    for line in output.split('\n'):
        if "Response time for " in line:
            current_size = line.split("Response time for ")[1].split(" outline")[0]
            response_times[current_size] = {}
            in_response_time_section = True
        elif in_response_time_section and "seconds" in line:
            try:
                metric, value = line.strip().split(": ")
                metric = metric.strip()
                value = float(value.split(" seconds")[0])
                response_times[current_size][metric] = value
            except ValueError:
                pass
        elif in_response_time_section and line.strip() == "":
            in_response_time_section = False
    
    return response_times

def parse_concurrent_results(output):
    """Parse concurrent request results from test output."""
    concurrent_results = {}
    in_concurrent_section = False
    
    for line in output.split('\n'):
        if "Concurrent requests performance" in line:
            num_requests = int(line.split("(")[1].split(" ")[0])
            concurrent_results["num_requests"] = num_requests
            in_concurrent_section = True
        elif in_concurrent_section and "Total time" in line:
            concurrent_results["total_time"] = float(line.split(": ")[1].split(" seconds")[0])
        elif in_concurrent_section and "Average time per request" in line:
            concurrent_results["avg_time_per_request"] = float(line.split(": ")[1].split(" seconds")[0])
        elif in_concurrent_section and "Requests per second" in line:
            concurrent_results["requests_per_second"] = float(line.split(": ")[1])
        elif in_concurrent_section and line.strip() == "":
            in_concurrent_section = False
    
    return concurrent_results

def parse_memory_usage(output):
    """Parse memory usage results from test output."""
    memory_usage = {}
    in_memory_section = False
    current_size = None
    
    for line in output.split('\n'):
        if "Memory usage for " in line:
            current_size = line.split("Memory usage for ")[1].split(" outline")[0]
            memory_usage[current_size] = {}
            in_memory_section = True
        elif in_memory_section and "MB" in line:
            try:
                metric, value = line.strip().split(": ")
                metric = metric.strip()
                value = float(value.split(" MB")[0])
                memory_usage[current_size][metric] = value
            except ValueError:
                pass
        elif in_memory_section and line.strip() == "":
            in_memory_section = False
    
    return memory_usage

def parse_component_timing(output):
    """Parse component timing results from test output."""
    component_timing = {}
    in_timing_section = False
    
    for line in output.split('\n'):
        if "Component timing analysis" in line:
            in_timing_section = True
        elif in_timing_section and "%" in line and ":" in line:
            try:
                component, timing_info = line.strip().split(": ")
                component = component.strip()
                time_value = float(timing_info.split("s")[0])
                percentage = float(timing_info.split("(")[1].split("%")[0])
                component_timing[component] = {"time": time_value, "percentage": percentage}
            except ValueError:
                pass
        elif in_timing_section and "Slowest component" in line:
            parts = line.split("Slowest component: ")[1].split(" (")
            component_timing["slowest_component"] = parts[0]
            component_timing["slowest_time"] = float(parts[1].split("s")[0])
        elif "Optimization opportunities" in line:
            in_timing_section = False
    
    return component_timing

def parse_optimization_suggestions(output):
    """Parse optimization suggestions from test output."""
    suggestions = []
    in_suggestions_section = False
    
    for line in output.split('\n'):
        if "Optimization opportunities" in line:
            in_suggestions_section = True
        elif in_suggestions_section and line.strip().startswith("  - "):
            suggestions.append(line.strip()[4:])
        elif in_suggestions_section and line.strip() == "":
            in_suggestions_section = False
    
    return suggestions

def generate_report(test_output, response_times, concurrent_results, memory_usage, component_timing, suggestions):
    """Generate a performance report based on the test results."""
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_file = f"output/performance_reports/performance_report_{now}.md"
    
    with open(report_file, "w") as f:
        f.write("# Script Doctor Performance Test Report\n\n")
        f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Response Times Section
        f.write("## Response Times\n\n")
        f.write("| Outline Size | Mean (s) | Median (s) | Min (s) | Max (s) |\n")
        f.write("|--------------|----------|------------|---------|----------|\n")
        for size, metrics in response_times.items():
            f.write(f"| {size} | {metrics.get('mean', 'N/A'):.4f} | {metrics.get('median', 'N/A'):.4f} | {metrics.get('min', 'N/A'):.4f} | {metrics.get('max', 'N/A'):.4f} |\n")
        f.write("\n")
        
        # Concurrent Request Performance
        f.write("## Concurrent Request Performance\n\n")
        f.write(f"- Number of concurrent requests: {concurrent_results.get('num_requests', 'N/A')}\n")
        f.write(f"- Total execution time: {concurrent_results.get('total_time', 'N/A'):.4f} seconds\n")
        f.write(f"- Average time per request: {concurrent_results.get('avg_time_per_request', 'N/A'):.4f} seconds\n")
        f.write(f"- Requests per second: {concurrent_results.get('requests_per_second', 'N/A'):.2f}\n\n")
        
        # Memory Usage
        f.write("## Memory Usage\n\n")
        f.write("| Outline Size | Before (MB) | After (MB) | Difference (MB) |\n")
        f.write("|--------------|-------------|------------|------------------|\n")
        for size, metrics in memory_usage.items():
            f.write(f"| {size} | {metrics.get('before_mb', 'N/A'):.2f} | {metrics.get('after_mb', 'N/A'):.2f} | {metrics.get('difference_mb', 'N/A'):.2f} |\n")
        f.write("\n")
        
        # Component Timing
        f.write("## Component Timing\n\n")
        f.write("| Component | Time (s) | Percentage |\n")
        f.write("|-----------|----------|------------|\n")
        for component, metrics in component_timing.items():
            if isinstance(metrics, dict):  # Skip non-dict entries like 'slowest_component'
                f.write(f"| {component} | {metrics.get('time', 'N/A'):.4f} | {metrics.get('percentage', 'N/A'):.1f}% |\n")
        f.write("\n")
        f.write(f"**Slowest Component:** {component_timing.get('slowest_component', 'N/A')} ({component_timing.get('slowest_time', 'N/A'):.4f}s)\n\n")
        
        # Optimization Suggestions
        f.write("## Optimization Suggestions\n\n")
        for suggestion in suggestions:
            f.write(f"- {suggestion}\n")
        f.write("\n")
        
        # Save raw test output
        f.write("## Raw Test Output\n\n")
        f.write("```\n")
        f.write(test_output)
        f.write("\n```\n")
    
    # Also save results as JSON for further processing
    json_file = f"output/performance_reports/performance_data_{now}.json"
    with open(json_file, "w") as f:
        json.dump({
            "response_times": response_times,
            "concurrent_results": concurrent_results,
            "memory_usage": memory_usage,
            "component_timing": component_timing,
            "suggestions": suggestions
        }, f, indent=2)
    
    return report_file, json_file

def main():
    """Run performance tests and generate a report."""
    test_output = run_performance_tests()
    
    # Parse the results
    response_times = parse_response_time_results(test_output)
    concurrent_results = parse_concurrent_results(test_output)
    memory_usage = parse_memory_usage(test_output)
    component_timing = parse_component_timing(test_output)
    suggestions = parse_optimization_suggestions(test_output)
    
    # Generate the report
    report_file, json_file = generate_report(
        test_output, 
        response_times, 
        concurrent_results, 
        memory_usage, 
        component_timing, 
        suggestions
    )
    
    print(f"\n=== Performance Report Generated ===")
    print(f"Report: {report_file}")
    print(f"JSON data: {json_file}")

if __name__ == "__main__":
    main() 