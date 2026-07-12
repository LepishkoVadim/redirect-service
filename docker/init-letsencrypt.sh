#!/usr/bin/env bash
# One-time Let's Encrypt bootstrap for the TLS stack.
#
# Solves the chicken-and-egg (nginx won't start with a 443 block whose cert doesn't exist
# yet, but certbot's HTTP-01 challenge needs nginx serving :80): stage a throwaway
# self-signed cert, start nginx, then replace it with a real certbot-issued cert.
#
# Run from the repo root on the host:
#   sudo DOMAIN=redirect-service.pp.ua EMAIL=you@example.com bash docker/init-letsencrypt.sh
set -euo pipefail

DOMAIN="${DOMAIN:-redirect-service.pp.ua}"
EMAIL="${EMAIL:-lepishko2000@gmail.com}"
COMPOSE="docker compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.tls.yml"
LIVE="/etc/letsencrypt/live/$DOMAIN"

echo ">> Bring up the app (db, redis, web) without nginx first"
$COMPOSE up -d db redis web

echo ">> Stage a temporary self-signed cert so nginx can start with the 443 block"
$COMPOSE run --rm --entrypoint sh certbot -c "
  mkdir -p '$LIVE' &&
  openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
    -keyout '$LIVE/privkey.pem' -out '$LIVE/fullchain.pem' -subj '/CN=$DOMAIN'"

echo ">> Start nginx (serves :80 ACME challenge + :443 with the dummy cert)"
$COMPOSE up -d nginx

echo ">> Delete the dummy cert and request the real one via webroot"
$COMPOSE run --rm --entrypoint sh certbot -c "
  rm -rf '$LIVE' /etc/letsencrypt/archive/$DOMAIN /etc/letsencrypt/renewal/$DOMAIN.conf"
$COMPOSE run --rm --entrypoint certbot certbot certonly \
  --webroot -w /var/www/certbot \
  -d "$DOMAIN" --email "$EMAIL" --agree-tos --no-eff-email

echo ">> Reload nginx with the real certificate"
$COMPOSE exec nginx nginx -s reload

echo ">> Done. https://$DOMAIN/ is live."
