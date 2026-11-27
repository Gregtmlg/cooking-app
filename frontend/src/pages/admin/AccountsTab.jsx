// src/pages/admin/AccountsTab.jsx
// Comptes, en lecture seule (J6a). Les actions (créer, reset, ajouter un profil,
// désactiver, purger) arrivent au J6b — jamais sur le compte Système.

import { useOutletContext } from 'react-router-dom'
import { AccountBadges } from './Badges'
import { formatDate } from './format'
import styles from './Admin.module.css'

export default function AccountsTab() {
  const { inventory } = useOutletContext()

  return (
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
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
