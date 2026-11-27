// src/pages/admin/ProfileDialogs.jsx
// Dialogues des actions sur les PROFILS (seuls les profils portent un état — J5a).

import { deactivateProfile, purgeProfile, reactivateProfile } from '../../api/admin'
import ActionDialog, { PurgeDialog } from './ActionDialog'
import { purgeMessage } from './format'

export function DeactivateProfileDialog({ profile, onClose }) {
  return (
    <ActionDialog
      title={`Désactiver le profil « ${profile.display_name} »`}
      submitLabel="Désactiver"
      danger
      run={async () => {
        await deactivateProfile(profile.id)
        return `Profil « ${profile.display_name} » désactivé.`
      }}
      onClose={onClose}
    >
      <p>
        Il disparaît de la sélection de profil et les sessions où il est actif sont fermées.
        Ses recettes restent en place. Réversible.
      </p>
    </ActionDialog>
  )
}

export function ReactivateProfileDialog({ profile, onClose }) {
  return (
    <ActionDialog
      title={`Réactiver le profil « ${profile.display_name} »`}
      submitLabel="Réactiver"
      run={async () => {
        await reactivateProfile(profile.id)
        return `Profil « ${profile.display_name} » réactivé.`
      }}
      onClose={onClose}
    >
      <p>Il réapparaît dans la sélection de profil (et son compte redevient actif).</p>
    </ActionDialog>
  )
}

export function PurgeProfileDialog({ profile, onClose }) {
  return (
    <PurgeDialog
      what="le profil"
      name={profile.display_name}
      consequence="Le profil est supprimé (et son compte aussi s'il n'en a plus aucun)."
      run={async (confirm) => purgeMessage(`Profil « ${profile.display_name} »`, await purgeProfile(profile.id, confirm))}
      onClose={onClose}
    />
  )
}
