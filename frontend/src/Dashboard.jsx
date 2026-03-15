import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { useOutletContext } from "react-router-dom";
import LoadingScreen from "./components/LoadingScreen";
import "./Dashboard.css";

const townHallAssets = require.context("./assets", false, /\.webp$/);

function getTownHallAsset(townhallLevel, weaponLevel) {
  if (!townhallLevel) {
    return null;
  }

  const assetNames = weaponLevel
    ? [`./townhall-${townhallLevel}-${weaponLevel}.webp`, `./townhall-${townhallLevel}.webp`]
    : [`./townhall-${townhallLevel}.webp`];

  for (const assetName of assetNames) {
    try {
      return townHallAssets(assetName);
    } catch {
      continue;
    }
  }

  return null;
}

function preloadImage(src) {
  if (!src) {
    return Promise.resolve();
  }

  return new Promise((resolve) => {
    const image = new Image();
    image.onload = resolve;
    image.onerror = resolve;
    image.src = src;
  });
}

function Dashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [townHallImage, setTownHallImage] = useState(null);
  const { user, townhall, townhallWeaponLevel, recruitStatus, dashboardLoaded } = useOutletContext();

  useEffect(() => {
    if (!dashboardLoaded) {
      setLoading(true);
      return;
    }

    let isMounted = true;

    const resolvedTownHallImage = getTownHallAsset(
      townhall,
      townhallWeaponLevel
    );

    preloadImage(resolvedTownHallImage).then(() => {
      if (!isMounted) {
        return;
      }

      setTownHallImage(resolvedTownHallImage);
      setLoading(false);
    });

    return () => {
      isMounted = false;
    };
  }, [dashboardLoaded, townhall, townhallWeaponLevel]);

  const Recruiter = () => {
    navigate("/recruit");
  };

  const Recruitee = () => {
    navigate("/looking-for-clan");
  };

  if (loading) {
    return <LoadingScreen />;
  }
  return (
    <div className="Dashboard">
      <section className="dashboard-layout">
        <div className="dashboard-hero">
          <div className="dashboard-townhall-shell">
            {townHallImage ? (
              <img
                src={townHallImage}
                alt={`Town Hall level ${townhall}`}
                className="dashboard-townhall-image"
              />
            ) : null}
          </div>

          <div className="dashboard-panel">
            <p className="dashboard-eyebrow">Player dashboard</p>
            <h1 className="dashboard-welcome">Welcome {user}</h1>

            <div className="dashboard-actions">
              {recruitStatus === true && (
                <button
                  type="button"
                  className="dashboard-btn dashboard-btn-primary"
                  onClick={Recruiter}
                >
                  Start Recruiting
                </button>
              )}

              <button
                type="button"
                className="dashboard-btn dashboard-btn-secondary"
                onClick={Recruitee}
              >
                Looking For Clan
              </button>
            </div>
          </div>
        </div>

        <section className="dashboard-stats-panel">
          <div className="dashboard-stats-header">
            <h2>More stats from API</h2>
            <p>
              If not in clan : current league | builder base stats | player level and player tag  
            </p>
            <p>
              If in clan add: clan icon + name | position in clan | member count/stats 
            </p>

            <p>
              If guest: LOGIN BUTTON
            </p>
          </div>

          <div className="dashboard-stats-placeholder">
            <div className="dashboard-placeholder-block" />
            <div className="dashboard-placeholder-block dashboard-placeholder-wide" />
            <div className="dashboard-placeholder-block" />
          </div>
        </section>
      </section>
    </div>
  );
}

export default Dashboard;
