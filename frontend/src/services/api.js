import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Handle specific error codes
      switch (error.response.status) {
        case 401:
          // Unauthorized - clear token and redirect to login
          localStorage.removeItem('auth_token')
          break
        case 404:
          console.error('Resource not found')
          break
        case 500:
          console.error('Server error')
          break
      }
    }
    return Promise.reject(error)
  }
)

// Weather API
export const weatherAPI = {
  getCurrentWeather: (latitude, longitude) => 
    api.get('/api/v1/weather/current', { params: { latitude, longitude } }),
  
  getForecast: (latitude, longitude, targetTime = null) => 
    api.get('/api/v1/weather/forecast', { 
      params: { latitude, longitude, target_time: targetTime } 
    })
}

// Risk Analysis API
export const riskAPI = {
  calculateRisk: (data) => 
    api.post('/api/v1/risk-analysis/calculate', data),
  
  getMatchRiskAnalysis: (matchId) => 
    api.get(`/api/v1/risk-analysis/match/${matchId}`)
}

// Match API
export const matchAPI = {
  listMatches: (params = {}) => 
    api.get('/api/v1/matches', { params }),
  
  getMatchDetails: (matchId) => 
    api.get(`/api/v1/matches/${matchId}`),
  
  getMatchPreview: (matchId) => 
    api.get(`/api/v1/matches/${matchId}/preview`)
}

// Stadium API
export const stadiumAPI = {
  getStadiumMap: (stadiumId) => 
    api.get(`/api/v1/stadium/${stadiumId}/map`),
  
  getStadiumZones: (stadiumId) => 
    api.get(`/api/v1/stadium/${stadiumId}/zones`)
}

// Recommendations API
export const recommendationsAPI = {
  getMatchRecommendations: (matchId, target = null) => 
    api.get(`/api/v1/recommendations/${matchId}`, { 
      params: target ? { target } : {} 
    })
}

export default api

