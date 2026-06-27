import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getRecipe, updateRecipe, getIngredients } from '../api/recipes'

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
  const [ingredients, setIngredients] = useState([
    { ingredient_name: '', quantity: '', unit: '' }
  ])
  const [allIngredients, setAllIngredients] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
  async function fetchData() {
    try {
      const [recipeData, ingredientsData] = await Promise.all([
        getRecipe(id),
        getIngredients()
      ])
      setForm({
        title: recipeData.title,
        description: recipeData.description ?? '',
        instructions: recipeData.instructions,
        prep_time: recipeData.prep_time ?? '',
        cook_time: recipeData.cook_time ?? '',
        servings: recipeData.servings ?? ''
      })
      setIngredients(
        recipeData.ingredients && recipeData.ingredients.length > 0
          ? recipeData.ingredients.map(ri => ({
              ingredient_name: ri.ingredient.name,
              quantity: ri.quantity ?? '',
              unit: ri.unit ?? ''
            }))
          : [{ ingredient_name: '', quantity: '', unit: '' }]
      )
      setAllIngredients(ingredientsData)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }
  fetchData()
}, [id])

  function handleChange(e) {
    // identique à RecipeCreate
    const { name, value } = e.target
    setForm({ ...form, [name]: value })
  }

  function handleIngredientChange(index, e) {
    const { name, value } = e.target
    const updated = ingredients.map((ing, i) =>
      i === index ? { ...ing, [name]: value } : ing
    )
    setIngredients(updated)
  }

  function handleAddIngredient() {
    setIngredients([...ingredients, { ingredient_name: '', quantity: '', unit: '' }])
  }

  function handleRemoveIngredient(index) {
    setIngredients(ingredients.filter((_, i) => i !== index))
  }

  async function handleSubmit(e) {
      e.preventDefault()
      if (!form.title.trim()) {
        setError('Votre recette doit avoir un nom.')
        return
      }
      try {
        const data = {
        ...form,
        prep_time: form.prep_time ? parseInt(form.prep_time) : null,
        cook_time: form.cook_time ? parseInt(form.cook_time) : null,
        servings: form.servings ? parseInt(form.servings) : null,
        ingredients: ingredients
          .filter(ing => ing.ingredient_name.trim() !== '')
          .map(ing => ({
            ingredient_name: ing.ingredient_name.trim().toLowerCase(),
            quantity: ing.quantity ? parseFloat(ing.quantity) : null,
            unit: ing.unit.trim() || null
          }))
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
    // identique à RecipeCreate, titre "Modifier la recette"Pourtan
    // bouton "Enregistrer" au lieu de "Créer"
    <div>
      <h2>Modifier la recette</h2>
      {error && <p>Erreur : {error}</p>}
      <form onSubmit={handleSubmit} onKeyDown={(e) => {
  if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
    e.preventDefault()
  }
}}>
        <br />
        <div>
          <label for="title">Nom de la recette</label>
          <input name="title" value={form.title} onChange={handleChange} placeholder="Sauce Jiper" />
        </div>
        <br />
        <div>
          <label for="description">Description</label>
          <textarea name="description" value={form.description} onChange={handleChange} placeholder="Une sauce délicieuse pour accompagner vos pâtes." />
        </div>
        <br />
        <div>
        <label>Ingrédients</label>
        <datalist id="ingredients-list">
          {allIngredients.map(ing => (
            <option key={ing.id} value={ing.name.charAt(0).toUpperCase() + ing.name.slice(1)} />
          ))}
        </datalist>
        {ingredients.map((ing, index) => (
          <div key={index}>
            <input
              list="ingredients-list"
              name="ingredient_name"
              value={ing.ingredient_name}
              onChange={(e) => handleIngredientChange(index, e)}
              placeholder="Tomate"
            />
            <input
              type="number"
              name="quantity"
              value={ing.quantity}
              onChange={(e) => handleIngredientChange(index, e)}
              placeholder="200"
            />
            <input
              name="unit"
              value={ing.unit}
              onChange={(e) => handleIngredientChange(index, e)}
              placeholder="g"
            />
            <button type="button" onClick={() => handleRemoveIngredient(index)}>✕</button>
          </div>
          
        ))}
        </div>
        <button type="button" onClick={handleAddIngredient}>+ Ajouter un ingrédient</button>

        <br />
        <br />
        <div>
          <label for="instructions">Instructions</label>
          <textarea name="instructions" value={form.instructions} onChange={handleChange} placeholder="Mélanger les ingrédients... Pétrir la pâte..." />
        </div>
        <br />
        <div>
          <label for="prep_time">Temps de préparation (minutes)</label>
          <input type="number" name="prep_time" value={form.prep_time} onChange={handleChange} placeholder="10" />
        </div>
        <br />
        <div>
          <label for="cook_time">Temps de cuisson (minutes)</label>
          <input type="number" name="cook_time" value={form.cook_time} onChange={handleChange} placeholder="30" />
        </div>
        <br />
        <div>
          <label for="servings">Nombre de portions</label>
          <input type="number" name="servings" value={form.servings} onChange={handleChange} placeholder="6" />
        </div>

        <br />
          <button type="submit">Enregistrer la recette</button>
      </form>
    </div>
  )
}

export default RecipeEdit