// L'instance axios centralise la baseURL pour éviter de la répéter partout.

import axios from 'axios'

const api = axios.create({
    baseURL: ''
})

export default api