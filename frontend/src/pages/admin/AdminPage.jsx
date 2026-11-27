// src/pages/admin/AdminPage.jsx
// Back-office (J6a) : UNE page, des onglets qui sont des routes enfants (/admin/comptes…).
// Le retour arrière, le rechargement et les favoris gardent donc l'onglet ouvert.
//
// Cette page charge l'inventaire UNE fois et le confie à son <Outlet /> : chaque onglet
// le lit avec useOutletContext(), sans nouvel appel.
//
// Après une action (J6b), les onglets appellent `afterAction(message)` : on RELIT le
// serveur plutôt que de corriger la liste à la main (sinon il faudrait recopier ses
// règles en React — principe 8), PUIS on affiche le message : il décrit ainsi ce que
// la liste montre déjà.
//
// Elle ne redirige jamais : un 401 est traité par l'intercepteur + RequireAuth ;
// un 403 (droits perdus) n'a pas de code → la page affiche simplement l'erreur.

import { useCallback, useEffect, useRef, useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import { getInventory } from '../../api/admin'
import { errorMessage } from '../../api/client'
import { ROUTES } from '../../routes'
import styles from './Admin.module.css'

const TABS = [
  { to: ROUTES.adminInventory, label: 'Inventaire' },
  { to: ROUTES.adminAccounts, label: 'Comptes' },
  { to: ROUTES.adminProfiles, label: 'Profils' },
  { to: ROUTES.adminGroups, label: 'Groupes' },
  { to: ROUTES.adminReassign, label: 'Réattributions' },
]

const LOAD_ERROR = "Impossible de charger l'inventaire."

// Un appel, un résultat : { inventory } ou { error }. Hors du composant (fonction pure).
async function fetchInventory() {
  try {
    return { inventory: await getInventory(), error: null }
  } catch (err) {
    return { error: errorMessage(err, LOAD_ERROR) }
  }
}

export default function AdminPage() {
  const [state, setState] = useState({ loading: true, inventory: null, error: null })
  const [notice, setNotice] = useState(null) // message de succès de la dernière action
  const [actionError, setActionError] = useState(null) // refus d'une action SANS dialogue
  const feedbackRef = useRef(null)

  // Chargement initial — même motif qu'AuthProvider : setState seulement dans le
  // callback de la réponse, et drapeau `ignore` si la page est quittée avant.
  useEffect(() => {
    let ignore = false
    fetchInventory().then((result) => {
      if (!ignore) setState((prev) => ({ ...prev, ...result, loading: false }))
    })
    return () => {
      ignore = true
    }
  }, [])

  // Relecture à la demande (J6b). En cas d'échec, l'inventaire précédent reste affiché
  // avec le message d'erreur au-dessus.
  const reload = useCallback(async () => {
    const result = await fetchInventory()
    setState((prev) => ({ ...prev, ...result, loading: false }))
  }, [])

  // Point UNIQUE de fin d'action : relire d'abord, annoncer ensuite (décision E4).
  // `extraReloads` : ce qu'un onglet charge lui-même (les recettes des Réattributions).
  const afterAction = useCallback(
    async (message, ...extraReloads) => {
      await Promise.all([reload(), ...extraReloads.map((r) => r())])
      setActionError(null)
      setNotice(message)
    },
    [reload],
  )

  // Refus du serveur pour une action SANS dialogue (groupes, réattribution) : il
  // s'affiche dans le bandeau, puisqu'il n'y a pas de dialogue pour le porter.
  const reportError = useCallback((message) => {
    setNotice(null)
    setActionError(message)
  }, [])

  // Sur mobile, le bandeau est en haut : on le ramène à l'écran dès qu'il change,
  // sinon une action faite en bas d'une longue liste paraîtrait sans réponse.
  useEffect(() => {
    if (notice || actionError) feedbackRef.current?.scrollIntoView({ block: 'nearest' })
  }, [notice, actionError])

  const { loading, inventory, error } = state

  return (
    <div>
      <h2 className={styles.title}>Administration</h2>
      <nav className={styles.tabs} aria-label="Onglets d'administration">
        {TABS.map((tab) => (
          <NavLink
            key={tab.to}
            to={tab.to}
            className={({ isActive }) => (isActive ? `${styles.tab} ${styles.tabActive}` : styles.tab)}
          >
            {tab.label}
          </NavLink>
        ))}
      </nav>

      {/* Retour de la dernière action : refus (sans dialogue) ou succès. */}
      <div ref={feedbackRef}>
        {actionError && (
          <p className={styles.errorBox} role="alert">
            {actionError}
          </p>
        )}
        {notice && (
          <p className={styles.notice} role="status">
            <span>{notice}</span>
            <button
              type="button"
              className={styles.noticeClose}
              onClick={() => setNotice(null)}
              aria-label="Fermer le message"
            >
              ×
            </button>
          </p>
        )}
      </div>
      {error && <p className={styles.error} role="alert">{error}</p>}
      {loading && <p>Chargement…</p>}
      {inventory && <Outlet context={{ inventory, reload, afterAction, reportError }} />}
    </div>
  )
}
