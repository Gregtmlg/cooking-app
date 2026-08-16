import { Link } from 'react-router-dom'
import styles from './HomePage.module.css'

const navItems = [
    {label: 'Recettes', to: '/recipes', available: true},
    {label: 'Favoris', to: '/favorites', available: false},
    {label: 'Recommendations', to: '/recommendations', available: false},
]


function HomePage() {
  return (
    <div className={styles.hub}>
        <div className={styles.content}>
            <h1 className={styles.brand}>Dingé Kitchen</h1>
            <nav className={styles.menu}>
                {navItems.map((item) =>
                    item.available ? (
                        <Link
                        key={item.to}
                        to={item.to}
                        className={`${styles.item} ${styles.itemLink}`}
                        >
                        {item.label}
                        </Link>
                    ) : (
                        <span
                        key={item.to}
                        className={`${styles.item} ${styles.itemDisabled}`}
                        aria-disabled="true"
                        >
                        {item.label}
                        <span className={styles.soon}>bientôt</span>
                        </span>
                    )
                    )}
            </nav>
        </div>
    </div>
  )
}

export default HomePage