# ArthroMate Backend — What Every Component Does

This document explains the backend system in plain language. It is meant to help you understand what each piece does and how the pieces fit together, without getting lost in code details.

---

## The Big Picture

ArthroMate is an app for arthritis patients. The backend in this repo is the "serverless brain" that lives inside AWS. Its main job is to:

1. Receive data from the mobile app (pain reports, profile updates).
2. Make sure only logged-in patients can send or read that data.
3. Store the data safely.
4. Send alerts if something breaks.

There are no physical servers you manage. Everything is made of small, on-demand services that AWS runs for you.

---

## How a Request Travels (The 30,000-Foot View)

Imagine a patient opens the app and submits a pain report. Here is what happens, end to end:

1. **Mobile app** sends the report over the internet to a single web address (the API).
2. **API Gateway** receives the request, checks that a valid login token is attached, and decides which worker should handle it.
3. **Lambda** (a small piece of code that runs on demand) wakes up, reads the request, validates the data, and decides what to do with it.
4. **RDS MySQL** (the database) stores the pain report.
5. Lambda sends a success message back through API Gateway to the app.
6. Along the way, **CloudWatch** writes logs and keeps an eye on performance. If errors spike, it sends an alarm.

That flow is the same whether the patient is creating a report, reading old reports, or updating their profile.

---

## The Application Code (`src/`)

This is the "brain" logic. It is written in Python and organized into layers so the code stays clean and easy to change.

### 1. Handlers (`src/handlers/`)

**What they are:** The front door of the code. There is one handler for each type of request the API accepts.

**Examples in this project:**
- `create_pain_report` — when a patient submits a new pain entry.
- `list_pain_reports` — when a patient views their history.
- `get_pain_report` — when a patient opens a single past entry.
- `delete_pain_report` — when a patient removes an entry.
- `get_user_profile` / `update_user_profile` — when a patient views or edits their profile.

**What they do:**
- Pull out the user's identity.
- Pull out the data the app sent (the JSON body, URL parameters, or query filters).
- Hand that information off to a service.
- Wrap the result into a standard response and send it back.

**Key idea:** Handlers are thin. They do not make decisions about what is "correct" data; they just receive the request and pass it along. Think of them as receptionists.

### 2. Middleware (`src/middleware/`)

**What it is:** Shared helpers that sit between the handler and the outside world. They handle repetitive chores so every handler does not have to reinvent them.

**Pieces inside middleware:**

- **Auth (`auth.py`)** — Confirms the request came from a real logged-in user. In this system, the heavy lifting of checking passwords and tokens is done by AWS Cognito *before* the request even reaches the code. The middleware simply reads the trusted user ID from the request and passes it inward. If the ID is missing, it rejects the request immediately.

- **Request Parser (`request_parser.py`)** — Safely extracts the JSON body, URL path variables (like a report ID), and query parameters (like date filters). It turns raw internet text into clean data the services can use.

- **Lambda Wrapper (`lambda_wrapper.py`)** — A safety blanket wrapped around every handler. It starts a timer, runs the handler, and catches any unexpected errors. If something goes wrong, it turns the error into a polite failure message for the app and writes a detailed log for developers. It also records how long the request took.

- **Error Handler (`error_handler.py`)** — Defines the types of errors the system can throw, such as "validation failed," "not found," or "unauthorized." Using typed errors lets the wrapper send the right HTTP status code back to the app automatically.

### 3. Services (`src/services/`)

**What they are:** The decision-makers. This is where the actual business rules live.

**Pain Report Service (`pain_report.py`):**
- Validates that pain level is between 0 and 10.
- Validates that affected joints are from an allowed list.
- Validates that notes are not too long.
- Generates a unique ID and timestamp.
- Saves the final report to the database via the model.
- Logs a custom metric so you can see how many reports are being created.

**User Service (`user.py`):**
- Fetches a patient's profile.
- Auto-creates a profile the very first time a new user interacts with the system.
- Merges profile updates (so you do not accidentally overwrite existing data).

**Notification Service (`notification.py`):**
- Publishes numbers to CloudWatch so you can graph them later (for example, how many auth failures happened today).
- Keeps the alarm system fed with real-time data.

