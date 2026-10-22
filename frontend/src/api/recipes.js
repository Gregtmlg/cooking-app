// Couche d'accès à l'API. Toutes les fonctions retournent directement response.data.

import api  from './client'

export async function getRecipes() {
    const response = await api.get('/api/v1/recipes/')
    return response.data
}

export async function getRecipe(id) {
    const response = await api.get(`/api/v1/recipes/${id}`)
    return response.data
}

export async function createRecipe(data) {
    const response = await api.post('/api/v1/recipes/', data)
    return response.data
}

export async function updateRecipe(id, data) {
    const response = await api.patch(`/api/v1/recipes/${id}`, data)
    return response.data
}

export async function deleteRecipe(id) {
    await api.delete(`/api/v1/recipes/${id}`)
}

export async function getIngredients() {
    const response = await api.get('/api/v1/ingredients/')
    return response.data
}
export async function getAudienceOptions() {
    // Pas de barre finale : URL canonique de la route (cf. dette redirect_slashes).
    const response = await api.get('/api/v1/recipes/audience-options')
    return response.data
}

// --- Audience : traduction écran ⇄ API (cf. cahier des charges §7.2) ---------------
// Écran (AudienceSelect) : un tableau de clés — ['all'] | ['private'] | ['famille', …] | [].
// API : { visible_to_all, audience: [slugs] } en entrée ; audience: [{ slug, name }] en sortie.
// Seule cette couche connaît la forme du JSON : les pages ne manipulent que des clés.

export function toApiAudience(selection) {
    if (selection.includes('all')) return { visible_to_all: true, audience: [] }
    if (selection.includes('private')) return { visible_to_all: false, audience: [] }
    return { visible_to_all: false, audience: selection } // [] → « Moi uniquement » aussi
}

export function fromApiAudience(recipe) {
    if (recipe.visible_to_all) return ['all']
    if (recipe.audience.length === 0) return ['private']
    return recipe.audience.map((group) => group.slug)
}