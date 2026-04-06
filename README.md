# 🦴 ArthroMate Backend

> Serverless backend for the ArthroMate arthritis patient tracking application.

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![AWS](https://img.shields.io/badge/AWS-serverless-orange.svg)](https://aws.amazon.com/)
[![Terraform](https://img.shields.io/badge/IaC-Terraform-623CE4.svg)](https://www.terraform.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

ArthroMate is a mobile companion for arthritis patients that helps them log daily pain levels, track affected joints, monitor mobility trends, and share structured reports with their healthcare providers. This repository contains the complete **serverless backend** — a production-grade REST API deployed entirely on AWS with infrastructure-as-code.

---

## 🏗️ Architecture

```
┌──────────┐     ┌────────────────┐     ┌──────────┐     ┌───────────┐
│  Mobile  │────▶│  API Gateway   │────▶│ Lambda   │────▶│ RDS MySQL │
│  Client  │     │  (REST + JWT)  │     │ (Python) │     │ (VPC)     │
└──────────┘     └──────┬─────────┘     └────┬─────┘     └───────────┘
                        │                    │
                   ┌────▼────┐          ┌────▼─────────┐
                   │ Cognito │          │CloudWatch    │
                   │ (Auth)  │          │(Logs+Metrics)│
                   └─────────┘          └──────────────┘
```

| Layer | Technology | Description |
|---|---|---|
| **API** | AWS API Gateway (REST) | Public entry point with Cognito JWT authorizer |
| **Compute** | AWS Lambda (Python 3.11) | On-demand serverless functions inside private VPC |
| **Database** | AWS RDS MySQL 8.0 | Managed relational database in private subnets |
| **Auth** | AWS Cognito User Pools | Sign-up, sign-in, token issuance and validation |
| **CI/CD** | AWS CodePipeline + CodeBuild | Automated test → plan → apply pipeline |
| **Observability** | AWS CloudWatch | Structured JSON logs, custom metrics, SNS alarms |
| **IaC** | Terraform (HashiCorp) | All infrastructure defined as code |

---

## 📦 Project Structure

```
arthromate-backend/
├── src/
│   ├── handlers/           # Lambda entry points (one per endpoint)
│   │   ├── create_pain_report.py
│   │   ├── get_pain_report.py
│   │   ├── list_pain_reports.py
│   │   ├── delete_pain_report.py
│   │   ├── get_user_profile.py
│   │   └── update_user_profile.py
│   ├── services/           # Business logic and validation
│   │   ├── pain_report.py
│   │   ├── user.py
│   │   └── notification.py
│   ├── models/             # MySQL data access layer (PyMySQL)
│   │   ├── db.py
│   │   ├── pain_report.py
│   │   └── user.py
│   ├── middleware/          # Auth, error handling, request parsing
│   │   ├── auth.py
│   │   ├── error_handler.py
│   │   ├── lambda_wrapper.py
│   │   └── request_parser.py
│   └── utils/              # Shared helpers
│       ├── logger.py       # Structured JSON logger
│       └── response_builder.py
├── infra/
│   ├── main.tf             # Root module — wires all child modules
│   ├── variables.tf
│   ├── outputs.tf
│   ├── backend.tf          # Remote state in S3 + DynamoDB locking
│   └── modules/
│       ├── rds/            # VPC, subnets, security groups, MySQL
│       ├── lambda/         # Functions, IAM roles, VPC config, packaging
│       ├── api_gateway/    # REST API, routes, Cognito authorizer
│       ├── cognito/        # User Pool, App Client
│       ├── monitoring/     # Log groups, metric alarms, SNS
│       └── cicd/           # CodePipeline, CodeBuild, artifacts bucket
├── migrations/
│   └── 001_init.sql        # Database schema
├── tests/
│   ├── unit/               # Isolated unit tests with mocked DB
│   └── integration/        # End-to-end API integration tests
├── pyproject.toml
├── AGENTS.md               # Agent build specification
├── system-overview.md       # Deep-dive architecture documentation
└── README.md               # ← you are here
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Terraform ≥ 1.2.0**
- **AWS credentials** configured locally
- **MySQL client** (for schema migrations)

### Local Development

```bash
# Clone the repository
git clone git@github.com:gultandon/arthromate1.git
cd arthromate1

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest --cov=src --cov-report=term-missing

# Lint the codebase
ruff check src/ tests/
ruff format src/ tests/
```

### Database Setup

```bash
# Apply schema to a fresh RDS instance
mysql -h <DB_HOST> -u arthromate -p arthromate < migrations/001_init.sql
```

---

## 🔌 API Endpoints

All endpoints require a valid **Cognito JWT** in the `Authorization: Bearer <token>` header.

| Method | Endpoint | Handler | Description |
|---|---|---|---|
| `POST` | `/pain-reports` | `createPainReport` | Submit a new pain report |
| `GET` | `/pain-reports` | `listPainReports` | List all reports for the user |
| `GET` | `/pain-reports/{reportId}` | `getPainReport` | Get a single pain report |
| `DELETE` | `/pain-reports/{reportId}` | `deletePainReport` | Delete a pain report |
| `GET` | `/user/profile` | `getUserProfile` | Get current user profile |
| `PUT` | `/user/profile` | `updateUserProfile` | Update user profile |

### Response Format

Every response follows a consistent envelope:

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

### Pain Report Schema

```json
{
  "reportId": "uuid-v4",
  "userId": "cognito-sub",
  "timestamp": "2024-03-20T09:45:00+05:30",
  "painLevel": 7,
  "affectedJoints": ["left_knee", "right_hip", "spine"],
  "notes": "Stiffness worse in the morning",
  "mobility": "low"
}
```

**Validation rules:**
- `painLevel` — integer between 0 and 10
- `affectedJoints` — non-empty array of valid joint identifiers
- `mobility` — one of `low`, `medium`, `high`
- `notes` — optional string, max 1000 characters

---

## 🔐 Authentication Flow

1. Mobile client authenticates with **Cognito User Pool** (email/phone + password)
2. Receives JWT access + ID tokens
3. Includes token in `Authorization` header on every request
4. **API Gateway Cognito Authorizer** validates the token before invoking Lambda
5. Lambda extracts `userId` from `event.requestContext.authorizer.claims.sub`

The Lambda layer never re-verifies tokens — it trusts the API Gateway authorizer.

---

## 🏗️ Infrastructure (Terraform)

All AWS resources are defined in Terraform. No manual console changes — everything is code.

```bash
cd infra

# Initialize (first time only)
terraform init

# Switch workspace
terraform workspace select dev    # or staging / prod

# Plan changes
terraform plan -var-file="terraform.tfvars"

# Apply changes
terraform apply -var-file="terraform.tfvars"

# Validate formatting
terraform fmt -check -recursive
terraform validate
```

### Remote State

State is stored in **S3** with **DynamoDB locking** to prevent concurrent applies:

```hcl
backend "s3" {
  bucket         = "my-terraform-state-bucket-gul1234"
  key            = "backend/terraform.tfstate"
  region         = "ap-south-1"
  encrypt        = true
}
```

### Workspaces

| Workspace | Purpose |
|---|---|
| `dev` | Local development and PR testing |
| `staging` | Pre-production integration |
| `prod` | Live production environment |

---

## 🔄 CI/CD Pipeline

```
GitHub (main) → CodePipeline → CodeBuild
  ├── pip install -e ".[dev]"
  ├── pytest --cov=src
  ├── terraform fmt -check
  ├── terraform validate
  ├── terraform plan
  └── terraform apply (auto-approve)
```

- **PRs** — plan-only run, no apply
- **Merges to `main`** — full pipeline including `terraform apply`
- **Failure** — pipeline halts, zero partial deployments

---

## 🧪 Testing

```bash
# Unit tests (fast, mocked — no real infrastructure)
pytest tests/unit/ --cov=src --cov-report=term-missing

# Integration tests (requires dev AWS environment)
pytest tests/integration/

# Run specific test file
pytest tests/unit/models/test_pain_report.py -v
```

**Coverage target:** ≥ 80% on `src/services/` and `src/models/`

---

## 📊 Observability

All Lambda functions emit **structured JSON logs** to CloudWatch. No `print()` statements — use the shared logger:

```python
from src.utils import logger

logger.log("info", "PainReportProcessed", user_id=user_id, duration_ms=120)
```

### Custom Metrics

| Metric | Namespace | Trigger |
|---|---|---|
| `PainReportProcessed` | ArthroMate/Backend | Every successful report creation |
| `AuthFailure` | ArthroMate/Backend | Failed authentication attempts |
| `LambdaError` | ArthroMate/Backend | Unhandled Lambda exceptions |

### Alarms

| Alarm | Threshold | Action |
|---|---|---|
| Lambda Errors | > 1 error in 5 min | SNS notification |
| Lambda Duration | P99 > 500ms | SNS notification |
| Lambda Throttles | > 0 throttles | SNS notification |

---

## 🌍 Environment Variables

Lambda environment variables are injected by Terraform. For local development, copy `.env.example` to `.env`:

| Variable | Source | Description |
|---|---|---|
| `DB_HOST` | `module.rds.db_host` | RDS MySQL endpoint |
| `DB_PORT` | `module.rds.db_port` | RDS port (3306) |
| `DB_NAME` | `module.rds.db_name` | Database name |
| `DB_USER` | `module.rds.db_user` | Database username |
| `DB_PASSWORD` | `module.rds.db_password` | Auto-generated password |
| `COGNITO_USER_POOL_ID` | `module.cognito.user_pool_id` | Cognito User Pool |
| `COGNITO_CLIENT_ID` | `module.cognito.app_client_id` | Cognito App Client |
| `AWS_REGION` | Lambda runtime | AWS region |
| `LOG_LEVEL` | `var.log_level` | Logging verbosity |

---

## 🧠 Design Principles

- **One Lambda, one responsibility** — each handler file maps to a single API endpoint
- **No business logic in handlers** — handlers parse input, call a service, return a response
- **Database access through models only** — no raw SQL in services or handlers
- **All errors bubble up** — typed `AppError` classes with automatic HTTP status codes
- **Structured logging only** — JSON logs for CloudWatch Logs Insights queries
- **Everything is code** — zero manual AWS console changes

---

## 📐 Scale Targets

- **500+** pain reports processed per day
- **99.9%** uptime SLA
- **≤ 200ms** average API response time

---

## 📚 Further Reading

- [`system-overview.md`](system-overview.md) — Deep dive into every component and how they connect
- [`AGENTS.md`](AGENTS.md) — Complete build specification and conventions for AI agents
- [`migrations/001_init.sql`](migrations/001_init.sql) — Database schema

---

## 📄 License

MIT © Gul Tandon
