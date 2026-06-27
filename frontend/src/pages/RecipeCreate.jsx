import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { createRecipe, getIngredients } from '../api/recipes'

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
  const [ingredients, setIngredients] = useState([
    { ingredient_name: '', quantity: '', unit: '' }
  ])
  const [allIngredients, setAllIngredients] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    async function fetchIngredients() {
      try {
        const data = await getIngredients()
        setAllIngredients(data)
      } catch (err) {
        console.error('Impossible de charger les ingrédients', err)
      }
    }
    fetchIngredients()
  }, [])

  function handleChange(e) {
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
      await createRecipe(data)
      navigate('/')
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div>
      <h2>Créer une recette</h2>
      {error && <p>Erreur : {error}</p>}
      <form onSubmit={handleSubmit} onKeyDown={(e) => {
        if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') e.preventDefault()
      }}>
        <br />
        <div>
          <label>Nom de la recette</label>
          <input name="title" value={form.title} onChange={handleChange} placeholder="Sauce Jiper" />
        </div>
        <br />
        <div>
          <label>Description</label>
          <textarea name="description" value={form.description} onChange={handleChange} />
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
          <label>Instructions</label>
          <textarea name="instructions" value={form.instructions} onChange={handleChange} />
        </div>
        <br />
        <div>
          <label>Temps de préparation (min)</label>
          <input type="number" name="prep_time" value={form.prep_time} onChange={handleChange} />
        </div>
        <br />
        <div>
          <label>Temps de cuisson (min)</label>
          <input type="number" name="cook_time" value={form.cook_time} onChange={handleChange} />
        </div>
        <br />
        <div>
          <label>Portions</label>
          <input type="number" name="servings" value={form.servings} onChange={handleChange} />
        </div>
        <br />
        
        <button type="submit">Enregistrer la recette</button>
      </form>
    </div>
  )
}

export default RecipeCreate