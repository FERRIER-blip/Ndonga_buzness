const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api'

async function request(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail || `Erreur HTTP ${response.status}`)
  }
  return response.json()
}

export const api = {
  stats: () => request('/dashboard/stats'),
  products: () => request('/products?include_inactive=true'),
  addProduct: (data) => request('/products', { method: 'POST', body: JSON.stringify(data) }),
  updateProduct: (id, data) => request(`/products/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteProduct: (id) => request(`/products/${id}`, { method: 'DELETE' }),
  orders: () => request('/orders'),
  chat: (session_id, message) => request('/chat/simulate', { method: 'POST', body: JSON.stringify({ session_id, message }) }),
  updateOrder: (id, status) => request(`/orders/${id}/status`, { method: 'PATCH', body: JSON.stringify({ status }) })
}
