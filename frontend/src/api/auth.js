// src/api/auth.js
// Couche d'accès à l'authentification. Fonctions « bêtes » : elles traduisent
// HTTP en JS et lèvent sur erreur. L'interprétation (401 = anonyme…) appartient
// à AuthContext, pas à cette couche.
// Conversion camelCase (JS) → snake_case (API) faite ici, et seulement ici.

import api from './client'

export async function login(username, password) {
    const response = await api.post('/api/v1/auth/login', { username, password })
    return response.data
}

export async function logout() {
    await api.post('/api/v1/auth/logout')
}

export async function getMe() {
    const response = await api.get('/api/v1/auth/me')
    return response.data
}

export async function getProfiles() {
    const response = await api.get('/api/v1/auth/profiles')
    return response.data
}

export async function selectProfile(profileId) {
    const response = await api.post('/api/v1/auth/select-profile', { profile_id: profileId })
    return response.data
}

export async function changePassword(oldPassword, newPassword) {
    const response = await api.post('/api/v1/auth/change-password', {
        old_password: oldPassword,
        new_password: newPassword
    })
    return response.data
}