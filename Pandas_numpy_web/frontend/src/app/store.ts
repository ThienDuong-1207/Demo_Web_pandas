import { create } from 'zustand'

type Column = { name: string; dtype: string }

type Widget = {
  id: string
  title: string
  config: any
  type: string
  w: number
  h: number
  x: number
  y: number
}

type State = {
  fileId?: string
  columns: Column[]
  selected: string[]
  widgets: Widget[]
  layoutKey: string
  setFile: (fileId: string, columns: Column[]) => void
  setSelected: (cols: string[]) => void
  addWidget: (w: Widget) => void
  removeWidget: (id: string) => void
  loadPersisted: () => void
  persist: () => void
}

export const useStore = create<State>((set) => ({
  fileId: undefined,
  columns: [],
  selected: [],
  widgets: [],
  layoutKey: 'pnw_widgets_v1',
  setFile: (fileId, columns) => set({ fileId, columns }),
  setSelected: (selected) => set({ selected }),
  addWidget: (w) => set((s) => {
    const next = [...s.widgets.filter((x) => x.id !== w.id), w]
    localStorage.setItem(s.layoutKey, JSON.stringify(next))
    return { widgets: next }
  }),
  removeWidget: (id) => set((s) => {
    const next = s.widgets.filter((w) => w.id !== id)
    localStorage.setItem(s.layoutKey, JSON.stringify(next))
    return { widgets: next }
  }),
  loadPersisted: () => set((s) => {
    const raw = localStorage.getItem(s.layoutKey)
    if (!raw) return {}
    try {
      const parsed = JSON.parse(raw)
      if (Array.isArray(parsed)) return { widgets: parsed }
    } catch {}
    return {}
  }),
  persist: () => set((s) => {
    localStorage.setItem(s.layoutKey, JSON.stringify(s.widgets))
    return {}
  })
}))


