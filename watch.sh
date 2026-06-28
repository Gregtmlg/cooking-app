#!/bin/bash

REPO_DIR="/srv/apps/cooking-app"
CHECK_INTERVAL=60

echo "==> Surveillance démarrée (intervalle : ${CHECK_INTERVAL}s)"

while true; do
    cd "$REPO_DIR"

    # Récupère les infos du dépôt distant sans modifier le code local
    git fetch origin master --quiet

    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/master)

    if [ "$LOCAL" != "$REMOTE" ]; then
        echo "==> Nouveau commit détecté — déploiement en cours..."
        bash deploy.sh
        echo "==> Déploiement terminé à $(date)"
    fi

    sleep "$CHECK_INTERVAL"
done
