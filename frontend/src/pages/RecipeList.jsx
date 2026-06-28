import { useState, useEffect } from 'react'
import { getRecipes } from '../api/recipes'
import { Link } from 'react-router-dom'
import styles from './RecipeList.module.css'

function RecipeList() {
  const [recipes, setRecipes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function fetchRecipes() {
      try {
        const data = await getRecipes()
        setRecipes(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchRecipes()
  }, [])

  if (loading) return <p>Chargement...</p>
  if (error) return <p>Erreur : {error}</p>

  return (
    <div>
      <h2 className={styles.title}>Recettes</h2>
      {recipes.length === 0 ? (
        <p>Aucune recette pour le moment.</p>
      ) : (
        <div className={styles.grid}>
          {recipes.map((recipe) => (
            <Link to={`/recipes/${recipe.id}`} className={styles.card} key={recipe.id}>
              <div className={styles.cardImage}></div>
              <h3 className={styles.cardTitle}>{recipe.title}</h3>
              <p className={styles.cardMeta}>
                {recipe.prep_time && <span>{recipe.prep_time} min</span>}
                {recipe.prep_time && recipe.servings && <span>·</span>}
                {recipe.servings && <span>{recipe.servings} pers.</span>}
              </p>
              </Link>
          ))}
        </div>
      )}
    </div>
  )
}

export default RecipeList