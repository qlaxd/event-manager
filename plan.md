# UCC Event Manager - Production Deployment Plan

## Overview

This document provides a comprehensive, step-by-step plan for deploying the UCC Event Manager application to a secure, scalable, and maintainable production environment. The plan places a heavy emphasis on security, incorporating the project's existing security documentation (`docs/security.md`) and addressing all identified risks. The recommended approach uses Amazon Web Services (AWS) and a CI/CD pipeline automated with GitHub Actions.

---

## 1. Pre-Deployment: Code & Environment Hardening

This phase focuses on preparing the codebase and environment for a secure production deployment.

- [ ] **Address Security Audit Recommendations (`docs/backend/dev/security.md`):**
    - [ ] **Remove HS256 Fallback:** In `backend/app/core/security.py`, modify `create_access_token`, `create_refresh_token`, and `decode_token` to *only* use RS256. The application should fail fast if the required JWT keys are not present in a production environment.
    - [ ] **Strengthen Password Validation:** In `backend/app/core/security.py`, replace the hardcoded common password list with a robust library (e.g., `password-strength` for Python) to check new passwords against a comprehensive list of known weak passwords.
    - [ ] **Secure Secondary Tokens:** In `backend/app/services/auth_service.py`, replace the unsalted `sha256` hashes for refresh tokens and password reset tokens with a keyed hash like `HMAC-SHA256`, using the application's `SECRET_KEY` as the key.

- [ ] **Pin Docker Image Versions:**
    - [ ] In `backend/rasa/actions/Dockerfile`, change `FROM rasa/rasa-sdk:latest` to a specific, stable version (e.g., `FROM rasa/rasa-sdk:3.6.2`).
    - [ ] In `backend/Dockerfile`, change `FROM python:3.11-slim` to a specific patch version (e.g., `FROM python:3.11.5-slim`).
    - [ ] Review all base images and pin them to specific versions to ensure reproducible builds.

- [ ] **Define `backend` Service in `docker-compose.yml`:**
    - [ ] Add the missing `backend` service definition to the `docker-compose.yml` file to align with the project's documentation and complete the local development setup. This service should build from `backend/Dockerfile`.

- [ ] **Review and Finalize Production Configuration:**
    - [ ] Scrutinize all variables in `example.env`. Document every variable required for production.
    - [ ] Generate strong, random values for all production secrets (`SECRET_KEY`, `ADMIN_API_KEY`, database passwords, etc.).

---

## 2. Production Infrastructure Setup (AWS)

This section details the provisioning of a secure and scalable infrastructure on AWS. Using Infrastructure as Code (IaC) with Terraform is highly recommended.

- [ ] **Networking (VPC):**
    - [ ] Provision a Virtual Private Cloud (VPC) with at least two Availability Zones (AZs) for high availability.
    - [ ] Create public and private subnets in each AZ. Public subnets for internet-facing resources (Load Balancers), and private subnets for application and data layers.
    - [ ] Set up a NAT Gateway in a public subnet to allow resources in private subnets (like the application containers) to access the internet for things like pulling images or calling external APIs, without being directly exposed.
    - [ ] Configure strict Network ACLs (NACLs) and Security Groups to control traffic between subnets and to/from the internet, following the principle of least privilege.

- [ ] **Managed Data Stores:**
    - [ ] **Database:** Provision an **AWS RDS for PostgreSQL** instance.
        - Place it in private subnets.
        - Enable encryption-at-rest.
        - Enforce SSL/TLS for connections.
        - Configure automated daily snapshots and point-in-time recovery.
    - [ ] **Cache:** Provision an **AWS ElastiCache for Redis** cluster.
        - Place it in private subnets.
        - Enable encryption-in-transit and encryption-at-rest.

- [ ] **Container Orchestration (ECS on Fargate):**
    - [ ] Create an **ECS Cluster**.
    - [ ] Use **AWS Fargate** as the launch type to run containers without managing servers.
    - [ ] Set up **ECS Task Definitions** for each service (`backend`, `rasa`, `action-server`, `ollama`).
        - The task definitions will specify the Docker image (from ECR), CPU/memory allocation, environment variables, and logging configuration.
    - [ ] Create **ECS Services** to maintain the desired number of tasks for each service and handle deployments.

- [ ] **Ingress and Service Discovery:**
    - [ ] Set up an **Application Load Balancer (ALB)** in the public subnets.
        - The ALB will terminate TLS (HTTPS) traffic using an ACM certificate.
        - It will route traffic to the appropriate backend services (`rasa`, `backend`) based on host or path.
    - [ ] Configure **ECS Service Discovery** (using AWS Cloud Map) to allow services within the VPC to discover and communicate with each other (e.g., `action-server` finding `backend`).

- [ ] **Container Registry:**
    - [ ] Create a private **Amazon Elastic Container Registry (ECR)** repository for each Docker image (`backend`, `action-server`, `ollama`).

---

## 3. CI/CD Pipeline Setup (GitHub Actions)

Automate the build, test, and deployment process securely. Create a workflow file like `.github/workflows/production-deploy.yml`.

