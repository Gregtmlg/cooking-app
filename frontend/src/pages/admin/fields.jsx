// src/pages/admin/fields.jsx
// Champs de formulaire partagés par les dialogues du back-office.

import { MAX_LENGTH, MIN_LENGTH } from '../../auth/password'
import styles from './Admin.module.css'

// Mot de passe provisoire + confirmation (décision E5 : il sera dicté de vive voix).
export function PasswordFields({ password, setPassword, confirmation, setConfirmation }) {
  return (
    <>
      <div>
        <label htmlFor="admin-password">Mot de passe provisoire</label>
        <input
          id="admin-password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="new-password"
          required
        />
        <p className={styles.hint}>Entre {MIN_LENGTH} et {MAX_LENGTH} caractères.</p>
      </div>
      <div>
        <label htmlFor="admin-password-confirm">Confirmer le mot de passe</label>
        <input
          id="admin-password-confirm"
          type="password"
          value={confirmation}
          onChange={(e) => setConfirmation(e.target.value)}
          autoComplete="new-password"
          required
        />
      </div>
    </>
  )
}

// Choix d'un groupe parmi ceux de l'inventaire ; vide = sans groupe.
export function GroupSelect({ id, value, onChange, groups }) {
  return (
    <div>
      <label htmlFor={id}>Groupe</label>
      <select id={id} value={value} onChange={(e) => onChange(e.target.value)}>
        <option value="">Sans groupe</option>
        {groups.map((group) => (
          <option key={group.slug} value={group.slug}>
            {group.name}
          </option>
        ))}
      </select>
    </div>
  )
}
