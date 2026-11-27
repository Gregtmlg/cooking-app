// src/components/Dialog.jsx
// Dialogue modal RÉUTILISABLE, sur l'élément natif <dialog> (fond assombri, Échap,
// focus gardé dans le dialogue — sans bibliothèque). Composant « bête » : il ne sait
// pas sur quoi on agit ; le parent lui passe le contenu et les deux réactions.
//
// Ouvert = monté. Le parent l'affiche quand il a une cible, le retire sinon : chaque
// ouverture repart donc d'un formulaire vierge.
//
// <dialog> s'ouvre par une MÉTHODE (showModal), pas par une prop : la référence
// (useRef) donne accès à l'élément réel, et l'effet fait le lien au montage.

import { useEffect, useId, useRef } from 'react'
import styles from './Dialog.module.css'

export default function Dialog({
  title,
  children,
  error = null,
  onSubmit,
  onCancel,
  submitLabel,
  submitDisabled = false,
  busy = false, // requête en cours : on ne ferme pas, on ne renvoie pas
  danger = false,
}) {
  const ref = useRef(null)
  const titleId = useId()

  useEffect(() => {
    const dialog = ref.current
    dialog.showModal()
    return () => dialog.close()
  }, [])

  // Échap déclenche l'événement « cancel » : c'est le parent qui décide de fermer.
  function handleCancel(e) {
    e.preventDefault()
    if (!busy) onCancel()
  }

  function handleSubmit(e) {
    e.preventDefault() // Entrée valide le formulaire sans recharger la page
    onSubmit()
  }

  return (
    <dialog ref={ref} className={styles.dialog} onCancel={handleCancel} aria-labelledby={titleId}>
      <form onSubmit={handleSubmit}>
        <h3 id={titleId} className={styles.title}>{title}</h3>
        {error && (
          <p className={styles.error} role="alert">
            {error}
          </p>
        )}
        <div className={styles.body}>{children}</div>
        <div className={styles.actions}>
          <button type="button" className={styles.cancel} onClick={onCancel} disabled={busy}>
            Annuler
          </button>
          <button
            type="submit"
            className={danger ? `${styles.submit} ${styles.danger}` : styles.submit}
            disabled={submitDisabled || busy}
          >
            {busy ? 'En cours…' : submitLabel}
          </button>
        </div>
      </form>
    </dialog>
  )
}
