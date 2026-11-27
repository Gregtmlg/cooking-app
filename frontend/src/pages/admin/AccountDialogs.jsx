// src/pages/admin/AccountDialogs.jsx
// Dialogues des actions sur les COMPTES. Chacun garde l'état de son propre formulaire ;
// monté à l'ouverture, il repart vierge à chaque fois.

import { useState } from 'react'
import { useOutletContext } from 'react-router-dom'
import {
  addProfile,
  createAccount,
  deactivateAccount,
  purgeAccount,
  resetPassword,
} from '../../api/admin'
import { checkNewPassword } from '../../auth/password'
import ActionDialog, { PurgeDialog } from './ActionDialog'
import { GroupSelect, PasswordFields } from './fields'
import { purgeMessage } from './format'

export function CreateAccountDialog({ onClose }) {
  const { inventory } = useOutletContext()
  const [username, setUsername] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [group, setGroup] = useState('')
  const [password, setPassword] = useState('')
  const [confirmation, setConfirmation] = useState('')

  return (
    <ActionDialog
      title="Créer un compte"
      submitLabel="Créer le compte"
      validate={() => checkNewPassword(password, confirmation)}
      run={async () => {
        const account = await createAccount({ username, password, displayName, group })
        return `Compte « ${account.username} » créé. Mot de passe provisoire à transmettre.`
      }}
      onClose={onClose}
    >
      <div>
        <label htmlFor="new-username">Identifiant de connexion</label>
        <input
          id="new-username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoComplete="off"
          required
          autoFocus
        />
      </div>
      <div>
        <label htmlFor="new-display-name">Nom du premier profil (facultatif)</label>
        <input
          id="new-display-name"
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          placeholder="Par défaut : l'identifiant"
          autoComplete="off"
        />
      </div>
      <GroupSelect id="new-group" value={group} onChange={setGroup} groups={inventory.groups} />
      <PasswordFields
        password={password}
        setPassword={setPassword}
        confirmation={confirmation}
        setConfirmation={setConfirmation}
      />
    </ActionDialog>
  )
}

export function ResetPasswordDialog({ account, onClose }) {
  const [password, setPassword] = useState('')
  const [confirmation, setConfirmation] = useState('')

  return (
    <ActionDialog
      title={`Réinitialiser le mot de passe de « ${account.username} »`}
      submitLabel="Réinitialiser"
      validate={() => checkNewPassword(password, confirmation)}
      run={async () => {
        const updated = await resetPassword(account.id, password)
        // Le serveur décide si le changement sera forcé (compte mono-profil) ou non.
        return updated.must_change_password
          ? `Mot de passe de « ${updated.username} » réinitialisé : changement forcé à la prochaine connexion.`
          : `Mot de passe de « ${updated.username} » réinitialisé : définitif (compte partagé).`
      }}
      onClose={onClose}
    >
      <p>Toutes les sessions ouvertes de ce compte seront fermées.</p>
      <PasswordFields
        password={password}
        setPassword={setPassword}
        confirmation={confirmation}
        setConfirmation={setConfirmation}
      />
    </ActionDialog>
  )
}

export function AddProfileDialog({ account, onClose }) {
  const { inventory } = useOutletContext()
  const [displayName, setDisplayName] = useState('')
  const [group, setGroup] = useState('')

  return (
    <ActionDialog
      title={`Ajouter un profil au compte « ${account.username} »`}
      submitLabel="Ajouter le profil"
      run={async () => {
        const profile = await addProfile(account.id, { displayName, group })
        return `Profil « ${profile.display_name} » ajouté au compte « ${account.username} ».`
      }}
      onClose={onClose}
    >
      <div>
        <label htmlFor="add-profile-name">Nom du profil</label>
        <input
          id="add-profile-name"
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          autoComplete="off"
          required
          autoFocus
        />
      </div>
      <GroupSelect id="add-profile-group" value={group} onChange={setGroup} groups={inventory.groups} />
    </ActionDialog>
  )
}

export function DeactivateAccountDialog({ account, onClose }) {
  return (
    <ActionDialog
      title={`Désactiver le compte « ${account.username} »`}
      submitLabel="Désactiver"
      danger
      run={async () => {
        await deactivateAccount(account.id)
        return `Compte « ${account.username} » désactivé.`
      }}
      onClose={onClose}
    >
      <p>
        Tous ses profils actifs sont désactivés et ses sessions fermées. Ses recettes restent
        en place. Réversible : réactivez un de ses profils dans l'onglet Profils.
      </p>
    </ActionDialog>
  )
}

export function PurgeAccountDialog({ account, onClose }) {
  return (
    <PurgeDialog
      what="le compte"
      name={account.username}
      consequence="Le compte et tous ses profils sont supprimés."
      run={async (confirm) => purgeMessage(`Compte « ${account.username} »`, await purgeAccount(account.id, confirm), false)}
      onClose={onClose}
    />
  )
}
