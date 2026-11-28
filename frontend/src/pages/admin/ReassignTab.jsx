// src/pages/admin/ReassignTab.jsx
// Réattributions (J6b-2). Seul onglet qui charge ses PROPRES données (les recettes ne
// servent qu'ici) ; l'inventaire, lui, vient d'AdminPage. Filtre « Système seulement »
// côté client (décision F/Q3) : il trie ce que l'admin a déjà le droit de voir.

import { useCallback, useEffect, useState } from 'react'
import { generatePath, Link, useOutletContext } from 'react-router-dom'
import { getAdminRecipes, reassignRecipe } from '../../api/admin'
import { errorMessage } from '../../api/client'
import { ROUTES } from '../../routes'
import { Badge } from './Badges'
import useInlineAction from './useInlineAction'
import styles from './Admin.module.css'

const LOAD_ERROR = 'Impossible de charger les recettes.'

function ownerLabel(owner) {
  return owner ? `${owner.display_name} (compte ${owner.account_username})` : 'sans propriétaire'
}

function RecipeRow({ recipe, candidates, reloadRecipes }) {
  const { busy, run } = useInlineAction()
  const [selected, setSelected] = useState('')
  const options = candidates.filter((c) => c.id !== recipe.owner?.profile_id)

  async function handleReassign() {
    const target = options.find((c) => String(c.id) === selected)
    if (!target) return
    const ok = await run(
      () => reassignRecipe(recipe.id, target.id),
      `Recette « ${recipe.title} » réattribuée à « ${target.label} ».`,
      reloadRecipes,
    )
    if (ok) setSelected('')
  }

  const selectId = `owner-${recipe.id}`
  return (
    <tr>
      <td>{recipe.id}</td>
      <td>
        <Link to={generatePath(ROUTES.recipe, { id: recipe.id })}>{recipe.title}</Link>
      </td>
      <td>
        {ownerLabel(recipe.owner)}
        {recipe.owner?.is_system && <> <Badge kind="system">Système</Badge></>}
      </td>
      <td>
        <span className={styles.inlineForm}>
          <label htmlFor={selectId} className={styles.srOnly}>Nouveau propriétaire de « {recipe.title} »</label>
          <select id={selectId} value={selected} onChange={(e) => setSelected(e.target.value)} disabled={busy}>
            <option value="">Nouveau propriétaire…</option>
            {options.map((c) => (
              <option key={c.id} value={c.id}>{c.label}</option>
            ))}
          </select>
          <button type="button" className={styles.actionButton} disabled={busy || !selected} onClick={handleReassign}>
            Réattribuer
          </button>
        </span>
      </td>
    </tr>
  )
}

export default function ReassignTab() {
  const { inventory } = useOutletContext()
  const [recipes, setRecipes] = useState(null)
  const [loadError, setLoadError] = useState(null)
  const [systemOnly, setSystemOnly] = useState(true) // décision (b) : filtre actif par défaut

  // Chargement initial — même motif qu'AdminPage (setState dans le callback, `ignore`).
  useEffect(() => {
    let ignore = false
    getAdminRecipes()
      .then((data) => {
        if (!ignore) setRecipes(data)
      })
      .catch((err) => {
        if (!ignore) setLoadError(errorMessage(err, LOAD_ERROR))
      })
    return () => {
      ignore = true
    }
  }, [])

  // Relecture après une réattribution (passée à afterAction : relire PUIS annoncer).
  const reloadRecipes = useCallback(async () => {
    try {
      setRecipes(await getAdminRecipes())
      setLoadError(null)
    } catch (err) {
      setLoadError(errorMessage(err, LOAD_ERROR))
    }
  }, [])

  // Nouveaux propriétaires proposés (décisions E3 / E3-bis, G4) : profils ACTIFS hors
  // Système et hors compte admin (modérateur, pas auteur), plus le profil Système.
  // Choix d'options seulement — aucune règle serveur.
  const candidates = inventory.accounts.filter((account) => !account.is_admin).flatMap((account) =>
    account.profiles
      .filter((profile) => account.is_system || !profile.deactivated_at)
      .map((profile) => ({
        id: profile.id,
        label: account.is_system ? 'Système' : `${profile.display_name} (compte ${account.username})`,
      })),
  )

  if (loadError && !recipes) return <p className={styles.error} role="alert">{loadError}</p>
  if (!recipes) return <p>Chargement…</p>

  const shown = systemOnly ? recipes.filter((r) => r.owner?.is_system) : recipes

  return (
    <div>
      {loadError && <p className={styles.error} role="alert">{loadError}</p>}
      <div className={styles.toolbar}>
        <label className={styles.checkbox}>
          <input type="checkbox" checked={systemOnly} onChange={(e) => setSystemOnly(e.target.checked)} />
          Recettes de Système seulement ({recipes.filter((r) => r.owner?.is_system).length} / {recipes.length})
        </label>
      </div>

      {shown.length === 0 ? (
        <p className={styles.meta}>
          {systemOnly ? "Aucune recette n'appartient à Système." : 'Aucune recette.'}
        </p>
      ) : (
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>#</th>
                <th>Recette</th>
                <th>Propriétaire</th>
                <th>Réattribuer à</th>
              </tr>
            </thead>
            <tbody>
              {shown.map((recipe) => (
                <RecipeRow key={recipe.id} recipe={recipe} candidates={candidates} reloadRecipes={reloadRecipes} />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
