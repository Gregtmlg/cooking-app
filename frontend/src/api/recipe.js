import axios from 'axios'

const api = axios.create({
    baseURL: 'http://localhost:8000'
})

export async function get_recipes() {
    const response = await api.get('/api/v1/recipes/')
    return response.data
}

export async function get_recipe(id) {
    const response = await api.get(`/api/v1/recipes/${id}/`)
    return response.data
}

export async function create_recipe(data) {
    const response = await api.post('/api/v1/recipes/', data)
    return response.data
}

export async function update_recipe(id, data) {
    const response = await api.put(`/api/v1/recipes/${id}/`, data)
    return response.data
}

export async function delete_recipe(id) {
    const response = await api.delete(`/api/v1/recipes/${id}/`)
}
