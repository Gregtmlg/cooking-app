import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { errorMessage } from '../api/client'
import {
  fromApiAudience,
  getAudienceOptions,
  getIngredients,
  getRecipe,
  toApiAudience,
  updateRecipe,
} from '../api/recipes'
import AudienceSelect from '../components/AudienceSelect'
import styles from './RecipeForm.module.css'

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
  const [audience, setAudience] = useState([])
  const [audienceGroups, setAudienceGroups] = useState([])
  const [loading, setLoading] = useState(true)
  // Deux erreurs distinctes : celle du CHARGEMENT remplace la page (rien à éditer) ;
  // celle de l'ENVOI s'affiche au-dessus du formulaire, sans perdre la saisie.
  const [loadError, setLoadError] = useState(null)
  const [error, setError] = useState(null)

  // Au montage : la recette, les ingrédients (autocomplétion) et les groupes
  // pour lesquels ce profil peut publier.
  useEffect(() => {
  async function fetchData() {
    try {
      // Les trois requêtes sont indépendantes : on les lance en parallèle avec Promise.all
      // pour réduire le temps de chargement (au lieu de les enchaîner l'une après l'autre).
      const [recipeData, ingredientsData, groupsData] = await Promise.all([
        getRecipe(id),
        getIngredients(),
        getAudienceOptions(),
      ])
      // Arrivé ici par l'URL sans en avoir le droit : le serveur refuserait l'envoi,
      // inutile d'afficher un formulaire voué à l'échec.
      if (!recipeData.can_edit) {
        setLoadError("Vous ne pouvez pas modifier cette recette : seul son auteur le peut.")
        return
      }
      setForm({
        title: recipeData.title,
        description: recipeData.description ?? '',
        instructions: recipeData.instructions,
        prep_time: recipeData.prep_time ?? '',
        cook_time: recipeData.cook_time ?? '',
        servings: recipeData.servings ?? ''
      })
      // Transforme le format API { ingredient: { name }, quantity, unit }
      // vers le format state { ingredient_name, quantity, unit } attendu par le formulaire.
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
      // API → puces.
      setAudience(fromApiAudience(recipeData))
      // Groupes affichables = ceux où l'on peut publier + ceux DÉJÀ sur la recette
      // (un groupe quitté reste conservable, règle J4b). Map → pas de doublon par slug.
      const groups = new Map(groupsData.map((group) => [group.slug, group]))
      recipeData.audience.forEach((group) => groups.set(group.slug, group))
      setAudienceGroups([...groups.values()])
    } catch (err) {
      setLoadError(errorMessage(err, 'Impossible de charger la recette.'))
    } finally {
      setLoading(false)
    }
  }
  fetchData()
}, [id])

  function handleChange(e) {
    const { name, value } = e.target
    setForm({ ...form, [name]: value })
  }

  // Met à jour un champ d'une ligne ingrédient sans modifier le state directement.
  // .map() retourne un nouveau tableau ; seule la ligne à l'index `index` est modifiée.
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
        // Filtre les lignes vides avant envoi, normalise les noms en minuscules
        // et convertit quantity en float (les inputs retournent toujours des strings).
        ingredients: ingredients
          .filter(ing => ing.ingredient_name.trim() !== '')
          .map(ing => ({
            ingredient_name: ing.ingredient_name.trim().toLowerCase(),
            quantity: ing.quantity ? parseFloat(ing.quantity) : null,
            unit: ing.unit.trim() || null
          })),
        // Toujours les DEUX champs d'audience (règle « tout ou rien » du PATCH).
        ...toApiAudience(audience),
        }
        await updateRecipe(id, data)
        navigate(`/recipes/${id}`)
      } catch (err) {
        setError(errorMessage(err))
      }
    }

  if (loading) return <p>Chargement...</p>
  if (loadError) return <p>{loadError}</p>

  return (
    <div>
      <h2 className={styles.title}>Modifier la recette</h2>
      {error && <p className={styles.error}>Erreur : {error}</p>}
      <form
      className={styles.form} 
      onSubmit={handleSubmit} 
      onKeyDown={(e) => {
        if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {e.preventDefault()}
      }}>
        <div className={styles.field}>
          <label>Nom de la recette</label>
          <input name="title" value={form.title} onChange={handleChange} placeholder="Sauce Jiper" />
        </div>

        <div className={styles.field}>
          <label htmlFor="description">Description</label>
          <textarea name="description" value={form.description} onChange={handleChange} placeholder="Une sauce délicieuse pour accompagner vos pâtes." />
        </div>

        <div className={styles.field}>
        <label>Ingrédients</label>
        <datalist id="ingredients-list">
          {allIngredients.map(ing => (
            <option key={ing.id} value={ing.name.charAt(0).toUpperCase() + ing.name.slice(1)} />
          ))}
        </datalist>
        {ingredients.map((ing, index) => (
          <div key={index} className={styles.ingredientRow}>
            <input
              className={styles.ingredientName}
              list="ingredients-list"
              name="ingredient_name"
              value={ing.ingredient_name}
              onChange={(e) => handleIngredientChange(index, e)}
              placeholder="Tomate"
            />
            <input
              className={styles.ingredientQuantity}
              type="number"
              name="quantity"
              value={ing.quantity}
              onChange={(e) => handleIngredientChange(index, e)}
              placeholder="200"
            />
            <input
              className={styles.ingredientUnit}
              name="unit"
              value={ing.unit}
              onChange={(e) => handleIngredientChange(index, e)}
              placeholder="g"
            />
            <button
              type="button"
              className={styles.removeButton}
              onClick={() => handleRemoveIngredient(index)}
              aria-label="Supprimer l'ingrédient"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 6h18" />
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                <line x1="10" y1="11" x2="10" y2="17" />
                <line x1="14" y1="11" x2="14" y2="17" />
              </svg>
            </button>
          </div>
        ))}
        <button type="button" className={styles.addButton} onClick={handleAddIngredient}>
          + Ajouter un ingrédient
        </button>
        </div>
        <div className={styles.field}>
          <label>Instructions</label>
          <textarea name="instructions" value={form.instructions} onChange={handleChange} />
        </div>

        <div className={styles.field}>
          <label>Temps de préparation (min)</label>
          <input type="number" name="prep_time" value={form.prep_time} onChange={handleChange} />
        </div>

        <div className={styles.field}>
          <label>Temps de cuisson (min)</label>
          <input type="number" name="cook_time" value={form.cook_time} onChange={handleChange} />
        </div>

        <div className={styles.field}>
          <label>Portions</label>
          <input type="number" name="servings" value={form.servings} onChange={handleChange} />
        </div>

        <div className={styles.field}>
          <label htmlFor="audience">Visible par</label>
          <AudienceSelect
            id="audience"
            value={audience}
            onChange={setAudience}
            groups={audienceGroups}
          />
        </div>

        <button type="submit" className={styles.submitButton}>Enregistrer la recette</button>
      </form>
    </div>
  )
}

export default RecipeEdit