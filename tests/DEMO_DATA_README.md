# Demo Data Generation Scripts

This directory contains scripts for generating demo data for testing the Job Recommender API.

## Prerequisites

Before running these scripts, make sure you have:

1. The Job Recommender API running on http://localhost:8000
2. Python 3.8+ with the required packages installed:
   ```
   pip install faker requests
   ```

## Available Scripts

### 1. Create Demo Candidates

Creates candidate accounts with realistic profile data.

```bash
python tests/create_demo_candidates.py [--count N]
```

Options:
- `--count N`: Number of candidate accounts to create (default: 10)

Output:
- Creates candidate accounts in the database
- Saves the created data to `tests/demo_candidates.json`

### 2. Create Demo Employers

Creates employer accounts with realistic company data.

```bash
python tests/create_demo_employers.py [--count N]
```

Options:
- `--count N`: Number of employer accounts to create (default: 10)

Output:
- Creates employer accounts in the database
- Saves the created data to `tests/demo_employers.json`

### 3. Create Demo Jobs

Creates job postings using existing employer accounts (or creates a new employer if needed).

```bash
python tests/create_demo_jobs.py [--count N]
```

Options:
- `--count N`: Number of job postings to create (default: 10)

Output:
- Creates job postings in the database
- Saves the created data to `tests/demo_jobs.json`

### 4. Create Demo Projects

Creates project postings using existing employer accounts (or creates a new employer if needed).

```bash
python tests/create_demo_projects.py [--count N]
```

Options:
- `--count N`: Number of project postings to create (default: 10)

Output:
- Creates project postings in the database
- Saves the created data to `tests/demo_projects.json`

## Usage Examples

### Generate a Complete Test Dataset

To generate a complete test dataset with 20 candidates, 5 employers, 30 jobs, and 15 projects:

```bash
# Create candidates
python tests/create_demo_candidates.py --count 20

# Create employers
python tests/create_demo_employers.py --count 5

# Create jobs
python tests/create_demo_jobs.py --count 30

# Create projects
python tests/create_demo_projects.py --count 15
```

### Generate Only Jobs or Projects

If you already have employer accounts and just want to create job postings:

```bash
python tests/create_demo_jobs.py --count 20
```

Or if you just want to create project postings:

```bash
python tests/create_demo_projects.py --count 15
```

## Notes

- All demo accounts use the password `Password123!` for easy testing
- The scripts will handle errors gracefully and continue with the next item if one fails
- The generated data is saved to JSON files for reference and further testing
- The scripts are independent and can be run in any order, but creating employers before jobs/projects is recommended
- If no existing employers are found when creating jobs/projects, a new employer account will be created automatically 