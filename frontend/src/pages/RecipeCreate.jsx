import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createRecipe } from '../api/recipes'
import { getIngredients } from '../api/recipes'

function RecipeCreate() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    title: '',
    description: '',
    instructions: '',
    prep_time: '',
    cook_time: '',
    servings: ''
  })
  const [error, setError] = useState(null)

  function handleChange(e) {
    const { name, value } = e.target
    setForm({ ...form, [name]: value })
  }

  async function handleSubmit(e) {
    e.preventDefault()  // empêche le rechargement de page
    try {
      // à compléter :
      // 1. construire l'objet data avec les bons types
      // 2. appeler createRecipe(data)
      // 3. naviguer vers '/'
      const data = {
        ...form,
        prep_time: form.prep_time ? parseInt(form.prep_time) : null,
        cook_time: form.cook_time ? parseInt(form.cook_time) : null,
        servings: form.servings ? parseInt(form.servings) : null
      }
      if (!form.title.trim()) {
        setError('Votre recette doit avoir un nom.')
        return
      }

      await createRecipe(data)
      navigate('/')
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    // à compléter — un formulaire avec :
    // - un champ par propriété de la recette
    // - un bouton de soumission
    // - affichage de l'erreur si présente
    <div>
      <h2>Créer une recette</h2>
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
          <label for="instructions">Instructions</label>
          <textarea name="instructions" value={form.instructions} onChange={handleChange} placeholder="Mélanger les ingrédients... Pétrir la pâte..." />
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
          <button type="submit">Enregistrer la recette</button>
      </form>
    </div>
  )
}

export default RecipeCreate