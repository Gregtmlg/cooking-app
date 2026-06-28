import { useState, useEffect } from 'react'
import { getRecipes } from '../api/recipes'
import { Link } from 'react-router-dom'

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
      <h2>Recettes 🍳</h2>
      {recipes.length === 0 ? (
        <p>Aucune recette pour le moment.</p>
      ) : (
        <ul>
          {recipes.map((recipe) => (
            <li key={recipe.id}>
              <Link to={`/recipes/${recipe.id}`}>{recipe.title}</Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default RecipeList