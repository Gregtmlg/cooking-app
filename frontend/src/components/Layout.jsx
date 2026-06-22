import { Link } from 'react-router-dom'

function Layout({ children }) {
    return (
        <div>
            <header>
                <h1><Link to="/">Cooking App</Link></h1>
                <nav>
                    <Link to="/">Recettes</Link>
                    <Link to="/recipes/new">Créer une recette</Link>
                </nav>
            </header>
            <main>
                {children}
            </main>
        </div>
    )
}

export default Layout