- [ ] **Create GitHub Actions Secrets:**
    - [ ] Store `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and other deployment-related secrets in GitHub Encrypted Secrets for the repository.

- [ ] **CI - Build and Test Job:**
    - [ ] **Trigger**: On push to `main` branch.
    - [ ] **Checkout Code**: Check out the repository.
    - [ ] **Linting & Unit Tests**: Run linters and unit/integration tests for the backend.
    - [ ] **Security Scanning (SAST & Dependency Check)**:
        - Integrate `bandit` to scan Python code for vulnerabilities.
        - Integrate `safety` or `pip-audit` to check for vulnerable Python dependencies.
        - Add `npm audit` if a frontend exists.
        - **Gate the build**: Fail the workflow if critical vulnerabilities are found.
    - [ ] **Build Docker Images**: Build the `backend`, `action-server`, and `ollama` images.

- [ ] **CD - Push and Deploy Job (depends on CI):**
    - [ ] **Log in to ECR**: Authenticate the workflow to the AWS ECR.
    - [ ] **Container Vulnerability Scan**:
        - Use a tool like **Trivy** or **Amazon ECR's native scanning** to scan the newly built Docker images for OS and library vulnerabilities.
        - Fail the build if high or critical severity vulnerabilities are found.
    - [ ] **Push to ECR**: Tag the images with the Git commit SHA and push them to their respective ECR repositories.
    - [ ] **Deploy to ECS**:
        - Download the current ECS task definitions.
        - Update the task definitions with the new ECR image tags.
        - Register the new task definitions with ECS.
        - Update the corresponding ECS services to trigger a rolling deployment with the new task definition.
    - [ ] **Run Database Migrations**: After a successful backend deployment, run `alembic upgrade head` as a one-off ECS task against the production database.

---

## 4. Production Configuration & Secrets Management

This is one of the most critical aspects of security. **Do not use `.env` files in production.**

- [ ] **Centralized Secret Management:**
    - [ ] Use **AWS Secrets Manager** or **AWS Systems Manager Parameter Store (SecureString)** to store all secrets.
    - [ ] Store database credentials, `SECRET_KEY`, JWT keys, third-party API keys, etc.
    - [ ] The application's IAM Role (assigned to the ECS Task) should have permissions to read these secrets.

- [ ] **JWT Key Management:**
    - [ ] Generate a production-grade 4096-bit RS256 key pair.
    - [ ] Store the private and public keys in AWS Secrets Manager.
    - [ ] The application should fetch these keys from Secrets Manager on startup. Do not bake them into the Docker image.

- [ ] **Update Application to Read from AWS:**
    - [ ] Modify `app/core/config.py` to fetch configuration from AWS Secrets Manager at startup if running in a production environment. Fall back to environment variables for local development.

---

## 5. Deployment, Logging, and Monitoring

- [ ] **Initial Deployment:**
    - [ ] Manually provision the infrastructure using your IaC scripts (Terraform).
    - [ ] Manually populate AWS Secrets Manager with all production secrets.
    - [ ] Manually trigger the CI/CD pipeline for the first time to deploy the application.
    - [ ] Manually run the initial database migration.

- [ ] **Centralized Logging:**
    - [ ] Configure ECS tasks to use the `awslogs` log driver.
    - [ ] This will send all container `stdout`/`stderr` to **Amazon CloudWatch Logs**.
    - [ ] Ensure logs are structured (the `structlog` library in the backend is perfect for this) to enable powerful querying and analysis.

- [ ] **Monitoring and Alerting (CloudWatch):**
    - [ ] **Metrics**:
        - Create CloudWatch Dashboards to monitor key application metrics: ALB request count, 5xx error rate, latency, ECS CPU and Memory utilization, RDS database connections and CPU utilization.
    - [ ] **Alarms**:
        - Create CloudWatch Alarms to notify the team (e.g., via Slack or PagerDuty) for critical events:
            - High API error rate (>1%).
            - High latency.
            - High CPU or Memory utilization on any service.
            - ECS service with zero running tasks.
            - Database CPU utilization > 80%.
    - [ ] **Security Monitoring (per `docs/security.md`):**
        - Create CloudWatch Metric Filters on your log groups to specifically track and create alarms for security events (e.g., `AUTH_FAILURE`, `AUTH_LOCKOUT`, `PRIVILEGE_ESCALATION`).

---

## 6. Ongoing Maintenance and Operations

- [ ] **Backup and Disaster Recovery:**
    - [ ] Verify that RDS automated daily backups are enabled.
    - [ ] Periodically test restoring from a backup to a temporary environment to ensure the recovery process works.
    - [ ] Back up your Infrastructure as Code state files.

- [ ] **Patch Management:**
    - [ ] Regularly update base Docker images to get security patches.
    - [ ] Regularly update application dependencies (`pyproject.toml`, `requirements.txt`) and run them through the full CI/CD pipeline to deploy.
    - [ ] Subscribe to security mailing lists for your key dependencies.

- [ ] **Incident Response:**
    - [ ] Formalize the Incident Response plan outlined in `docs/security.md`.
    - [ ] Ensure the on-call team has a clear playbook for responding to the CloudWatch alarms you've configured.

- [ ] **Key Rotation:**
    - [ ] Establish and document a schedule for rotating all secrets and keys (database credentials, JWT keys, API keys), as specified in `docs/security.md`. Automate this process where possible. 