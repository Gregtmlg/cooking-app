import axios from 'axios'

const api = axios.create({
    baseURL: 'http://localhost:8000'
})

export async function getRecipes() {
    const response = await api.get('/api/v1/recipes/')
    return response.data
}

export async function getRecipe(id) {
    const response = await api.get(`/api/v1/recipes/${id}/`)
    return response.data
}

export async function createRecipe(data) {
    const response = await api.post('/api/v1/recipes/', data)
    return response.data
}

export async function updateRecipe(id, data) {
    const response = await api.patch(`/api/v1/recipes/${id}/`, data)
    return response.data
}

export async function deleteRecipe(id) {
    const response = await api.delete(`/api/v1/recipes/${id}/`)
}