**Key idea:** Services do not talk directly to the internet, and they do not know about HTTP status codes. They just receive clean data, enforce rules, and ask the models to save or retrieve things.

### 4. Models (`src/models/`)

**What they are:** The filing clerks. Every interaction with the database goes through a model. No other part of the code talks to the database directly.

**Pain Report Model (`pain_report.py`):**
- Creates a new record.
- Retrieves one record by ID for a specific user.
- Lists all records for a user, optionally filtered by a date range.
- Deletes a record.

**User Model (`user.py`):**
- Creates a user record.
- Fetches a user by ID.
- Updates user fields.

**Database Connection (`db.py`):**
- A single shared doorway to RDS MySQL. Every model uses this same doorway so there is only one place to manage the connection. The connection is cached within a Lambda container and automatically reconnected if it goes stale between warm invocations.

**Key idea:** Models know *how* to store and retrieve data, but they do not know *why* the data is being stored. They enforce no business rules; they only execute the commands the services give them.

### 5. Utils (`src/utils/`)

**What they are:** Shared tools used by many other parts of the system.

- **Logger (`logger.py`)** — Writes structured JSON logs. Instead of plain text, every log line is a machine-readable object with a timestamp, level, message, and extra details. This makes it easy to search logs in CloudWatch and build dashboards.
- **Response Builder (`response_builder.py`)** — Creates the standard envelope that every API response uses. Whether the request succeeds or fails, the app always receives a predictable shape:
  ```json
  {
    "success": true|false,
    "data": { ... },
    "error": null|{ ... }
  }
  ```

---

## The Infrastructure (`infra/`)

This is the "physical plant" of the system, described as code using Terraform. Instead of clicking around the AWS website to create resources, every resource is defined in text files. That means the entire environment can be recreated, copied, or inspected just by reading these files.

### 1. API Gateway (`modules/api_gateway/`)

**What it is:** The public front door. It exposes the web address that the mobile app talks to.

**What it does:**
- Defines the available URLs (routes), such as `/pain-reports`, `/pain-reports/{reportId}`, and `/user/profile`.
- Protects every route with the Cognito authorizer, so unauthenticated requests are turned away immediately.
- Routes valid requests to the correct Lambda function.
- Keeps access logs so you can see traffic patterns and debug issues.

### 2. Lambda (`modules/lambda/`)

**What it is:** The compute engine. Lambda is AWS's service that runs your Python code only when a request arrives. You do not pay for idle time, and AWS automatically handles scaling from one request to thousands.

**What this module does:**
- Defines six functions, one for each handler.
- Packages all the Python code into a single zip file.
- Creates an IAM role (security identity) for the functions, including the VPC access policy needed to reach the private RDS instance.
- Places every function inside the same private VPC as RDS so they can communicate over the internal network.
- Injects environment variables (DB connection details, Cognito IDs, log level) so the code knows which resources to use without hardcoding names.

### 3. RDS (`modules/rds/`)

**What it is:** The database. RDS MySQL is a managed relational database. You do not install or patch the database engine; AWS handles backups, failover, and patching.

**What this module creates:**
- A **VPC** (Virtual Private Cloud) — a private network that isolates the database and Lambda functions from the public internet.
- Two **private subnets** across two availability zones, where both RDS and Lambda live.
- **Security groups** — RDS only accepts MySQL connections from the Lambda security group; Lambda can reach RDS but nothing else can.
- A **DB subnet group** that tells RDS which subnets it may use.
- A **MySQL 8.0 instance** (`db.t3.micro` by default) with a randomly generated password.

**Tables in this project:**
- **`pain_reports`** — Stores every pain entry, indexed by `(userId, timestamp)` for efficient per-user queries sorted by date. `reportId` is the primary key for direct lookups.
- **`users`** — Stores patient profile data, keyed by `userId`.

The schema lives in `migrations/001_init.sql` and must be applied once against a fresh database before the first deployment.

### 4. Cognito (`modules/cognito/`)

**What it is:** The identity and login system. Cognito handles sign-up, sign-in, password resets, and token generation.

