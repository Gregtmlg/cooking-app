from app.services.inventory_service import get_inventory
from app.services.session_service import create_session


def test_inventory_lists_accounts_profiles_and_groups(db_session, world):
    inv = get_inventory(db_session)

    assert [a.username for a in inv.accounts] == [
        "auteur",
        "lambda",
        "fam",
        "chu",
        "multi",
        "admin",
    ]
    multi = next(a for a in inv.accounts if a.username == "multi")
    assert multi.profiles[0].groups == ["famille", "chuteam"]
    assert multi.profiles[0].theme == "famille"  # défaut : groupe le plus ancien
    assert next(a for a in inv.accounts if a.username == "admin").is_admin
    assert {g.slug: g.members for g in inv.groups} == {"famille": 2, "chuteam": 2}


def test_inventory_counts_only_active_sessions(db_session, account):
    create_session(db_session, account.id)
    create_session(db_session, account.id)
    account.sessions[0].expires_at = account.sessions[0].created_at.replace(year=2000)
    db_session.commit()

    assert get_inventory(db_session).accounts[0].active_sessions == 1


def test_lambda_profile_has_neutral_theme(db_session, world):
    lam = next(a for a in get_inventory(db_session).accounts if a.username == "lambda")
    assert lam.profiles[0].groups == []
    assert lam.profiles[0].theme is None
