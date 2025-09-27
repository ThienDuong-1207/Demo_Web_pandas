import { useState } from 'react'
import { createChart } from '../../services/api'
import { useStore } from '../../app/store'

export function ManualChart() {
  const { fileId, columns, addWidget } = useStore()
  const [type, setType] = useState<'bar' | 'line' | 'scatter' | 'heatmap'>('bar')
  const [x, setX] = useState('')
  const [y, setY] = useState('')
  const [cat, setCat] = useState('')
  const [val, setVal] = useState('')
  const [busy, setBusy] = useState(false)

  async function onCreate() {
    if (!fileId) return
    setBusy(true)
    try {
      let spec: any
      if (type === 'bar') spec = { type, category: cat || x, value: val || y, agg: 'sum' }
      else if (type === 'line' || type === 'scatter') spec = { type, x, y }
      else spec = { type, x, y }
      const res = await createChart(fileId, spec)
      if (res.config) {
        const title = `${type.toUpperCase()} ${x}${y ? ' vs ' + y : ''}`
        addWidget({ id: res.chart_id || Math.random().toString(36).slice(2), title, type, config: res.config, x: 0, y: 0, w: 4, h: 6 })
      }
    } finally {
      setBusy(false)
    }
  }

  return (
    <div style={{ padding: '8px 16px 16px', borderTop: '1px solid #222' }}>
      <div style={{ fontWeight: 600, marginBottom: 8 }}>Create Chart</div>
      <div style={{ display: 'grid', gap: 8 }}>
        <label>
          <span style={{ display: 'block', fontSize: 12, opacity: 0.8 }}>Type</span>
          <select value={type} onChange={(e) => setType(e.target.value as any)} style={{ width: '100%', background: '#111', color: '#fff', border: '1px solid #333', borderRadius: 6, padding: 6 }}>
            <option value="bar">bar</option>
            <option value="line">line</option>
            <option value="scatter">scatter</option>
            <option value="heatmap">heatmap</option>
          </select>
        </label>
        <label>
          <span style={{ display: 'block', fontSize: 12, opacity: 0.8 }}>X</span>
          <select value={x} onChange={(e) => setX(e.target.value)} style={{ width: '100%', background: '#111', color: '#fff', border: '1px solid #333', borderRadius: 6, padding: 6 }}>
            <option value="">--</option>
            {columns.map((c) => (
              <option key={c.name} value={c.name}>{c.name}</option>
            ))}
          </select>
        </label>
        <label>
          <span style={{ display: 'block', fontSize: 12, opacity: 0.8 }}>Y / Value</span>
          <select value={y} onChange={(e) => setY(e.target.value)} style={{ width: '100%', background: '#111', color: '#fff', border: '1px solid #333', borderRadius: 6, padding: 6 }}>
            <option value="">--</option>
            {columns.map((c) => (
              <option key={c.name} value={c.name}>{c.name}</option>
            ))}
          </select>
        </label>
        {type === 'bar' && (
          <>
            <label>
              <span style={{ display: 'block', fontSize: 12, opacity: 0.8 }}>Category (if using different field)</span>
              <select value={cat} onChange={(e) => setCat(e.target.value)} style={{ width: '100%', background: '#111', color: '#fff', border: '1px solid #333', borderRadius: 6, padding: 6 }}>
                <option value="">--</option>
                {columns.map((c) => (
                  <option key={c.name} value={c.name}>{c.name}</option>
                ))}
              </select>
            </label>
            <label>
              <span style={{ display: 'block', fontSize: 12, opacity: 0.8 }}>Value (if using different field)</span>
              <select value={val} onChange={(e) => setVal(e.target.value)} style={{ width: '100%', background: '#111', color: '#fff', border: '1px solid #333', borderRadius: 6, padding: 6 }}>
                <option value="">--</option>
                {columns.map((c) => (
                  <option key={c.name} value={c.name}>{c.name}</option>
                ))}
              </select>
            </label>
          </>
        )}
        <button onClick={onCreate} disabled={!fileId || busy} style={{ background: '#1f2937', color: '#fff', border: '1px solid #374151', borderRadius: 6, padding: '6px 10px' }}>Create</button>
      </div>
    </div>
  )
}


