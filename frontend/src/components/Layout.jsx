import { Link } from 'react-router-dom'
import styles from './Layout.module.css'

function Layout({ children }) {
    return (
        <div>
            <header className={styles.header}>
                <h1 className= {styles.logo}>
                    <Link to="/">Dingé Kitchen</Link>
                </h1>
                <nav className={styles.nav}>
                    <Link className={styles.navLink} to="/">Recettes</Link>
                    <Link className={styles.navLink} to="/recipes/new">Créer une recette</Link>
                </nav>
            </header>
            <main className={styles.main}>
                {children}
            </main>
        </div>
    )
}

export default Layout