// src/pages/admin/ProfilesTab.jsx
// Tous les profils, à plat, en lecture seule (J6a). Actions au J6b.

import { useOutletContext } from 'react-router-dom'
import { Badge, ProfileBadge } from './Badges'
import { formatDate, groupNames } from './format'
import styles from './Admin.module.css'

export default function ProfilesTab() {
  const { inventory } = useOutletContext()
  // Aplatit comptes → profils en gardant le compte de chacun (simple mise en forme).
  const rows = inventory.accounts.flatMap((account) =>
    account.profiles.map((profile) => ({ account, profile })),
  )

  return (
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
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
