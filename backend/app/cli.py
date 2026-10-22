import typer

from app.db.session import SessionLocal
from app.services.account_service import (
    AccountServiceError,
    create_account,
    reset_password,
)
from app.services.group_service import (
    GroupServiceError,
    add_profile_to_group,
    remove_profile_from_group,
)
from app.services.profile_service import ProfileServiceError, find_profile

cli = typer.Typer(
    help="Administration de cooking-app (comptes et profils).",
)


@cli.command("create-account")
def create_account_cmd(
    username: str = typer.Option(..., help="Identifiant de connexion (unique)."),
    group: str | None = typer.Option(
        None, help="Slug du groupe (famille, chuteam…). Omis : utilisateur sans groupe."
    ),
    password: str = typer.Option(
        ...,
        prompt=True,
        confirmation_prompt=True,
        hide_input=True,
        help="Mot de passe provisoire (l'utilisateur devra le changer).",
    ),
    display_name: str = typer.Option(None, help="Nom affiché du 1er profil (défaut : username)."),
    admin: bool = typer.Option(False, "--admin", help="Fait de ce compte un administrateur."),
):
    """Crée un compte + son premier profil (rattaché à un groupe ou sans groupe)."""

    db = SessionLocal()
    try:
        account = create_account(
            db,
            username=username,
            password=password,
            group_slug=group,
            display_name=display_name,
            is_admin=admin,
        )
        profile = account.profiles[0]
        group_label = f"groupe « {group} »" if group else "sans groupe"
        typer.secho(
            f"✓ Compte « {account.username} » créé "
            f"(profil « {profile.display_name} », {group_label}"
            f"{', admin' if admin else ''}). "
            f"Changement de mot de passe requis à la 1re connexion.",
            fg=typer.colors.GREEN,
        )

    except (AccountServiceError, GroupServiceError) as e:
        typer.secho(f"✗ {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1) from None

    finally:
        db.close()


@cli.command("reset-password")
def reset_password_cmd(
    username: str = typer.Option(..., help="Identifiant du compte à réinitialiser."),
    password: str = typer.Option(
        ...,
        prompt=True,
        confirmation_prompt=True,
        hide_input=True,
        help="Nouveau mot de passe provisoire.",
    ),
):
    """Réinitialise le mot de passe d'un compte (met must_change_password à True)."""
    db = SessionLocal()
    try:
        account = reset_password(db, username=username, new_password=password)
        suite = (
            "Changement de mot de passe requis à la prochaine connexion."
            if account.must_change_password
            else "Compte partagé (multi-profils) : ce mot de passe est définitif."
        )
        typer.secho(
            f"✓ Mot de passe du compte « {account.username} » réinitialisé. {suite}",
            fg=typer.colors.GREEN,
        )
    except AccountServiceError as e:
        typer.secho(f"✗ {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1) from None
    finally:
        db.close()


@cli.command("add-to-group")
def add_to_group_cmd(
    username: str = typer.Option(..., help="Identifiant du compte à ajouter au groupe."),
    group: str = typer.Option(..., help="Slug du groupe (famille, chuteam ...)."),
    profile: str | None = typer.Option(
        None, help="Nom affiché du profil (facultatif si le compte n'a qu'un profil)."
    ),
):
    """Ajoute un profil à un groupe"""

    db = SessionLocal()
    try:
        target = find_profile(db, username=username, display_name=profile)
        add_profile_to_group(db, profile=target, group_slug=group)
        typer.secho(
            f"✓ Profil « {target.display_name} » ajouté au groupe « {group} ».",
            fg=typer.colors.GREEN,
        )

    except (ProfileServiceError, GroupServiceError) as e:
        typer.secho(f"✗ {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1) from None

    finally:
        db.close()


@cli.command("remove-from-group")
def remove_from_group_cmd(
    username: str = typer.Option(..., help="Identifiant du compte à retirer du groupe."),
    group: str = typer.Option(..., help="Slug du groupe (famille, chuteam ...)."),
    profile: str | None = typer.Option(
        None, help="Nom affiché du profil (facultatif si le compte n'a qu'un profil)."
    ),
):
    """Retire un profil d'un groupe"""

    db = SessionLocal()
    try:
        target = find_profile(db, username=username, display_name=profile)
        remove_profile_from_group(db, profile=target, group_slug=group)
        typer.secho(
            f"✓ Profil « {target.display_name} » retiré du groupe « {group} ».",
            fg=typer.colors.GREEN,
        )

    except (ProfileServiceError, GroupServiceError) as e:
        typer.secho(f"✗ {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1) from None

    finally:
        db.close()


if __name__ == "__main__":
    cli()
