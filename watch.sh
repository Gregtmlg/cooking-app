#!/bin/bash

REPO_DIR="/srv/apps/cooking-app"
CHECK_INTERVAL=60

echo "==> Surveillance démarrée (intervalle : ${CHECK_INTERVAL}s)"

while true; do
    cd "$REPO_DIR"

    # Récupère les infos du dépôt distant sans modifier le code local
    if ! git fetch origin main --quiet; then
        echo "==> [$(date)] Échec de la récupération des informations du dépôt distant.">&2
        sleep "$CHECK_INTERVAL"
        continue
    fi

    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/main)

    if [ "$LOCAL" != "$REMOTE" ]; then
        echo "==> Nouveau commit détecté — déploiement en cours..."
        bash deploy.sh
        echo "==> Déploiement terminé à $(date)"
    fi

    sleep "$CHECK_INTERVAL"
done
