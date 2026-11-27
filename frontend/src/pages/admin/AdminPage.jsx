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

import { useCallback, useEffect, useState } from 'react'
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
  const afterAction = useCallback(
    async (message) => {
      await reload()
      setNotice(message)
    },
    [reload],
  )

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

      {notice && (
        <p className={styles.notice} role="status">
          <span>{notice}</span>
          <button type="button" className={styles.noticeClose} onClick={() => setNotice(null)} aria-label="Fermer le message">
            ×
          </button>
        </p>
      )}
      {error && <p className={styles.error} role="alert">{error}</p>}
      {loading && <p>Chargement…</p>}
      {inventory && <Outlet context={{ inventory, reload, afterAction }} />}
    </div>
  )
}
