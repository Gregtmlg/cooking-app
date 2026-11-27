// src/pages/admin/useInlineAction.js
// Hook « maison » (une fonction dont le nom commence par `use` et qui utilise des
// hooks) : le cycle d'une action SANS dialogue, écrit une seule fois —
// appel serveur → relire + annoncer (afterAction) ; refus → relire AUSSI, puis bandeau
// (reportError). Un refus comme « déjà membre » prouve que l'écran était en retard sur
// le serveur : on se resynchronise pour que la liste montre la réalité.
// `busy` grise les boutons pendant la requête (pas de double clic).

import { useState } from 'react'
import { useOutletContext } from 'react-router-dom'
import { errorMessage } from '../../api/client'

export default function useInlineAction() {
  const { afterAction, reload, reportError } = useOutletContext()
  const [busy, setBusy] = useState(false)

  // Renvoie true si l'action a réussi (l'appelant peut alors vider sa sélection).
  async function run(call, message, ...extraReloads) {
    setBusy(true)
    try {
      await call()
      await afterAction(message, ...extraReloads)
      return true
    } catch (err) {
      await Promise.all([reload(), ...extraReloads.map((r) => r())])
      reportError(errorMessage(err, 'Action impossible pour le moment. Réessayez.'))
      return false
    } finally {
      setBusy(false)
    }
  }

  return { busy, run }
}
