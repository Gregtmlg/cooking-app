import { Link, Outlet } from 'react-router-dom'
import styles from './Layout.module.css'

function Layout() {
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
      </header>
      <main className={styles.main}>
        <Outlet />
      </main>
    </div>
  )
}

export default Layout