import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { getRecipe, deleteRecipe } from '../api/recipes'
import style from './RecipeDetail.module.css'

// Capitalise la première lettre d'un nom d'ingrédient pour l'affichage.
// Les noms sont stockés en minuscules en base (normalisés à la création).
function capitalize(str) {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1)
}

function RecipeDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [recipe, setRecipe] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function fetchRecipe() {
      try {
        const data = await getRecipe(id)
        setRecipe(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchRecipe()
  }, [id])

  if (loading) return <p>Chargement...</p>
  if (error) return <p>Erreur : {error}</p>

  async function handleDelete() {
    const confirmed = window.confirm('Êtes-vous sûr de vouloir supprimer cette recette ?')
    if (confirmed) {
      try {
        await deleteRecipe(id)
        navigate('/')
      } catch (err) {
        setError(err.message)
      }
    }
  }

  return (
    <div>
      <Link to="/" className={styles.backLink}>← Retour à la liste</Link>
      <div className={styles.card}>
        <h2 className={styles.title}>{recipe.title}</h2>
        <p className={styles.description}>{recipe.description}</p>

        <div className={styles.meta}>
          {recipe.prep_time && <span>Préparation : {recipe.prep_time} min</span>}
          {recipe.cook_time && <span>Cuisson : {recipe.cook_time} min</span>}
          {recipe.servings && <span>{recipe.servings} personnes</span>}
        </div>

        <h3 className={styles.sectionTitle}>Ingrédients</h3>
        {recipe.ingredients.length === 0 ? (
          <p>Aucun ingrédient n'a été listé.</p>
        ) : (
          <ul className={styles.ingredientGrid}>
            {recipe.ingredients.map((ing, index) => {
              const name = capitalize(ing.ingredient.name)
              return (
                <li key={index} className={styles.ingredientItem}>
                  {ing.quantity === null
                    ? name
                    : ing.unit === null
                    ? `${ing.quantity} ${name}`
                    : `${ing.quantity} ${ing.unit} de ${name}`}
                </li>
              )
            })}
          </ul>
        )}

        <h3 className={styles.sectionTitle}>Instructions</h3>
        <p className={styles.instructions}>{recipe.instructions}</p>

        <div className={styles.actions}>
          <Link to={`/recipes/${id}/edit`} className={styles.editButton}>Modifier</Link>
          <button onClick={handleDelete} className={styles.deleteButton}>Supprimer</button>
        </div>
      </div>
    </div>
  )
}

export default RecipeDetail