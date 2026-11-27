// src/pages/admin/AccountsTab.jsx
// Comptes. Les boutons ne recalculent AUCUNE règle de droit : ils lisent des champs
// fournis par le serveur (is_system, is_active) ; les refus (anti-verrouillage,
// mot de passe provisoire…) viennent du serveur et s'affichent dans le dialogue.

import { useState } from 'react'
import { useOutletContext } from 'react-router-dom'
import {
  AddProfileDialog,
  CreateAccountDialog,
  DeactivateAccountDialog,
  PurgeAccountDialog,
  ResetPasswordDialog,
} from './AccountDialogs'
import { AccountBadges } from './Badges'
import { formatDate } from './format'
import styles from './Admin.module.css'

const DIALOGS = {
  reset: ResetPasswordDialog,
  addProfile: AddProfileDialog,
  deactivate: DeactivateAccountDialog,
  purge: PurgeAccountDialog,
}

export default function AccountsTab() {
  const { inventory } = useOutletContext()
  // Quel dialogue est ouvert, et sur QUEL compte : c'est l'onglet qui le sait.
  // null = aucun ; { kind: 'create' } ; { kind: 'reset', account } …
  const [dialog, setDialog] = useState(null)
  const close = () => setDialog(null)
  const OpenDialog = dialog && dialog.kind !== 'create' ? DIALOGS[dialog.kind] : null

  return (
    <div>
      <div className={styles.toolbar}>
        <button type="button" className={styles.primaryButton} onClick={() => setDialog({ kind: 'create' })}>
          Créer un compte
        </button>
      </div>

      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>#</th>
              <th>Identifiant</th>
              <th>État</th>
              <th>Profils actifs</th>
              <th>Sessions</th>
              <th>Créé le</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {inventory.accounts.map((account) => (
              <tr key={account.id} className={account.is_system ? styles.muted : undefined}>
                <td>{account.id}</td>
                <td>{account.username}</td>
                <td><AccountBadges account={account} /></td>
                <td>
                  {account.profiles.filter((p) => !p.deactivated_at).length} / {account.profiles.length}
                </td>
                <td>{account.active_sessions}</td>
                <td>{formatDate(account.created_at)}</td>
                <td>
                  {/* Compte Système : aucune action (drapeau fourni par le serveur). */}
                  {!account.is_system && (
                    <span className={styles.rowActions}>
                      <button type="button" className={styles.actionButton} onClick={() => setDialog({ kind: 'reset', account })}>
                        Réinitialiser le mot de passe
                      </button>
                      <button type="button" className={styles.actionButton} onClick={() => setDialog({ kind: 'addProfile', account })}>
                        Ajouter un profil
                      </button>
                      {account.is_active ? (
                        <button type="button" className={styles.actionButton} onClick={() => setDialog({ kind: 'deactivate', account })}>
                          Désactiver
                        </button>
                      ) : (
                        // Purge réservée aux comptes inactifs (le serveur l'exige — 409 sinon).
                        <button type="button" className={styles.dangerButton} onClick={() => setDialog({ kind: 'purge', account })}>
                          Purger
                        </button>
                      )}
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {dialog?.kind === 'create' && <CreateAccountDialog onClose={close} />}
      {OpenDialog && <OpenDialog account={dialog.account} onClose={close} />}
    </div>
  )
}
