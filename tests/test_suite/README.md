# Job Recommender System Test Suite

This test suite provides comprehensive testing for the Job Recommender System API and Streamlit frontend.

## Components

The test suite consists of the following components:

- **test_config.py**: Configuration settings and test data generators
- **test_api.py**: API wrapper for interacting with the backend
- **test_services.py**: Service management for starting/stopping the backend and frontend
- **test_flow.py**: Complete test flows for employer and candidate paths
- **run_full_tests.py**: Main test runner with command-line options
- **diagnostic_test.py**: Diagnostic tool for debugging API issues
- **job_diagnostic.py**: Specialized tool for debugging job creation
- **candidate_diagnostic.py**: Specialized tool for debugging candidate registration

## Running Tests

To run the full test suite:

```bash
python run_full_tests.py
```

### Command-line Options

- `--api-url`: Specify a custom API URL (default: http://localhost:8000)
- `--streamlit-url`: Specify a custom Streamlit URL (default: http://localhost:8501)
- `--no-services`: Don't start or manage services (assumes they are already running)
- `--no-cleanup`: Don't stop services after tests complete

## Test Flow

The test suite runs through the following flows:

### Employer Flow

1. Register a new employer
2. Login as the employer
3. Create multiple job postings
4. Create multiple project postings
5. Update the employer profile

### Candidate Flow

1. Register a new candidate
2. Login as the candidate
3. Search for jobs
4. Get job recommendations
5. Apply for jobs and projects
6. Save jobs for later
7. Get saved jobs
8. Get skill gap analysis

## Notes and Workarounds

- The employer registration endpoint doesn't return an employer ID, so we use a fallback ID for job creation
- Candidate registration with complex data can cause server errors, so we use simplified candidate data

## Diagnostic Tools

For debugging specific issues:

- For general API diagnostics: `python diagnostic_test.py`
- For job creation issues: `python job_diagnostic.py`
- For candidate registration issues: `python candidate_diagnostic.py`

## Output

Test results are saved to `test_flow_results.json` for further analysis. 