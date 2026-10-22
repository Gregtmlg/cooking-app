// src/components/AudienceSelect.jsx
// Sélecteur d'audience : des puces supprimables + un <select> « Ajouter… ».
//
// MÉCANISME PROVISOIRE (décision J5) : le <select> natif sera remplacé par le
// combobox réutilisable de la tâche 5. La logique (valeur, règles d'exclusivité)
// et l'interface du composant (props) resteront les mêmes.
//
// Props :
//   id       — pour relier le <label> de la page au <select>
//   value    — tableau de clés : ['all'] | ['private'] | ['famille', 'chuteam'] | []
//   onChange — reçoit le NOUVEAU tableau (le composant ne garde aucun état)
//   groups   — groupes proposables [{ slug, name }], fournis par le serveur

import styles from './AudienceSelect.module.css'

const ALL = { key: 'all', label: 'Tous' }
const PRIVATE = { key: 'private', label: 'Moi uniquement' }

export default function AudienceSelect({ id, value, onChange, groups }) {
  // Texte affiché dans une puce, à partir de sa clé.
  function labelOf(key) {
    if (key === ALL.key) return ALL.label
    if (key === PRIVATE.key) return PRIVATE.label
    return groups.find((group) => group.slug === key)?.name ?? key
  }

  // Règles d'exclusivité → options encore proposables :
  // - « Tous » ou « Moi uniquement » choisi : plus rien à ajouter ;
  // - au moins un groupe choisi : seulement les AUTRES groupes ;
  // - rien de choisi : tout est possible.
  const exclusive = value.includes(ALL.key) || value.includes(PRIVATE.key)
  const remainingGroups = groups
    .filter((group) => !value.includes(group.slug))
    .map((group) => ({ key: group.slug, label: group.name }))
  let available = []
  if (!exclusive) {
    available = value.length === 0 ? [ALL, ...remainingGroups, PRIVATE] : remainingGroups
  }

  function handleAdd(e) {
    const key = e.target.value
    if (key) onChange([...value, key])
  }

  function handleRemove(key) {
    onChange(value.filter((k) => k !== key))
  }

  return (
    <div className={styles.wrapper}>
      {value.length > 0 && (
        <ul className={styles.chips}>
          {value.map((key) => (
            <li key={key} className={styles.chip}>
              {labelOf(key)}
              <button
                type="button"
                className={styles.remove}
                onClick={() => handleRemove(key)}
                aria-label={`Retirer « ${labelOf(key)} »`}
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      )}

      {value.length === 0 && (
        <p className={styles.hint}>Aucune audience choisie : la recette sera visible par vous seul.</p>
      )}

      {available.length > 0 && (
        // value="" en permanence : le <select> sert de « bouton d'ajout »,
        // il revient sur son libellé après chaque choix.
        <select id={id} className={styles.add} value="" onChange={handleAdd}>
          <option value="">{value.length === 0 ? 'Choisir…' : 'Ajouter un groupe…'}</option>
          {available.map((option) => (
            <option key={option.key} value={option.key}>
              {option.label}
            </option>
          ))}
        </select>
      )}
    </div>
  )
}
