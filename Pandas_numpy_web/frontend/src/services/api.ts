import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001'

export async function uploadFile(file: File) {
  const form = new FormData()
  form.append('file', file)
  const { data } = await axios.post(`${BASE_URL}/upload`, form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return data as {
    file_id: string
    filename: string
    columns: { name: string; dtype: string }[]
    row_count: number
    sample: any[]
  }
}

export async function getColumns(fileId: string) {
  const { data } = await axios.get(`${BASE_URL}/columns/${fileId}`)
  return data as { file_id: string; columns: { name: string; dtype: string }[] }
}

export async function suggestCharts(fileId: string, selected: string[], limit = 5) {
  const { data } = await axios.post(`${BASE_URL}/suggest-charts`, {
    file_id: fileId,
    selected_columns: selected,
    limit
  })
  return data as {
    suggestions: {
      id: string
      type: string
      title: string
      library: 'plotly'
      config: any
    }[]
  }
}

export async function createChart(fileId: string, spec: any) {
  const { data } = await axios.post(`${BASE_URL}/create-chart`, {
    file_id: fileId,
    spec
  })
  return data as { chart_id?: string; library?: 'plotly'; config?: any; error?: string }
}

export async function listFiles() {
  const { data } = await axios.get(`${BASE_URL}/files`)
  return data as { files: { file_id: string; filename: string; columns?: { name: string; dtype: string }[] }[] }
}

// -------- Analytics endpoints (pre-aggregated JSON) --------
export async function revenueOverTime(fileId: string, freq = 'M') {
  const { data } = await axios.get(`${BASE_URL}/charts/revenue-over-time`, { params: { file_id: fileId, freq } })
  return data as { data: { Date: string; Revenue: number }[] }
}

export async function revenueByCategory(fileId: string, topK = 10) {
  const { data } = await axios.get(`${BASE_URL}/charts/revenue-by-category`, { params: { file_id: fileId, top_k: topK } })
  return data as { data: { ['Product Category']: string; Revenue: number }[] }
}

export async function revenueByGender(fileId: string) {
  const { data } = await axios.get(`${BASE_URL}/charts/revenue-by-gender`, { params: { file_id: fileId } })
  return data as { data: { Gender: string; Revenue: number }[] }
}

export async function ageDistribution(fileId: string, bins = 10) {
  const { data } = await axios.get(`${BASE_URL}/charts/age-distribution`, { params: { file_id: fileId, bins } })
  return data as { data: { ['Age Bin']: string; Count: number }[] }
}

export async function quantityVsRevenue(fileId: string, sample = 500) {
  const { data } = await axios.get(`${BASE_URL}/charts/quantity-vs-revenue`, { params: { file_id: fileId, sample } })
  return data as { data: { Quantity: number; ['Total Amount']: number }[] }
}


