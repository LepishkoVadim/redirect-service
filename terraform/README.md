# Terraform — AWS deploy (single EC2, HTTP)

Provisions one EC2 instance in the **default VPC** that runs the production docker-compose
stack (nginx + gunicorn/Django + PostgreSQL + Redis) over **HTTP** on an **Elastic IP**.
Terraform state is **local**.

## What it creates

- EC2 key pair from your public key (`~/.ssh/lepishko.pub`).
- Security group — inbound **80** (HTTP, all) and **22** (SSH, `ssh_ingress_cidr`); all egress.
  Postgres/Redis are **not** exposed (they stay on the container network).
- Elastic IP + `t3.small` Ubuntu 24.04 instance (AMI from Canonical's SSM parameter).
- `random_password` for `DJANGO_SECRET_KEY`, the Postgres password, and the Django admin password.
- `user_data` bootstraps the box: installs Docker, clones the public repo, writes `.env`
  (with the generated secrets and the EIP in `ALLOWED_HOSTS`), then
  `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build`.

## Prerequisites

- Terraform ≥ 1.6, an AWS profile named `redirect-service` (`~/.aws/credentials`).
- The app repo must be **public** (user_data clones over HTTPS).
- `~/.ssh/lepishko.pub` present (its private key is what you SSH with).

## Usage

```bash
cd terraform
export AWS_PROFILE=redirect-service

terraform init
terraform plan          # review — creates ~7 resources
terraform apply         # type: yes

terraform output app_url                       # http://<eip>/
terraform output -raw superuser_password       # the bootstrapped admin password
```

First boot takes a few minutes (Docker install + image build). Then:

```bash
curl -i "$(terraform output -raw app_url)health/"    # → 200
```

- Swagger: `http://<eip>/api/docs/` · Admin: `http://<eip>/admin/` (user `admin`).
- SSH: `terraform output -raw ssh_command` → `ssh ubuntu@<eip>`.
- Inspect boot: `ssh ubuntu@<eip> 'sudo cat /var/log/cloud-init-output.log'`.
- App logs: `ssh ubuntu@<eip> 'cd /opt/redirect-service && sudo docker compose ... logs web'`.

## Tear down

```bash
terraform destroy
```

## Notes & trade-offs

- **HTTP only.** No domain/TLS. To add HTTPS later: point a domain's A-record at the EIP,
  enable the commented `443` block in `nginx/nginx.conf`, run certbot on the host, open 443
  in the security group.
- **Postgres runs in Docker** (per the project design — no RDS). Data lives in the `pgdata`
  Docker volume on the instance, so it is **ephemeral if the instance is replaced**. Changing
  `user_data` triggers instance replacement (`user_data_replace_on_change = true`) — take a
  `pg_dump` first if you need to keep data.
- **SSH is open to `0.0.0.0/0` by default** — set `ssh_ingress_cidr` to your IP/32 for real use.
- **Redeploying code:** the box clones once at boot. To ship new code either SSH in and
  `git pull && docker compose ... up -d --build`, wire up the GitHub Actions SSH deploy step,
  or taint the instance (`terraform apply -replace=aws_instance.web`).
- **State is local** — `terraform.tfstate` stays in this dir (gitignored). Back it up; for teams
  switch to an S3 + DynamoDB backend.
