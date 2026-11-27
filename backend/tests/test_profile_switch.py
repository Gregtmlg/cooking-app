"""J6a — « Changer de profil » : la règle vit dans le service, le front l'affiche.

Le 3e test est celui qui compte : si quelqu'un comptait `profiles` au lieu de
`active_profiles`, seul lui tomberait (réflexe mutation du J5).
"""

from app.services.account_service import deactivate_profile
from app.services.profile_service import can_switch_profile


def test_single_profile_cannot_switch(account):
    assert can_switch_profile(account) is False


def test_two_active_profiles_can_switch(multi_profile_account):
    assert can_switch_profile(multi_profile_account) is True


def test_deactivated_profile_does_not_count(db_session, multi_profile_account):
    deactivate_profile(db_session, multi_profile_account.profiles[1])
    db_session.refresh(multi_profile_account)
    assert can_switch_profile(multi_profile_account) is False


def test_me_exposes_can_switch_profile(client, account, multi_profile_account):
    client.post("/api/v1/auth/login", json={"username": "Louise", "password": "motdepasse123"})
    assert client.get("/api/v1/auth/me").json()["can_switch_profile"] is False

    client.post("/api/v1/auth/logout")
    r = client.post("/api/v1/auth/login", json={"username": "Famille", "password": "motdepasse123"})
    assert r.json()["can_switch_profile"] is True  # aussi dans la réponse de /login
