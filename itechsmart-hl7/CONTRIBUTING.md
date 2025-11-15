# Contributing to iTechSmart HL7

Thank you for your interest in contributing to iTechSmart HL7! This document provides guidelines and instructions for contributing to the project.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Testing Guidelines](#testing-guidelines)
6. [Documentation](#documentation)
7. [Pull Request Process](#pull-request-process)
8. [Issue Reporting](#issue-reporting)
9. [Security Vulnerabilities](#security-vulnerabilities)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of:
- Age, body size, disability, ethnicity, gender identity and expression
- Level of experience, education, socio-economic status
- Nationality, personal appearance, race, religion, or sexual identity and orientation

### Our Standards

**Positive behaviors include:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behaviors include:**
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate in a professional setting

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported to the project team at conduct@itechsmart.dev. All complaints will be reviewed and investigated promptly and fairly.

---

## Getting Started

### Prerequisites

Before contributing, ensure you have:
- Python 3.11+
- Node.js 20+
- Docker and Docker Compose
- Git
- A GitHub account

### Setting Up Development Environment

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/itechsmart-hl7.git
   cd itechsmart-hl7
   ```

2. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/itechsmart/itechsmart-hl7.git
   ```

3. **Set up backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Set up frontend**
   ```bash
   cd frontend
   npm install
   ```

5. **Start services**
   ```bash
   docker-compose up -d postgres redis
   cd backend && alembic upgrade head
   ```

6. **Run tests**
   ```bash
   # Backend
   cd backend && pytest

   # Frontend
   cd frontend && npm test
   ```

---

## Development Workflow

### Branch Naming Convention

Use descriptive branch names following this pattern:
- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Urgent production fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Test additions/updates

**Examples:**
```bash
feature/add-patient-search
bugfix/fix-drug-interaction-check
docs/update-api-documentation
```

### Workflow Steps

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, readable code
   - Follow coding standards
   - Add tests for new features
   - Update documentation

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add patient search functionality"
   ```

4. **Keep your branch updated**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Go to GitHub and create a PR
   - Fill out the PR template
   - Link related issues

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Code style changes (formatting, etc.)
- `refactor` - Code refactoring
- `test` - Adding or updating tests
- `chore` - Maintenance tasks
- `perf` - Performance improvements
- `ci` - CI/CD changes

**Examples:**
```bash
feat(api): add patient search endpoint
fix(drug-checker): correct interaction severity calculation
docs(readme): update installation instructions
test(workflows): add tests for admission workflow
```

---

## Coding Standards

### Python (Backend)

**Style Guide:**
- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Use [flake8](https://flake8.pycqa.org/) for linting

**Best Practices:**
```python
# Use type hints
def get_patient(patient_id: str) -> Optional[Patient]:
    """
    Get patient by ID.
    
    Args:
        patient_id: The patient's unique identifier
        
    Returns:
        Patient object if found, None otherwise
    """
    return db.query(Patient).filter(Patient.id == patient_id).first()

# Use docstrings for all functions/classes
class PatientService:
    """Service for managing patient data."""
    
    def __init__(self, db: Session):
        """Initialize patient service with database session."""
        self.db = db
```

**Code Quality:**
- Maximum line length: 88 characters (Black default)
- Use meaningful variable names
- Keep functions small and focused
- Avoid deep nesting (max 3 levels)
- Use list comprehensions when appropriate
- Handle exceptions properly

**Running Linters:**
```bash
cd backend
black app/
isort app/
flake8 app/
mypy app/
```

### TypeScript (Frontend)

**Style Guide:**
- Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use [ESLint](https://eslint.org/) for linting
- Use [Prettier](https://prettier.io/) for formatting

**Best Practices:**
```typescript
// Use TypeScript interfaces
interface Patient {
  id: string;
  name: string;
  dateOfBirth: string;
}

// Use functional components with hooks
const PatientList: React.FC = () => {
  const [patients, setPatients] = useState<Patient[]>([]);
  
  useEffect(() => {
    fetchPatients();
  }, []);
  
  return (
    <div>
      {patients.map(patient => (
        <PatientCard key={patient.id} patient={patient} />
      ))}
    </div>
  );
};

// Use async/await for promises
const fetchPatients = async (): Promise<Patient[]> => {
  try {
    const response = await api.get('/patients');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch patients:', error);
    throw error;
  }
};
```

**Running Linters:**
```bash
cd frontend
npm run lint
npm run format
npm run type-check
```

---

## Testing Guidelines

### Backend Testing

**Test Structure:**
```python
# tests/test_patient_service.py
import pytest
from app.services.patient_service import PatientService

class TestPatientService:
    """Tests for PatientService."""
    
    def test_get_patient_success(self, db_session):
        """Test successful patient retrieval."""
        # Arrange
        service = PatientService(db_session)
        patient = create_test_patient()
        
        # Act
        result = service.get_patient(patient.id)
        
        # Assert
        assert result is not None
        assert result.id == patient.id
    
    def test_get_patient_not_found(self, db_session):
        """Test patient not found scenario."""
        service = PatientService(db_session)
        result = service.get_patient("nonexistent")
        assert result is None
```

**Running Tests:**
```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_patient_service.py

# Run specific test
pytest tests/test_patient_service.py::TestPatientService::test_get_patient_success
```

**Coverage Requirements:**
- Minimum 80% code coverage
- All new features must include tests
- Critical paths must have 100% coverage

### Frontend Testing

**Test Structure:**
```typescript
// PatientList.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { PatientList } from './PatientList';

describe('PatientList', () => {
  it('renders patient list', async () => {
    // Arrange
    const mockPatients = [
      { id: '1', name: 'John Doe', dateOfBirth: '1980-01-01' }
    ];
    jest.spyOn(api, 'get').mockResolvedValue({ data: mockPatients });
    
    // Act
    render(<PatientList />);
    
    // Assert
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
  });
});
```

**Running Tests:**
```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

---

## Documentation

### Code Documentation

**Python:**
```python
def calculate_drug_interaction_risk(
    medication: str,
    current_medications: List[str],
    allergies: List[str]
) -> Dict[str, Any]:
    """
    Calculate drug interaction risk for a new medication.
    
    This function checks for drug-drug interactions, drug-allergy
    interactions, and duplicate therapy.
    
    Args:
        medication: Name of the new medication to check
        current_medications: List of current medications
        allergies: List of known allergies
        
    Returns:
        Dictionary containing:
            - risk_level: str (low, moderate, high, critical)
            - interactions: List of detected interactions
            - recommendations: List of clinical recommendations
            
    Raises:
        ValueError: If medication name is invalid
        
    Example:
        >>> result = calculate_drug_interaction_risk(
        ...     "warfarin",
        ...     ["aspirin", "lisinopril"],
        ...     ["penicillin"]
        ... )
        >>> print(result['risk_level'])
        'high'
    """
    # Implementation
```

**TypeScript:**
```typescript
/**
 * Fetch patient data from the API
 * 
 * @param patientId - The unique identifier for the patient
 * @returns Promise resolving to patient data
 * @throws {ApiError} If the request fails
 * 
 * @example
 * ```typescript
 * const patient = await fetchPatient('123');
 * console.log(patient.name);
 * ```
 */
async function fetchPatient(patientId: string): Promise<Patient> {
  // Implementation
}
```

### API Documentation

- Update OpenAPI/Swagger documentation for API changes
- Include request/response examples
- Document error responses
- Specify authentication requirements

### User Documentation

- Update user guide for new features
- Include screenshots for UI changes
- Provide step-by-step instructions
- Add troubleshooting tips

---

## Pull Request Process

### Before Submitting

**Checklist:**
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] Branch is up to date with main
- [ ] No merge conflicts
- [ ] Code has been self-reviewed

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Fixes #123

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots here

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass locally
```

### Review Process

1. **Automated Checks**
   - CI/CD pipeline runs automatically
   - All tests must pass
   - Code coverage must meet minimum
   - Linting must pass

2. **Code Review**
   - At least one approval required
   - Address all review comments
   - Make requested changes
   - Re-request review after changes

3. **Merge**
   - Squash and merge (default)
   - Delete branch after merge
   - Update related issues

---

## Issue Reporting

### Bug Reports

**Template:**
```markdown
**Describe the bug**
A clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen

**Screenshots**
If applicable, add screenshots

**Environment:**
- OS: [e.g., Ubuntu 22.04]
- Browser: [e.g., Chrome 120]
- Version: [e.g., 1.0.0]

**Additional context**
Any other relevant information
```

### Feature Requests

**Template:**
```markdown
**Is your feature request related to a problem?**
A clear description of the problem

**Describe the solution you'd like**
What you want to happen

**Describe alternatives you've considered**
Other solutions you've thought about

**Additional context**
Any other relevant information
```

---

## Security Vulnerabilities

**DO NOT** create public issues for security vulnerabilities.

Instead:
1. Email security@itechsmart.dev
2. Include detailed description
3. Provide steps to reproduce
4. Wait for acknowledgment
5. Allow time for fix before disclosure

We aim to respond within 48 hours and provide a fix within 30 days.

---

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to iTechSmart HL7! 🎉

---

## Questions?

- **General Questions:** community@itechsmart.dev
- **Technical Questions:** dev@itechsmart.dev
- **Security Issues:** security@itechsmart.dev

---

**Last Updated:** January 15, 2024