**What this module does:**
- Creates a User Pool — the directory of all registered patients.
- Enforces password rules (minimum length, uppercase, numbers, symbols).
- Creates an App Client — the specific configuration the mobile app uses to talk to the User Pool.
- Works with API Gateway so that only users with a valid token can reach the backend.

### 5. Monitoring (`modules/monitoring/`)

**What it is:** The security camera and alarm system.

**What this module does:**
- Creates a CloudWatch log group for API Gateway and each Lambda function, keeping 30 days of logs.
- Creates an SNS topic (a notification channel) for alarms.
- Sets alarms that watch every Lambda function:
  - **Error alarm** — fires if a function throws errors.
  - **Duration alarm** — fires if the slowest 1% of requests take longer than 500ms.
  - **Throttle alarm** — fires if AWS starts limiting traffic because a function is overloaded.

When an alarm fires, it sends a message to the SNS topic, which can email or text the team.

### 6. CI/CD (`modules/cicd/`)

**What it is:** The auto-deploy factory. It watches the GitHub repository and automatically updates the live system when code changes.

**What this module does:**
- Creates a CodePipeline that listens to the `main` branch on GitHub.
- When new code is pushed, it pulls the code into a CodeBuild worker.
- The worker runs the test suite, checks that Terraform files are formatted correctly, validates the infrastructure plan, and then applies it.
- Uses an S3 bucket to pass files between pipeline stages.

**Why it matters:** You never have to manually update AWS from your laptop. The pipeline guarantees that every change is tested and applied the same way every time.

### 7. Root Terraform Files (`infra/` at the top level)

- **`main.tf`** — The wiring diagram. It creates all the modules above and passes information between them. For example, it takes the RDS connection details from the `rds` module and passes them to the `lambda` module as environment variables.
- **`variables.tf`** — Declares inputs the entire infrastructure needs, such as project name, environment (dev/staging/prod), and AWS region.
- **`outputs.tf`** — Declares useful values the system exports after creation, such as the API URL and the RDS endpoint.
- **`backend.tf`** — Tells Terraform to store its state file in S3 with DynamoDB locking. This prevents two people from accidentally changing infrastructure at the same time. (This locking table is separate from the application database.)
- **`terraform.tfvars`** — Holds the actual values for variables (not committed for production, because it can contain sensitive settings).

---

## Tests (`tests/`)

Tests make sure the code behaves correctly before it ever reaches a live environment.

- **Unit tests** (`tests/unit/`) — Test individual functions in isolation. They mock the MySQL connection, so no real database or internet calls happen. They cover services, models, middleware, and utilities.
- **Integration tests** (`tests/integration/`) — Test the system as a whole, sometimes against real AWS resources in the dev environment, to confirm the pieces work together.

The CI/CD pipeline runs unit tests automatically on every push. If a test fails, the deployment stops.

---

## How the Layers Connect (A Simple Map)

| Layer | Analogy | Talks to |
|---|---|---|
| **Mobile App** | The patient | API Gateway |
| **API Gateway** | The front desk | Cognito (for ID checks), Lambda (to process requests) |
| **Lambda / Handlers** | The receptionist | Middleware (auth, parsing), Services |
| **Middleware** | Security guard / translator | Handlers, Services, Utils |
| **Services** | The doctor making decisions | Models, Utils |
| **Models** | The filing clerk | RDS MySQL |
| **RDS MySQL** | The filing cabinet | Nobody; it just stores data |
| **Cognito** | The ID office | API Gateway |
| **CloudWatch / Alarms** | Security cameras | SNS (to alert humans) |
| **CI/CD Pipeline** | The factory assembly line | GitHub, CodeBuild, Terraform, AWS |

---

## Summary

- **Handlers** receive requests.
- **Middleware** handles authentication, parsing, and error safety nets.
- **Services** enforce business rules and orchestrate what should happen.
- **Models** read and write data to RDS MySQL.
- **Utils** provide shared logging and response formatting.
- **Terraform** builds and connects all the AWS pieces: API Gateway, Lambda, RDS MySQL (inside a private VPC), Cognito, monitoring, and CI/CD.
- **Tests** catch problems before they reach patients.

Everything is wired together through `infra/main.tf`, deployed automatically via the CI/CD pipeline, and observed through CloudWatch logs and alarms.
