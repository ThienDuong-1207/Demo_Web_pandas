import { useRef, useState } from 'react'
import { uploadFile, suggestCharts, revenueOverTime, revenueByCategory, revenueByGender, ageDistribution, quantityVsRevenue } from '../../services/api'
import { useStore } from '../../app/store'
import { ManualChart } from './ManualChart'

export function Sidebar() {
  const inputRef = useRef<HTMLInputElement | null>(null)
  const { fileId, columns, selected, setFile, setSelected, addWidget } = useStore()
  const [busy, setBusy] = useState(false)

  async function onUploadChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0]
    if (!f) return
    setBusy(true)
    try {
      const data = await uploadFile(f)
      setFile(data.file_id, data.columns)
    } finally {
      setBusy(false)
    }
  }

  // removed refresh/select existing files

  async function onSuggest() {
    if (!fileId || selected.length === 0) return
    setBusy(true)
    try {
      const data = await suggestCharts(fileId, selected)
      for (const s of data.suggestions) {
        addWidget({ id: s.id, title: s.title, config: s.config, type: s.type, x: 0, y: 0, w: 4, h: 6 })
      }
    } finally {
      setBusy(false)
    }
  }

  function toggleSelect(col: string) {
    if (selected.includes(col)) setSelected(selected.filter((c) => c !== col))
    else setSelected([...selected, col])
  }

  async function onGenerateDashboard() {
    if (!fileId) return
    setBusy(true)
    try {
      const [t, cat, gen, age, scat] = await Promise.all([
        revenueOverTime(fileId),
        revenueByCategory(fileId),
        revenueByGender(fileId),
        ageDistribution(fileId),
        quantityVsRevenue(fileId)
      ])
      // Map JSON -> Plotly configs
      addWidget({ id: 'w_line_rev', title: 'Revenue over Time', type: 'line', config: { data: [{ type: 'scatter', mode: 'lines', x: t.data.map(d=>d.Date), y: t.data.map(d=>d.Revenue) }], layout: { title: 'Revenue over Time', paper_bgcolor:'#000', plot_bgcolor:'#000', font:{color:'#fff'}, xaxis:{title:'Date'}, yaxis:{title:'Revenue'} } }, x:0, y:0, w:6, h:8 })
      addWidget({ id: 'w_bar_cat', title: 'Revenue by Category', type: 'bar', config: { data: [{ type: 'bar', x: cat.data.map(d=>d['Product Category']), y: cat.data.map(d=>d.Revenue) }], layout: { title: 'Revenue by Category', paper_bgcolor:'#000', plot_bgcolor:'#000', font:{color:'#fff'}, xaxis:{title:'Product Category'}, yaxis:{title:'Revenue'} } }, x:6, y:0, w:6, h:8 })
      addWidget({ id: 'w_pie_gender', title: 'Revenue by Gender', type: 'pie', config: { data: [{ type: 'pie', labels: gen.data.map(d=>d.Gender), values: gen.data.map(d=>d.Revenue), textinfo:'label+percent' }], layout: { title: 'Revenue by Gender', paper_bgcolor:'#000', plot_bgcolor:'#000', font:{color:'#fff'} } }, x:0, y:8, w:4, h:8 })
      addWidget({ id: 'w_hist_age', title: 'Age Distribution', type: 'bar', config: { data: [{ type: 'bar', x: age.data.map(d=>d['Age Bin']), y: age.data.map(d=>d.Count) }], layout: { title: 'Age Distribution', paper_bgcolor:'#000', plot_bgcolor:'#000', font:{color:'#fff'}, xaxis:{title:'Age Bin'}, yaxis:{title:'Count'} } }, x:4, y:8, w:4, h:8 })
      addWidget({ id: 'w_scatter_qty_rev', title: 'Quantity vs Revenue', type: 'scatter', config: { data: [{ type: 'scatter', mode: 'markers', x: scat.data.map(d=>d.Quantity), y: scat.data.map(d=>d['Total Amount']) }], layout: { title: 'Quantity vs Revenue', paper_bgcolor:'#000', plot_bgcolor:'#000', font:{color:'#fff'}, xaxis:{title:'Quantity'}, yaxis:{title:'Total Amount'} } }, x:8, y:8, w:4, h:8 })
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="sidebar">
      <div className="section-title">Data</div>
      <div className="upload-area">
        <input ref={inputRef} type="file" accept=".csv,.tsv,.txt,.xls,.xlsx" onChange={onUploadChange} />
        <div style={{ opacity: 0.8, marginTop: 8, fontSize: 12 }}>{busy ? 'Processing...' : fileId ? `File: ${fileId}` : 'No file'}</div>
        <div style={{ opacity: 0.7, marginTop: 6, fontSize: 11 }}>Tip: select 2 columns (e.g., date + revenue) before Suggest</div>
        <div style={{ marginTop: 10 }}>
          <button onClick={onGenerateDashboard} disabled={!fileId || busy} style={{ background: '#1f2937', color: '#fff', border: '1px solid #374151', borderRadius: 6, padding: '6px 10px' }}>Generate Dashboard</button>
        </div>
      </div>

      <div className="section-title">Columns</div>
      <div className="columns-list">
        {columns.map((c) => (
          <div className="col-item" key={c.name}>
            <span>
              {c.name}
              <span style={{ fontSize: 11, opacity: 0.7, marginLeft: 8, padding: '1px 6px', border: '1px solid #333', borderRadius: 999 }}>{c.dtype}</span>
            </span>
            <button onClick={() => toggleSelect(c.name)} style={{ background: selected.includes(c.name) ? '#333' : '#111', color: '#fff', border: '1px solid #333', borderRadius: 4, padding: '2px 6px' }}>
              {selected.includes(c.name) ? 'Selected' : 'Select'}
            </button>
          </div>
        ))}
      </div>

      <div className="toolbar">
        <button onClick={onSuggest} disabled={!fileId || selected.length === 0 || busy} style={{ background: '#1f2937', color: '#fff', border: '1px solid #374151', borderRadius: 6, padding: '6px 10px' }}>
          Suggest Charts
        </button>
      </div>

      <ManualChart />
    </div>
  )
}


