import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
// Nếu bạn chưa có file index.css thì xóa dòng dưới đi nhé, kẻo lại báo lỗi
import './index.css' 

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)