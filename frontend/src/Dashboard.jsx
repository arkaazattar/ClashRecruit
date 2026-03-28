import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { useOutletContext } from "react-router-dom";
import LoadingScreen from "./components/LoadingScreen";
import usePageTitle from "./hooks/usePageTitle";
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

function normalizeUserInfo(data) {
  return {
    player_tag: data.player_tag || "N/A",
    expLevel: data.expLevel ?? "N/A",
    leagueName: data.leagueTier?.name || "Unranked",
    builderLeagueName: data.builderBaseLeague?.name || "Unranked",
    builderHallLevel: data.builderHallLevel ?? "N/A",
    clan: data.clan
      ? {
          name: data.clan.name,
          tag: data.clan.tag,
          role: data.clan.role,
          badgeUrl: data.clan.badgeUrls.medium,
        }
      : null,
  };
}

function Dashboard() {
  usePageTitle("Dashboard | ClashRecruit")
  
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [townHallImage, setTownHallImage] = useState(null);
  const [userInfo, setUserInfo] = useState(null);
  const { user, townhall, townhallWeaponLevel, recruitStatus, sessionStateLoaded } = useOutletContext();
  const normalizedUser = user === "Guest" ? null : user;

  useEffect(() => {
    if (!sessionStateLoaded) {
      setLoading(true);
      return;
    }

    let isMounted = true;
    setLoading(true);

    const resolvedTownHallImage = getTownHallAsset(
      townhall,
      townhallWeaponLevel
    );

    Promise.all([
      preloadImage(resolvedTownHallImage).then(() => resolvedTownHallImage),
      fetch("/session-state/user-info", { credentials: "include" })
        .then((res) => res.json())
        .then((data) => normalizeUserInfo(data))
        .catch(() => null),
    ])
      .then(([nextTownHallImage, nextUserInfo]) => {
        if (!isMounted) {
          return;
        }

        setTownHallImage(nextTownHallImage);
        setUserInfo(nextUserInfo);
      })
      .finally(() => {
        if (!isMounted) {
          return;
        }

        setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [sessionStateLoaded, townhall, townhallWeaponLevel, normalizedUser]);

  const Recruiter = () => {
    navigate("/recruit");
  };

  const Recruitee = () => {
    navigate("/looking-for-clan");
  };

  const dashboardUserInfo = userInfo || normalizeUserInfo({});
  const playerTag = dashboardUserInfo.player_tag;
  const playerLevel = dashboardUserInfo.expLevel;
  const leagueName = dashboardUserInfo.leagueName;
  const builderLeagueName = dashboardUserInfo.builderLeagueName;
  const builderHallLevel = dashboardUserInfo.builderHallLevel;
  const clan = dashboardUserInfo.clan;
  const clanName = clan ? clan.name : "";
  const clanTag = clan ? clan.tag : "N/A";
  const clanRole = clan ? clan.role : "N/A";
  const clanBadge = clan ? clan.badgeUrl : "";

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
            <div className="dashboard-panel-content">
              <div className="dashboard-panel-copy">
                <p className="dashboard-eyebrow">Player dashboard</p>
                <h1 className="dashboard-welcome">Welcome {normalizedUser || "Player"}</h1>

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

                      {clanBadge ? (
                        <img
                          src={clanBadge}
                          alt={`${clanName} badge`}
                          className="dashboard-panel-badge"
                />
              ) : null}
            </div>
          </div>
        </div>

        <section className="dashboard-stats-panel">
          <div className="dashboard-stats-header">
            <h2>Player Stats</h2>
          </div>

          <div className="dashboard-carousel">
            <div className="dashboard-carousel-item">
              <div className="dashboard-stat-box-content">
                <p className="dashboard-stat-box-title">Player Tag</p>
                <p className="dashboard-stat-line">#{playerTag}</p>
              </div>
            </div>

            <div className="dashboard-carousel-item">
              <div className="dashboard-stat-box-content">
                <p className="dashboard-stat-box-title">Player Level</p>
                <p className="dashboard-stat-line">{playerLevel}</p>
              </div>
            </div>

            <div className="dashboard-carousel-item">
              <div className="dashboard-stat-box-content">
                <p className="dashboard-stat-box-title">League</p>
                <p className="dashboard-stat-line">{leagueName}</p>
              </div>
            </div>

            <div className="dashboard-carousel-item">
              <div className="dashboard-stat-box-content">
                <p className="dashboard-stat-box-title">Builder League</p>
                <p className="dashboard-stat-line">{builderLeagueName}</p>
              </div>
            </div>

            <div className="dashboard-carousel-item">
              <div className="dashboard-stat-box-content">
                <p className="dashboard-stat-box-title">Builder Hall</p>
                <p className="dashboard-stat-line">{builderHallLevel}</p>
              </div>
            </div>

            <div className="dashboard-carousel-item">
              <div className="dashboard-stat-box-content">
                <p className="dashboard-stat-box-title">Clan</p>
                {clanName ? (
                  <>
                    <p className="dashboard-stat-line"><strong>Name:</strong> {clanName}</p>
                    <p className="dashboard-stat-line"><strong>Tag:</strong> {clanTag}</p>
                    <p className="dashboard-stat-line"><strong>Role:</strong> {clanRole || "N/A"}</p>
                  </>
                ) : (
                  <p className="dashboard-stat-empty">Not currently in a clan.</p>
                )}
              </div>
            </div>
          </div>
        </section>
      </section>
    </div>
  );
}

export default Dashboard;
