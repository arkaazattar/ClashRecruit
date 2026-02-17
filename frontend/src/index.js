import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './index.css';
import App from './App';
import Dashboard from './Dashboard';
import Recruiter from './Recruiter'
import LookingForClan from './LookingForClan';
import Layout from "./components/Layout"
import ClanDetails from "./ClanDetails"

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />

        <Route element={<Layout />}>
          <Route path="/dashboard/" element={<Dashboard />} />
          <Route path="/recruit/" element={<Recruiter/>} />
          <Route path="/looking-for-clan/" element={<LookingForClan/>}/>
          <Route path="/looking-for-clan/:clanTag/" element={<ClanDetails/>}/>
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals

