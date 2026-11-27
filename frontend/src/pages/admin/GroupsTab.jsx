// src/pages/admin/GroupsTab.jsx
// Groupes et leurs membres, en lecture seule (J6a). Ajout / retrait au J6b.

import { useOutletContext } from 'react-router-dom'
import { ProfileBadge } from './Badges'
import styles from './Admin.module.css'

export default function GroupsTab() {
  const { inventory } = useOutletContext()

  return (
    <ul className={styles.cards}>
      {inventory.groups.map((group) => {
        // Membres = profils qui portent ce slug (donnée serveur, simplement filtrée).
        const members = inventory.accounts.flatMap((account) =>
          account.profiles
            .filter((profile) => profile.groups.includes(group.slug))
            .map((profile) => ({ account, profile })),
        )
        return (
          <li key={group.slug} className={styles.card}>
            <div className={styles.cardHead}>
              <strong>{group.name}</strong>
              <span className={styles.meta}>{group.slug} — {group.members} membre(s)</span>
            </div>
            {members.length === 0 ? (
              <p className={styles.meta}>Aucun membre.</p>
            ) : (
              <ul className={styles.profileList}>
                {members.map(({ account, profile }) => (
                  <li key={profile.id}>
                    {profile.display_name} (#{profile.id}) — compte {account.username}{' '}
                    <ProfileBadge profile={profile} />
                  </li>
                ))}
              </ul>
            )}
          </li>
        )
      })}
    </ul>
  )
}
