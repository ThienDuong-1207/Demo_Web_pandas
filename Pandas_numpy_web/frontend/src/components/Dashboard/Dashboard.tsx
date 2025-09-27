import { useEffect } from 'react'
import GridLayout, { Layout } from 'react-grid-layout'
import Plot from 'react-plotly.js'
import { useStore } from '../../app/store'
import 'react-grid-layout/css/styles.css'
import 'react-resizable/css/styles.css'

export function Dashboard() {
  const { widgets, removeWidget, loadPersisted, persist } = useStore()

  // Load persisted layout once after mount
  useEffect(() => {
    loadPersisted()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const layout: Layout[] = widgets.map((w, i) => ({ i: w.id, x: (i % 3) * 4, y: Math.floor(i / 3) * 6, w: w.w, h: w.h }))

  return (
    <div className="dashboard">
      <GridLayout
        className="layout"
        cols={12}
        rowHeight={30}
        width={window.innerWidth - Math.min(window.innerWidth * 0.3, 560)}
        isResizable
        isDraggable
        draggableCancel=".nodrag"
        onLayoutChange={() => { persist(); }}
        onResizeStop={() => { window.dispatchEvent(new Event('resize')); }}
        onDragStop={() => { window.dispatchEvent(new Event('resize')); }}
      >
        {widgets.map((w) => (
          <div key={w.id} data-grid={{ i: w.id, x: w.x, y: w.y, w: w.w, h: w.h }} style={{ background: '#0b0b0b', border: '1px solid #222', borderRadius: 8, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
            <div className="nodrag" style={{ padding: '8px 10px', borderBottom: '1px solid #222', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>{w.title}</span>
              <button className="nodrag" onMouseDown={(e) => e.stopPropagation()} onClick={() => removeWidget(w.id)} style={{ background: '#111', color: '#fff', border: '1px solid #333', borderRadius: 6, padding: '4px 8px' }}>Remove</button>
            </div>
            <div style={{ padding: 8, flex: 1, minHeight: 0 }}>
              <Plot
                data={w.config.data}
                layout={{ ...w.config.layout, autosize: true, xaxis: { ...(w.config.layout?.xaxis || {}), automargin: true }, yaxis: { ...(w.config.layout?.yaxis || {}), automargin: true } }}
                useResizeHandler
                style={{ width: '100%', height: '100%' }}
                config={{ displayModeBar: false, responsive: true }}
              />
            </div>
          </div>
        ))}
      </GridLayout>
    </div>
  )
}


