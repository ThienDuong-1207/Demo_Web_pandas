# BI Dashboard Project (Flask + React + Plotly)

## 🔹 Backend (Flask + Pandas)

### 1. Analytics (Main Dashboard – 5 fixed charts)
Implement `services/analytics.py` with 5 functions. Each must pre-aggregate data using pandas and return **JSON records**, not Plotly config.

1. **chart_revenue_over_time(df, freq="M")**
   - Parse Date, resample by freq (D/W/M/Q/Y).
   - Sum "Total Amount".
   - Return: `[{"Date": "...", "Revenue": ...}, ...]`

2. **chart_revenue_by_category(df, top_k=10)**
   - Group by "Product Category", sum "Total Amount".
   - Keep top_k categories, aggregate rest into "Others".
   - Return: `[{"Product Category": "Electronics", "Revenue": ...}, ...]`

3. **chart_revenue_by_gender(df)**
   - Group by "Gender", sum "Total Amount".
   - Return: `[{"Gender": "Male", "Revenue": ...}, {"Gender": "Female", "Revenue": ...}]`

4. **chart_age_distribution(df, bins=10)**
   - Bin "Age" into ranges.
   - Count per bin.
   - Return: `[{"Age Bin": "(20,25]", "Count": ...}, ...]`

5. **chart_quantity_vs_revenue(df, sample=500)**
   - Take Quantity vs Total Amount.
   - Random sample max 500 rows.
   - Return: `[{"Quantity": ..., "Total Amount": ...}, ...]`

#### Endpoints
Expose in `api/routes.py`:
- GET `/charts/revenue-over-time?file_id=...&freq=M`
- GET `/charts/revenue-by-category?file_id=...&top_k=10`
- GET `/charts/revenue-by-gender?file_id=...`
- GET `/charts/age-distribution?file_id=...&bins=10`
- GET `/charts/quantity-vs-revenue?file_id=...&sample=500`

Response format:
```json
{ "data": [...] }
```

---

### 2. Exploration (Recommendation)
Implement `services/recommend.py` for **rule-based chart suggestions**.  
Only support **line, multi-line, bar, pie, scatter**.

- Input: list of selected columns (dimensions/metrics).
- Detect dtypes: datetime, numeric, categorical.
- Suggest chart types:
  - **Line**: Date + Numeric (sum over time).
  - **Multi-line**: Date + Category + Numeric (legend by category).
  - **Bar**: Category + Numeric (sum), or single category (count).
  - **Pie**: Category + Numeric (share).
  - **Scatter**: 2 numeric (x vs y), or 3 numeric (x vs y, color by 3rd).

#### Endpoints
- POST `/suggest-charts`
  - Input: `{ "file_id": "...", "selected_columns": [...] }`
  - Output: `{ "suggestions": [ { "id": "...", "type": "bar", "config": {...} } ] }`

- POST `/create-chart`
  - Input: `{ "file_id": "...", "spec": {...} }`
  - Output: `{ "chart_id": "...", "config": {...} }`

---

### 3. File Handling
- `/upload` → upload CSV/Excel, store DataFrame in memory by `file_id`.
- `/columns/<file_id>` → return column metadata.
- `/files` → list uploaded files.

---

## 🔹 Frontend (React + Plotly + Tailwind)

### 1. Layout
- Split screen: **Sidebar 30%** and **Dashboard 70%**.
- Use dark theme with TailwindCSS + shadcn/ui.
- Use react-plotly.js for charts.
- Use react-grid-layout for draggable/resizable dashboard grid.

### 2. Sidebar (30%)
#### Header Section
- File Upload (CSV/Excel) → POST `/upload`.
- Dropdown: select file_id (from `/files`).
- Button **Generate Dashboard**:
  - Calls 5 analytics endpoints.
  - Renders 5 fixed charts in Dashboard.

#### Chart Management
- Show list of current dashboard charts.
- Each chart has a ❌ Remove button → remove from dashboard.

#### Exploration Section (bottom of sidebar)
- Multi-select dropdown: choose columns (from `/columns/<file_id>`).
- Dropdown: choose chart type (line, multi-line, bar, pie, scatter).
- Button **Suggest Chart**:
  - Calls `/suggest-charts`.
  - Renders suggested charts in preview.
  - Each preview chart has a "Stick to dashboard" button → adds chart to main dashboard.

### 3. Dashboard (70%)
- Responsive grid layout (2x2 or 3x2).
- Render:
  - 5 Analytics charts:
    - Line: Revenue over Time (x=Date, y=Revenue).
    - Bar: Revenue by Category (x=Category, y=Revenue).
    - Pie: Revenue by Gender (labels=Gender, values=Revenue).
    - Histogram: Age Distribution (x=Age Bin, y=Count).
    - Scatter: Quantity vs Revenue (x=Quantity, y=Total Amount).
  - Exploration charts if user sticks them.
- Each chart is wrapped in `ChartCard`:
  - Title
  - Plotly chart
  - ❌ Remove button
  - Draggable & resizable in grid

### 4. State Management
- Use Zustand or React Context.
- Store:
  - `files` → uploaded file list.
  - `selectedFileId`.
  - `dashboardCharts` → list of chart objects.
  - Persist layout & charts in localStorage.

### 5. UX
- Dark theme (`bg-gray-900`, `text-gray-200`).
- Smooth animations with Framer Motion.
- Charts autoscale to container.
- Dashboard persists state between reloads.

---
