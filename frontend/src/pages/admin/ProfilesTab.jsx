// src/pages/admin/ProfilesTab.jsx
// Tous les profils, à plat. Désactiver / réactiver / purger : seuls les profils portent
// un état (J5a) — c'est aussi ici qu'on « réactive un compte » (décision E2).

import { useState } from 'react'
import { useOutletContext } from 'react-router-dom'
import { Badge, ProfileBadge } from './Badges'
import { formatDate, groupNames } from './format'
import { DeactivateProfileDialog, PurgeProfileDialog, ReactivateProfileDialog } from './ProfileDialogs'
import styles from './Admin.module.css'

const DIALOGS = {
  deactivate: DeactivateProfileDialog,
  reactivate: ReactivateProfileDialog,
  purge: PurgeProfileDialog,
}

export default function ProfilesTab() {
  const { inventory } = useOutletContext()
  const [dialog, setDialog] = useState(null) // { kind, profile } ou null
  const close = () => setDialog(null)
  const OpenDialog = dialog ? DIALOGS[dialog.kind] : null

  // Aplatit comptes → profils en gardant le compte de chacun (simple mise en forme).
  const rows = inventory.accounts.flatMap((account) =>
    account.profiles.map((profile) => ({ account, profile })),
  )

  return (
    <div>
      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>#</th>
              <th>Nom</th>
              <th>Compte</th>
              <th>Groupes</th>
              <th>Thème</th>
              <th>État</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(({ account, profile }) => (
              <tr key={profile.id} className={account.is_system ? styles.muted : undefined}>
                <td>{profile.id}</td>
                <td>{profile.display_name}</td>
                <td>
                  {account.username}
                  {account.is_system && <> <Badge kind="system">Système</Badge></>}
                </td>
                <td>{groupNames(profile.groups, inventory.groups)}</td>
                <td>{profile.theme ?? 'neutre'}</td>
                <td>
                  <ProfileBadge profile={profile} />
                  {profile.deactivated_at && (
                    <span className={styles.meta}> depuis le {formatDate(profile.deactivated_at)}</span>
                  )}
                </td>
                <td>
                  {!account.is_system && (
                    <span className={styles.rowActions}>
                      {profile.deactivated_at ? (
                        <>
                          <button type="button" className={styles.actionButton} onClick={() => setDialog({ kind: 'reactivate', profile })}>
                            Réactiver
                          </button>
                          <button type="button" className={styles.dangerButton} onClick={() => setDialog({ kind: 'purge', profile })}>
                            Purger
                          </button>
                        </>
                      ) : (
                        <button type="button" className={styles.actionButton} onClick={() => setDialog({ kind: 'deactivate', profile })}>
                          Désactiver
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

      {OpenDialog && <OpenDialog profile={dialog.profile} onClose={close} />}
    </div>
  )
}
