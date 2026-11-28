// src/pages/admin/GroupsTab.jsx
// Groupes et leurs membres (J6b-2) : ajout et retrait DIRECTS, sans dialogue
// (décision D4/F1) — le message en haut de page confirme, la liste est relue.

import { useState } from 'react'
import { useOutletContext } from 'react-router-dom'
import { addToGroup, removeFromGroup } from '../../api/admin'
import { ProfileBadge } from './Badges'
import useInlineAction from './useInlineAction'
import styles from './Admin.module.css'

function GroupCard({ group, accounts }) {
  const { busy, run } = useInlineAction()
  const [selected, setSelected] = useState('') // id du profil à ajouter, en texte

  // Membres = profils qui portent ce slug (donnée serveur, simplement filtrée).
  const members = accounts.flatMap((account) =>
    account.profiles
      .filter((profile) => profile.groups.includes(group.slug))
      .map((profile) => ({ account, profile })),
  )
  // Proposés à l'ajout (décisions F2, G4) : actifs, hors Système, hors compte admin
  // (« admin sans groupe », cahier §7.1), pas déjà membres. Simple choix d'options :
  // le serveur reste juge (409 « déjà membre », Système refusé).
  const candidates = accounts
    .filter((account) => !account.is_system && !account.is_admin)
    .flatMap((account) =>
      account.profiles
        .filter((profile) => !profile.deactivated_at && !profile.groups.includes(group.slug))
        .map((profile) => ({ account, profile })),
    )

  async function handleAdd() {
    const entry = candidates.find(({ profile }) => String(profile.id) === selected)
    if (!entry) return
    const ok = await run(
      () => addToGroup(entry.profile.id, group.slug),
      `« ${entry.profile.display_name} » ajouté au groupe ${group.name}.`,
    )
    if (ok) setSelected('')
  }

  function handleRemove(profile) {
    run(
      () => removeFromGroup(profile.id, group.slug),
      `« ${profile.display_name} » retiré du groupe ${group.name}.`,
    )
  }

  const selectId = `add-to-${group.slug}`
  return (
    <li className={styles.card}>
      <div className={styles.cardHead}>
        <strong>{group.name}</strong>
        <span className={styles.meta}>{group.slug} — {group.members} membre(s)</span>
      </div>

      {members.length === 0 ? (
        <p className={styles.meta}>Aucun membre.</p>
      ) : (
        <ul className={styles.memberList}>
          {members.map(({ account, profile }) => (
            <li key={profile.id} className={styles.memberRow}>
              <span>
                {profile.display_name} (#{profile.id}) — compte {account.username}{' '}
                <ProfileBadge profile={profile} />
              </span>
              <button type="button" className={styles.actionButton} disabled={busy} onClick={() => handleRemove(profile)}>
                Retirer
              </button>
            </li>
          ))}
        </ul>
      )}

      <div className={styles.inlineForm}>
        <label htmlFor={selectId} className={styles.srOnly}>Profil à ajouter au groupe {group.name}</label>
        <select id={selectId} value={selected} onChange={(e) => setSelected(e.target.value)} disabled={busy || candidates.length === 0}>
          <option value="">{candidates.length ? 'Ajouter un profil…' : 'Aucun profil à ajouter'}</option>
          {candidates.map(({ account, profile }) => (
            <option key={profile.id} value={profile.id}>
              {profile.display_name} (compte {account.username})
            </option>
          ))}
        </select>
        <button type="button" className={styles.actionButton} disabled={busy || !selected} onClick={handleAdd}>
          Ajouter
        </button>
      </div>
    </li>
  )
}

export default function GroupsTab() {
  const { inventory } = useOutletContext()
  return (
    <ul className={styles.cards}>
      {inventory.groups.map((group) => (
        <GroupCard key={group.slug} group={group} accounts={inventory.accounts} />
      ))}
    </ul>
  )
}
