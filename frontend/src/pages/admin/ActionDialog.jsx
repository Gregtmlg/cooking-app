// src/pages/admin/ActionDialog.jsx
// Cycle de vie d'UNE action admin, écrit une seule fois pour toutes :
//   valider la saisie (confort) → appeler le serveur → relire + annoncer (afterAction)
//   → fermer. En cas de refus du serveur, son message s'affiche DANS le dialogue,
//   qui reste ouvert (on sait encore ce qu'on tentait, on peut annuler).
// Le dialogue générique (components/Dialog) ne connaît rien de l'admin ; celui-ci oui.

import { useState } from 'react'
import { useOutletContext } from 'react-router-dom'
import { errorMessage } from '../../api/client'
import Dialog from '../../components/Dialog'
import styles from './Admin.module.css'

export default function ActionDialog({
  title,
  submitLabel,
  danger = false,
  canSubmit = true,
  validate, // () => message d'erreur ou null — confort, avant tout envoi
  run, // async () => message de succès ; lève si le serveur refuse
  onClose,
  children,
}) {
  const { afterAction } = useOutletContext()
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  async function handleSubmit() {
    const problem = validate?.()
    if (problem) {
      setError(problem)
      return
    }
    setError(null)
    setBusy(true)
    try {
      const message = await run()
      await afterAction(message)
      onClose() // le parent retire le dialogue : plus de setState ici ensuite
    } catch (err) {
      setError(errorMessage(err, 'Action impossible pour le moment. Réessayez.'))
      setBusy(false)
    }
  }

  return (
    <Dialog
      title={title}
      error={error}
      onSubmit={handleSubmit}
      onCancel={onClose}
      submitLabel={submitLabel}
      submitDisabled={!canSubmit}
      busy={busy}
      danger={danger}
    >
      {children}
    </Dialog>
  )
}

// Le serveur compare le nom retapé après strip (+ NFC pour un identifiant). Le front
// compare de la même façon : jamais plus strictement, sinon il bloquerait une saisie
// que le serveur accepterait. Le bouton grisé n'est qu'un confort ; le serveur juge.
function sameName(typed, name) {
  return typed.trim().normalize('NFC') === name.normalize('NFC')
}

export function PurgeDialog({ what, name, consequence, run, onClose }) {
  const [typed, setTyped] = useState('')
  return (
    <ActionDialog
      title={`Purger ${what} « ${name} »`}
      submitLabel="Purger définitivement"
      danger
      canSubmit={sameName(typed, name)}
      run={() => run(typed)}
      onClose={onClose}
    >
      <p>
        Action <strong>irréversible</strong>. {consequence} Ses recettes sont transférées au
        compte Système.
      </p>
      <div>
        <label htmlFor="purge-confirm">
          Pour confirmer, tapez exactement : <strong className={styles.typeMe}>{name}</strong>
        </label>
        <input
          id="purge-confirm"
          value={typed}
          onChange={(e) => setTyped(e.target.value)}
          autoComplete="off"
          autoFocus
        />
      </div>
    </ActionDialog>
  )
}
