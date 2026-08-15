import typer

from app.db.session import SessionLocal
from app.services.account_service import (
    AccountServiceError,
    create_account,
    reset_password,
)

cli = typer.Typer(
    help="Administration de cooking-app (comptes et profils).",
)


@cli.command("create-account")
def create_account_cmd(
    username: str = typer.Option(..., help="Identifiant de connexion (unique)."),
    group: str = typer.Option(..., help="Slug du groupe : famille / amis / ..."),
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
    """Crée un compte + son premier profil rattaché à un groupe."""

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
        typer.secho(
            f"✓ Compte « {account.username} » créé "
            f"(profil « {profile.display_name} », groupe « {group} »"
            f"{', admin' if admin else ''}). "
            f"Changement de mot de passe requis à la 1re connexion.",
            fg=typer.colors.GREEN,
        )

    except AccountServiceError as e:
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
        typer.secho(
            f"✓ Mot de passe du compte « {account.username} » réinitialisé. "
            f"Changement de mot de passe requis à la 1re connexion.",
            fg=typer.colors.GREEN,
        )
    except AccountServiceError as e:
        typer.secho(f"✗ {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1) from None
    finally:
        db.close()


if __name__ == "__main__":
    cli()
