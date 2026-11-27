// src/pages/admin/Badges.jsx
// Pastilles d'état. Elles RECOPIENT des champs calculés par le serveur
// (is_active dérivé, is_system, deactivated_at…) : aucune n'est déduite ici.

import styles from './Admin.module.css'

export function Badge({ kind = 'neutral', children }) {
  return <span className={`${styles.badge} ${styles[`badge_${kind}`]}`}>{children}</span>
}

export function AccountBadges({ account }) {
  return (
    <span className={styles.badges}>
      {account.is_system && <Badge kind="system">Système</Badge>}
      {account.is_admin && <Badge kind="admin">admin</Badge>}
      {account.must_change_password && <Badge kind="warning">mdp provisoire</Badge>}
      {!account.is_active && !account.is_system && <Badge kind="off">désactivé</Badge>}
    </span>
  )
}

export function ProfileBadge({ profile }) {
  return profile.deactivated_at ? <Badge kind="off">désactivé</Badge> : <Badge kind="on">actif</Badge>
}
