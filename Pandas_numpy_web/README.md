# Pandas Numpy Web Dashboard

## Backend Prompt (Flask + Pandas)
- Mục tiêu: Cung cấp API xử lý dữ liệu và biểu đồ cho dashboard e-commerce. Tất cả endpoint trả JSON đã pre-aggregate để frontend chỉ việc vẽ.
- Stack: Flask, flask-cors, pandas, numpy. Lưu DataFrame trong RAM; registry file dưới `backend/storage/registry.json`. Upload lưu tại `backend/storage/uploads/`.
- Endpoint:
  - POST `/upload` → lưu file, chuẩn hoá dtype, suy luận cột, trả `file_id`, `columns`, `row_count`, `sample`.
  - GET `/columns/{file_id}` → danh sách cột với dtype: `number | category | datetime | text`.
  - GET `/files` → danh sách file đã upload (đọc từ registry; tự reconcile với thư mục uploads).
  - POST `/suggest-charts` → gợi ý biểu đồ dựa vào cột đã chọn; trả về cấu hình Plotly (đã có title, legend, axis titles).
  - POST `/create-chart` → nhận `spec` và trả về config Plotly tương ứng.
  - Analytics (pre-aggregate, JSON):
    - GET `/charts/revenue-over-time?file_id&freq=D|W|M|Q|Y`
    - GET `/charts/revenue-by-category?file_id&top_k=10`
    - GET `/charts/revenue-by-gender?file_id`
    - GET `/charts/age-distribution?file_id&bins=10`
    - GET `/charts/quantity-vs-revenue?file_id&sample=500`
- Logic gợi ý chính:
  - 1 cột: number → histogram + box; category → bar Top-K + pie.
  - 2 cột: time+number → line (sum over time); category+number → bar; number+number → scatter; category+category → heatmap; time+category → multi-line count.
  - 3 cột: time+category+number → multi-line sum; 3 number → scatter colored by number thứ 3.
  - ≥3 number → correlation heatmap.
- Quy tắc line/time:
  - Ép `Date` về datetime; chọn `freq` theo span (D/W/M/Q).
  - time+measure → resample + sum; time+category(+measure) → groupby(time, category) + sum hoặc count.
- Plotly layout: dark theme; có `layout.title`, `xaxis.title`, `yaxis.title`, `showlegend=true`, `automargin=true`.

## Frontend Prompt (React + Vite + Plotly)
- Mục tiêu: UI dashboard dark theme với sidebar chọn dữ liệu/cột, gợi ý biểu đồ, grid kéo/thả/resize; render từ JSON của backend.
- Stack: React 18 + Vite, TypeScript, react-grid-layout, react-plotly.js, Zustand, Axios.
- UI/State:
  - Sidebar (30%): Upload, Refresh Files, dropdown “Select existing file”, danh sách cột (dtype), chọn cột, Suggest Charts, Create Chart.
  - Dashboard (70%): react-grid-layout widget Plotly; header title + Remove; lưu layout vào localStorage.
  - Store: `fileId`, `columns`, `selected[]`, `widgets[]`, `layoutKey`, actions `setFile/setSelected/addWidget/removeWidget/loadPersisted/persist`.
- API mapping:
  - Upload/Files/Columns; Suggest nhận `suggestions[].config` và thêm widget.
  - 5 chart chính gọi `/charts/*` và map field → Plotly:
    - Line: x=`Date`, y=`Revenue`
    - Bar Category: x=`Product Category`, y=`Revenue`
    - Pie Gender: labels=`Gender`, values=`Revenue`
    - Histogram Age: x=`Age Bin`, y=`Count` (bar)
    - Scatter: x=`Quantity`, y=`Total Amount`
- Resizing/UX:
  - Dùng `useResizeHandler`, `responsive=true`; container `flex:1; minHeight:0`.
  - Phát `window.resize` khi drag/resize stop để Plotly reflow; `draggableCancel=".nodrag"` cho header/button.
- Env: `.env` → `VITE_API_BASE_URL=http://localhost:5001`.

## Quickstart
Backend
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py
# http://localhost:5001/health
```
Frontend
```bash
cd frontend
cp ENV_EXAMPLE .env
npm i
npm run dev -- --port 5175 --strictPort
```
