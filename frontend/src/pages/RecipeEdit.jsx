import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getRecipe, updateRecipe } from '../api/recipes'

function RecipeEdit() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    title: '',
    description: '',
    instructions: '',
    prep_time: '',
    cook_time: '',
    servings: ''
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    // à compléter — charger la recette et pré-remplir le form
    async function fetchRecipe() {
      try {
        const data = await getRecipe(id)
        setForm({
          title: data.title,
          description: data.description ?? '',
          instructions: data.instructions,
          prep_time: data.prep_time ?? '',
          cook_time: data.cook_time ?? '',
          servings: data.servings ?? ''
        })
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchRecipe()
  }, [id])

  function handleChange(e) {
    // identique à RecipeCreate
    const { name, value } = e.target
    setForm({ ...form, [name]: value })
  }

  async function handleSubmit(e) {
    e.preventDefault()  // empêche le rechargement de page
    // à compléter — valider le titre, construire data, appeler updateRecipe(id, data)
    // puis naviguer vers `/recipes/${id}`
    if (!form.title.trim()) {
        setError('Votre recette doit avoir un nom.')
        return
      }
    try {
      const data = {
        ...form,
        prep_time: parseInt(form.prep_time),
        cook_time: parseInt(form.cook_time),
        servings: parseInt(form.servings)
      }

      await updateRecipe(id, data)
      navigate(`/recipes/${id}`)
    } catch (err) {
      setError(err.message)
    }
  }

  if (loading) return <p>Chargement...</p>
  if (error) return <p>Erreur : {error}</p>

  return (
    // identique à RecipeCreate, titre "Modifier la recette"
    // bouton "Enregistrer" au lieu de "Créer"
    <div>
      <h2>Modifier la recette</h2>
      {error && <p>Erreur : {error}</p>}
      <form onSubmit={handleSubmit} onKeyDown={(e) => {
  if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
    e.preventDefault()
  }
}}>
        <div>
          <label for="title">Nom de la recette</label>
          <input name="title" value={form.title} onChange={handleChange} placeholder="Sauce Jiper" />
        </div>
        <div>
          <label for="description">Description</label>
          <textarea name="description" value={form.description} onChange={handleChange} placeholder="Une sauce délicieuse pour accompagner vos pâtes." />
        </div>
        <div>
          <label for="prep_time">Temps de préparation (minutes)</label>
          <input type="number" name="prep_time" value={form.prep_time} onChange={handleChange} placeholder="10" />
        </div>
        <div>
          <label for="cook_time">Temps de cuisson (minutes)</label>
          <input type="number" name="cook_time" value={form.cook_time} onChange={handleChange} placeholder="30" />
        </div>
        <div>
          <label for="servings">Nombre de portions</label>
          <input type="number" name="servings" value={form.servings} onChange={handleChange} placeholder="6" />
        </div>
        <div>
          <label for="instructions">Instructions</label>
          <textarea name="instructions" value={form.instructions} onChange={handleChange} placeholder="Mélanger les ingrédients... Pétrir la pâte..." />
        </div>
          <button type="submit">Enregistrer la recette</button>
      </form>
    </div>
  )
}

export default RecipeEdit