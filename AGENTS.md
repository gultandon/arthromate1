# ArthroMate Backend — Agent Build Spec

## Project Overview

ArthroMate is a mobile app for arthritis patients. This repo contains the **serverless backend** built on AWS. It processes pain reports submitted by patients, handles auth, and exposes a REST API consumed by iOS/Android clients.

Infrastructure is managed entirely with **Terraform**. There is no SAM, CloudFormation, or CDK in this repo.

---

## Architecture

| Layer | Technology |
|---|---|
| API | AWS API Gateway (REST) |
| Compute | AWS Lambda (Python 3.11) |
| Database | AWS RDS MySQL 8.0 (private VPC) |
| Auth | AWS Cognito (User Pools + Identity Pools) |
| CI/CD | AWS CodePipeline + CodeBuild |
| Observability | AWS CloudWatch (logs, metrics, alarms) |
| IaC | Terraform (HashiCorp) |

**Key scale targets:**
- 500+ pain reports processed per day
- 99.9% uptime SLA
- ≤200ms average API response time

---

## Repository Structure

```
arthromate-backend/
├── src/
│   ├── handlers/          # Lambda function entry points (one file per function)
│   ├── services/          # Business logic (painReport, user, notification)
│   ├── models/            # MySQL data models (PyMySQL)
│   ├── middleware/        # Auth validation, error handling, request parsing
│   └── utils/             # Shared helpers (logger, response builder, etc.)
├── infra/
│   ├── main.tf            # Root module — wires together all child modules
│   ├── variables.tf       # Input variable declarations
│   ├── outputs.tf         # Output values (API URL, RDS endpoint, etc.)
│   ├── terraform.tfvars   # Environment-specific values (not committed for prod)
│   ├── backend.tf         # Remote state config (S3 + DynamoDB lock)
│   └── modules/
│       ├── api_gateway/   # API Gateway REST API + stages + authorizer
│       ├── lambda/        # Lambda functions + IAM roles + VPC config + packaging
│       ├── rds/           # VPC + private subnets + security groups + RDS MySQL
│       ├── cognito/       # User Pool + App Client + Identity Pool
│       ├── cicd/          # CodePipeline + CodeBuild + IAM
│       └── monitoring/    # CloudWatch log groups + metrics + alarms + SNS
├── migrations/
│   └── 001_init.sql       # Schema: CREATE TABLE for users and pain_reports
├── tests/
│   ├── unit/
│   └── integration/
├── .env.example
├── pyproject.toml
└── AGENTS.md              # ← you are here
```

---

## Commands

### Install dependencies
```bash
pip install -e ".[dev]"
```

### Run tests
```bash
pytest --cov=src --cov-report=term-missing    # unit tests
pytest tests/integration                        # integration tests (requires AWS creds)
```

### Lint application code
```bash
ruff check src/ tests/
ruff format src/ tests/
```

### Apply schema to a fresh database
```bash
mysql -h <DB_HOST> -u arthromate -p arthromate < migrations/001_init.sql
```

### Terraform — first-time setup
```bash
cd infra
terraform init            # initialises providers and remote backend
```

### Terraform — plan and apply
```bash
terraform plan -var-file="terraform.tfvars"
terraform apply -var-file="terraform.tfvars"
```

### Terraform — target a single module (use sparingly)
```bash
terraform plan -target=module.lambda
terraform apply -target=module.lambda
```

### Terraform — destroy (dev only, never prod)
```bash
terraform destroy -var-file="terraform.tfvars"
```

### Format and validate Terraform
```bash
terraform fmt -recursive
terraform validate
```

### Deploy via CI/CD
Push to `main` — CodePipeline picks it up automatically and runs `terraform apply`.

---

## Terraform State

Remote state is stored in **S3** with **DynamoDB locking** to prevent concurrent applies. This locking table is a Terraform bootstrapping resource, separate from the application database.

```hcl
# infra/backend.tf
terraform {
  backend "s3" {
    bucket         = "arthromate-tf-state"
    key            = "backend/terraform.tfstate"
    region         = "ap-south-1"
    dynamodb_table = "arthromate-tf-locks"
    encrypt        = true
  }
}
```

Never run `terraform apply` locally against the `prod` workspace. Use the CI/CD pipeline.

### Workspaces

| Workspace | Purpose |
|---|---|
| `dev` | Local and PR testing |
| `staging` | Pre-prod integration |
| `prod` | Live environment |

Switch with: `terraform workspace select dev`

---

## Environment Variables

Lambda environment variables are injected by Terraform via the `lambda` module. Do not hardcode them in `src/`.

| Variable | Terraform source |
|---|---|
| `DB_HOST` | `module.rds.db_host` |
| `DB_PORT` | `module.rds.db_port` |
| `DB_NAME` | `module.rds.db_name` |
| `DB_USER` | `module.rds.db_user` |
| `DB_PASSWORD` | `module.rds.db_password` |
| `COGNITO_USER_POOL_ID` | `module.cognito.user_pool_id` |
| `COGNITO_CLIENT_ID` | `module.cognito.app_client_id` |
| `AWS_REGION` | Set by Lambda execution environment |
| `LOG_LEVEL` | `var.log_level` (default: `info`) |

