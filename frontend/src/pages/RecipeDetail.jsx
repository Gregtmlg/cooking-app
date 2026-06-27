import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { getRecipe, deleteRecipe } from '../api/recipes'

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
    // à compléter — même structure que RecipeList
    // mais appelle getRecipe(id)
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

  // à compléter — même guards que RecipeList
  if (loading) return <p>Chargement...</p>
  if (error) return <p>Erreur : {error}</p>

  async function handleDelete() {
    // à compléter :
    // 1. demander confirmation avec window.confirm
    // 2. si confirmé : appeler deleteRecipe(id)
    // 3. naviguer vers '/'
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
    // à compléter — afficher les champs de recipe
    // + un <Link> pour modifier
    // + un <button> pour supprimer qui appelle handleDelete
    <div>
      <div>
      <Link to="/">Retour à la liste</Link>
      </div>
      <div>
        <h2>{recipe.title}</h2>
        <br />
        <p>{recipe.description}</p>
        <br />
        <p>Temps de préparation : {recipe.prep_time} minutes</p>
        <br />
        <p>Temps de cuisson : {recipe.cook_time} minutes</p>
        <br />
        <p>Nombre de portions : {recipe.servings}</p>
        <br />
        <h3>Ingrédients :</h3>
        {recipe.ingredients.length === 0 ? (
          <p>Aucun ingrédient n'a été listé.</p>
        ) : (
          <ul>
            {recipe.ingredients.map((ing, index) => {
              const name = capitalize(ing.ingredient.name)
              return (
              <li key={index}>
                <p>{ing.quantity === null
                  ? name
                  : ing.unit === null
                  ? `${ing.quantity} ${name}`
                  : `${ing.quantity} ${ing.unit} de ${name}`
                  }</p>
              </li>
            )})}
          </ul>
        )}
        <br />
        <h3>Instructions :</h3>
        <p>{recipe.instructions}</p>
        <br />
        <Link to={`/recipes/${id}/edit`}>Modifier</Link>
        <button onClick={handleDelete}>Supprimer</button>
      </div>
    </div>
  )
}

export default RecipeDetail