# Project LifeCoach reservation
A web application for coaching and psychological counseling.  


## Project Description
- [ ] 1 Client account (`feature/client-account`)
  - [ ] Registration
  - [ ] Profile
  - [ ] Session History

- [ ] 2 Booking system (`feature/booking-system`)
  - [ ] Ability to book appointments (US time, EU)
    - [ ] Personal or online session
  - [ ] View available slots
  - [ ] Cancel or reschedule sessions
    - [ ] More than 24 hours in advance – allowed
    - [ ] Less than 24 hours – admin only

- [ ] 3 List of Services and Prices (`feature/services-prices`)

- [ ] 4 Payment integration (`feature/payment-integration`)
  - [ ] PayPall
  - [ ] Venmo
  - [ ] Cash

- [ ] 5 Content management (`feature/content-management`)
  - [ ] Downloadable materials
  - [ ] Articles
  - [ ] Courses

- [ ] 6 Notifications (`feature/notifications`)
  - [ ] Session reminders
  - [ ] News and announcements

- [ ] 7 Session Feedback (`feature/session-feedback`)
  - [ ] Rating system after completed session
  - [ ] Optional written review/comments

- [ ] 8 Reporting (`feature/reporting-analytics`)
  - [ ] Booking reports
  - [ ] Payment overviews
  - [ ] Client engagement analytics

### Sub-feature Branches
- Client Account:
  - `feature/user-registration`
  - `feature/user-profile`
  - `feature/session-history`

- Booking System:
  - `feature/appointment-booking`
  - `feature/timezone-management`
  - `feature/session-cancellation`

- Payment Integration:
  - `feature/paypal-integration`
  - `feature/venmo-integration`
  - `feature/cash-payment-handling`

- Content Management:
  - `feature/material-downloads`
  - `feature/article-management`
  - `feature/course-system`

## Development Setup

### Prerequisites
- Python 3.11.2
- pip (Python package manager)
- GitHub repository: https://github.com/JudynkaS/LifeCoach

### Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/JudynkaS/LifeCoach.git
cd LifeCoach
```

2. Create and activate virtual environment:
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows
.venv\Scripts\activate
```

3. Install Django and other dependencies:
```bash
# Install Django
pip install django==5.0.2

# Install other dependencies
pip install -r requirements.txt
```

4. Set up environment variables:
- Create a `.env` file in the root directory
- Add the following variables:
  ```
  SECRET_KEY=your_secret_key_here
  DEBUG=True
  DATABASE_URL=your_database_url
  ```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser (admin account):
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

### Troubleshooting
- If you encounter any issues with pip, try upgrading it first:
  ```bash
  python -m pip install --upgrade pip
  ```
- If you get permission errors, try running commands with sudo (Linux/Mac) or run as administrator (Windows)
- Make sure your Python version matches the requirement (3.11.2)

## Git Workflow

### Branch Strategy
- `main` - Production-ready code, stable version of the application
- `develop` - Main development branch where features are integrated
- Feature branches: `feature/<feature-name>` - For developing new features
- Bug fix branches: `bugfix/<bug-name>` - For fixing bugs
- Release branches: `release/v<version>` - For preparing new releases
- Hotfix branches: `hotfix/<fix-name>` - For urgent production fixes

### Branch Naming Convention
- Feature branches: `feature/user-authentication`, `feature/booking-system`
- Bugfix branches: `bugfix/login-error`, `bugfix/payment-validation`
- Release branches: `release/v1.0.0`, `release/v1.1.0`
- Hotfix branches: `hotfix/security-patch`, `hotfix/critical-error`

### Development Process
1. Create a new branch for each feature/fix:
```bash
git checkout develop
git pull origin develop
git checkout -b feature/<feature-name>
```

2. Make changes and commit regularly:
```bash
git add .
git commit -m "Description of changes"
```

3. Push changes to remote:
```bash
git push origin feature/<feature-name>
```

4. Create pull request to merge into `develop` branch
5. After review and approval, merge into develop
6. Delete feature branch after successful merge

### Commit Message Convention
- `feat:` New feature (e.g., "feat: Add user authentication")
- `fix:` Bug fix (e.g., "fix: Resolve booking conflict")
- `docs:` Documentation changes (e.g., "docs: Update API documentation")
- `style:` Code style changes (e.g., "style: Format booking component")
- `refactor:` Code refactoring (e.g., "refactor: Optimize booking logic")
- `test:` Adding or modifying tests (e.g., "test: Add booking validation tests")
- `chore:` Maintenance tasks (e.g., "chore: Update dependencies")

### Branch Protection Rules
- `main` branch: 
  - Requires pull request reviews
  - Must be up-to-date before merging
  - Must pass CI/CD checks
- `develop` branch:
  - Requires at least one review
  - Must pass basic tests