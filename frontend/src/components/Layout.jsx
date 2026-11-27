import { Link, Outlet } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { ROUTES } from '../routes'
import { brandOf } from '../theme/theme'
import ThemeSelect from './ThemeSelect'
import styles from './Layout.module.css'

function Layout() {
  // Layout est sous RequireProfile : profile n'est jamais null ici.
  // is_admin et canSwitchProfile viennent du serveur (SessionRead) : l'en-tête
  // ne décide rien, il affiche ou masque (principe 8).
  const { account, profile, theme, canSwitchProfile, logout } = useAuth()

  return (
    <div>
      <header className={styles.header}>
        <h1 className={styles.logo}>
          <Link to={ROUTES.home}>{brandOf(theme)}</Link>
        </h1>
        <nav className={styles.nav}>
          <Link className={styles.navLink} to={ROUTES.recipes}>Recettes</Link>
          <Link className={styles.navLink} to={ROUTES.recipeNew}>Créer une recette</Link>
          {account.is_admin && (
            <Link className={styles.navLink} to={ROUTES.admin}>Administration</Link>
          )}
        </nav>
        <div className={styles.session}>
          <ThemeSelect />
          {canSwitchProfile && (
            <Link className={styles.navLink} to={ROUTES.selectProfile}>Changer de profil</Link>
          )}
          <span className={styles.profileName}>{profile.display_name}</span>
          <button className={styles.logoutButton} type="button" onClick={logout}>
            Se déconnecter
          </button>
        </div>
      </header>
      <main className={styles.main}>
        <Outlet />
      </main>
    </div>
  )
}

export default Layout
