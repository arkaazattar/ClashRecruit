import ReactDOM from 'react-dom/client';
import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation, useOutletContext } from 'react-router-dom';
import './index.css';
import Login from './Login';
import Dashboard from './Dashboard';
import Recruiter from './Recruiter'
import LookingForClan from './LookingForClan';
import Layout from "./components/Layout"
import ClanDetails from "./ClanDetails"
import Landing from "./Landing"
import LoadingScreen from "./components/LoadingScreen";
import StaticPage from "./StaticPage";
import LegalPage from "./LegalPage";

function DashboardRouteGuard() {
  const { user, sessionStateLoaded } = useOutletContext();
  const normalizedUser = user === "Guest" ? null : user;

  if (!sessionStateLoaded) {
    return <LoadingScreen />;
  }

  if (!normalizedUser) {
    return <Navigate to="/login" replace />;
  }

  return <Dashboard />;
}

function ScrollToTop() {
  const { hash, pathname } = useLocation();

  useEffect(() => {
    if (hash) {
      const section = document.querySelector(hash);
      section?.scrollIntoView();
      return;
    }

    window.scrollTo({ top: 0, left: 0 });
  }, [hash, pathname]);

  return null;
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <BrowserRouter>
      <ScrollToTop />
      <Routes>

        <Route element={<Layout />}>
          <Route path="/landing" element={<Landing />} />
          <Route path="/" element={<Landing />} />
          <Route path="/dashboard" element={<DashboardRouteGuard />} />
          <Route path="/login" element={<Login />} />
          <Route path="/recruit" element={<Recruiter/>} />
          <Route path="/looking-for-clan" element={<LookingForClan/>}/>
          <Route path="/looking-for-clan/:clanTag" element={<ClanDetails/>}/>
          <Route path="/contact" element={<StaticPage page="contact" />} />
          <Route path="/privacy" element={<LegalPage page="privacy" />} />
          <Route path="/terms" element={<LegalPage page="terms" />} />
        </Route>
      </Routes>
    </BrowserRouter>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
