#!/bin/bash
set -e

echo "==> Récupération du code..."
git pull

echo "==> Reconstruction des images..."
docker compose build

echo "==> Redémarrage des conteneurs..."
docker compose up -d

echo "==> Déploiement terminé."
docker compose ps
