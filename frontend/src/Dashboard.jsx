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
      
      {townHallImage && (
        <img
          src={townHallImage}
          alt={`Town Hall level ${townhall}`}
          className="dashboard-townhall-image"
        />
      )}

      <section className="dashboard-panel">
        <div className="dashboard-box">
          <p className="dashboard-welcome">Welcome {user}</p>
          
        
          <form className="dashboard-form">
            {recruitStatus === true && (
              <button
                type="button"
                className="dashboard-btn dashboard-btn-primary"
                onClick={Recruiter}
              >
                Recruit!
              </button>
            )}

            <button
              type="button"
              className="dashboard-btn dashboard-btn-secondary"
              onClick={Recruitee}
            >
              Start Searching →
            </button>
          </form>
        </div>
      </section>
    </div>
  );
}

export default Dashboard;