For local development, copy `.env.example` to `.env`. Never commit real credentials or state files.

---

## Core Domain: Pain Reports

The primary entity is a **pain report** submitted by a patient.

```json
{
  "reportId": "uuid-v4",
  "userId": "cognito-sub",
  "timestamp": "ISO-8601",
  "painLevel": 0-10,
  "affectedJoints": ["left_knee", "right_hip"],
  "notes": "optional free text",
  "mobility": "low | medium | high"
}
```

**MySQL access patterns:**
- List all reports for a user, sorted newest-first: `SELECT ... WHERE userId = ? ORDER BY timestamp DESC`
- Get a single report by ID: `SELECT ... WHERE reportId = ? AND userId = ?`
- Query reports in a date range: `SELECT ... WHERE userId = ? AND timestamp BETWEEN ? AND ?`

`affectedJoints` and `profile` (users table) are stored as JSON columns and decoded automatically by the model layer.

---

## Auth Flow

1. Mobile client authenticates via **Cognito User Pool**
2. Receives JWT (ID token + access token)
3. Passes token in `Authorization: Bearer <token>` header
4. API Gateway **Cognito Authorizer** validates token before invoking Lambda
5. Lambda extracts `userId` from `event.requestContext.authorizer.claims.sub`

Do not reimplement auth logic in Lambda — trust the Cognito authorizer.

---

## Coding Conventions

- **One Lambda, one responsibility.** Don't put multiple routes in a single handler.
- **No business logic in handlers.** Handlers parse input, call a service, return a response. Logic lives in `src/services/`.
- **Structured logging only.** Use the shared logger (`src/utils/logger.py`) which outputs JSON. Never use `print()` or `logging` directly outside the shared logger.
- **All errors bubble up via the error middleware.** Throw typed errors from services; don't construct HTTP responses inside services.
- **Database access goes through model files only.** No raw SQL or PyMySQL calls in handlers or services.

### Response format
All API responses follow this envelope:
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

---

## Observability

CloudWatch is the single source of truth for operational data. Log groups and alarms are provisioned by the `monitoring` Terraform module — do not create them manually in the console.

- **Every Lambda** emits structured JSON logs with `userId`, `requestId`, `durationMs`, and outcome.
- **Custom metrics** are published for: `PainReportProcessed`, `AuthFailure`, `LambdaError`.
- **Alarms** fire to SNS on: error rate >1%, P99 latency >500ms, Lambda throttles >0.

When debugging, always check CloudWatch Logs Insights before assuming code issues.

---

## CI/CD Pipeline (CodePipeline)

```
GitHub (main) → CodePipeline → CodeBuild
  → pytest --cov=src --cov-report=term-missing
  → terraform fmt -check
  → terraform validate
  → terraform plan
  → terraform apply (auto-approve, prod workspace)
```

- PRs trigger a plan-only run — no apply on PRs.
- Merges to `main` trigger the full pipeline including `terraform apply`.
- If `terraform apply` exits non-zero, the pipeline halts — no partial deploys.
- Deployment time target: ≤ previous baseline × 0.5 (50% reduction achieved vs manual deploy).

---

## Testing Guidelines

- Unit tests mock the MySQL connection (`get_connection`) — no real database calls in unit tests.
- Integration tests run against the `dev` Terraform workspace.
- Aim for >80% coverage on `src/services/` — this is where bugs live.
- Use `pytest` as the test runner.

---

## What Agent Should Know

- **All infrastructure changes go through Terraform.** Never create or modify AWS resources manually in the console — they will be overwritten on the next `terraform apply`.
- **Modules are the unit of change.** When adding a new Lambda, add it inside `infra/modules/lambda/` and wire outputs through `main.tf`. Don't create standalone `.tf` files at the root level.
- **Schema changes require a migration.** Add a new numbered file to `migrations/` and apply it manually (or via a migration step in CI) before deploying code that depends on the new schema. RDS MySQL is strongly typed — column additions, removals, and type changes are explicit operations.
- **Lambda runs inside a private VPC.** It cannot reach the public internet without a NAT Gateway. Keep Lambda dependencies lean and avoid any package that makes outbound internet calls at runtime.
- **Lambda cold starts matter.** The PyMySQL connection is established lazily on first invocation and reused on warm starts. Do not move `get_connection()` to module-level (import time) — it would block the cold start unnecessarily.
- **Cognito Authorizer is the security boundary.** Assume `userId` from the authorizer context is trusted; don't re-verify tokens in Lambda.
- **CloudWatch log retention** is set to 30 days (configured in the `monitoring` module). Don't log PII — no patient names, emails, or health note content verbatim.
- **Never commit `terraform.tfvars` for prod or `.terraform/` directories.** Both are in `.gitignore`.
- **The DynamoDB table in `backend.tf`** is only for Terraform state locking, not application data. Do not confuse it with the application database.
