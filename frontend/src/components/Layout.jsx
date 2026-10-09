import { Link, Outlet } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import styles from './Layout.module.css'

function Layout() {
  // Layout est sous RequireProfile : profile n'est jamais null ici.
  const { profile, logout } = useAuth()

  return (
    <div>
      <header className={styles.header}>
        <h1 className={styles.logo}>
          <Link to="/">Dingé Kitchen</Link>
        </h1>
        <nav className={styles.nav}>
          <Link className={styles.navLink} to="/recipes">Recettes</Link>
          <Link className={styles.navLink} to="/recipes/new">Créer une recette</Link>
        </nav>
        <div className={styles.session}>
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