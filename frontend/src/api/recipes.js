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