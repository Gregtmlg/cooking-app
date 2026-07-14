#!/bin/bash
# Déploiement : tire les images validées par la CI et redémarre si elles ont changé.
# Exécuté par cooking-deploy.timer. Silencieux quand il n'y a rien à faire.

set -uo pipefail
# NOTE : pas de `set -e`. Un échec de `pull` (réseau coupé, GHCR indisponible)
# ne doit PAS être traité comme une panne : c'est un non-événement.
# Le prochain tick réessaiera. L'application en cours n'est jamais touchée.

cd /srv/apps/cooking || exit 1

before=$(docker compose images -q 2>/dev/null)

if ! docker compose pull --quiet 2>/dev/null; then
    echo "Registre injoignable — nouvelle tentative au prochain tick." >&2
    exit 0        # ← exit 0 : ce n'est PAS un échec du service
fi

after=$(docker compose images -q 2>/dev/null)

if [ "$before" = "$after" ]; then
    exit 0        # rien de neuf : on se tait
fi

echo "==> Nouvelle image détectée — déploiement."
docker compose up -d
echo "==> Déployé. Images en service :"
docker compose images

# Purge les images qui ne sont plus référencées par aucun conteneur.
docker image prune -f