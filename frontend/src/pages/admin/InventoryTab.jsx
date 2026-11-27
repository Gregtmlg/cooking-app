// src/pages/admin/InventoryTab.jsx
// Vue d'ensemble en lecture seule — l'équivalent web de `python -m app.cli inventory`.

import { useOutletContext } from 'react-router-dom'
import { AccountBadges, Badge } from './Badges'
import { groupNames } from './format'
import styles from './Admin.module.css'

export default function InventoryTab() {
  const { inventory } = useOutletContext()

  return (
    <div className={styles.stack}>
      <section>
        <h3 className={styles.sectionTitle}>Comptes ({inventory.accounts.length})</h3>
        <ul className={styles.cards}>
          {inventory.accounts.map((account) => (
            <li key={account.id} className={account.is_system ? `${styles.card} ${styles.muted}` : styles.card}>
              <div className={styles.cardHead}>
                <strong>#{account.id} {account.username}</strong>
                <AccountBadges account={account} />
                <span className={styles.meta}>{account.active_sessions} session(s) active(s)</span>
              </div>
              <ul className={styles.profileList}>
                {account.profiles.map((profile) => (
                  <li key={profile.id}>
                    {profile.display_name} (#{profile.id}) — {groupNames(profile.groups, inventory.groups)}
                    {' '}— thème : {profile.theme ?? 'neutre'}
                    {profile.deactivated_at && <> <Badge kind="off">désactivé</Badge></>}
                  </li>
                ))}
              </ul>
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h3 className={styles.sectionTitle}>Groupes ({inventory.groups.length})</h3>
        <ul className={styles.plainList}>
          {inventory.groups.map((group) => (
            <li key={group.slug}>
              {group.name} ({group.slug}) — {group.members} membre(s)
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}
