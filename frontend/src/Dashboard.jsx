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
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [townHallImage, setTownHallImage] = useState(null);
  const [userInfo, setUserInfo] = useState(null);
  const [userInfoLoading, setUserInfoLoading] = useState(false);
  const { user, townhall, townhallWeaponLevel, recruitStatus, dashboardLoaded } = useOutletContext();

  useEffect(() => {
    if (!dashboardLoaded) {
      setLoading(true);
      return;
    }

    let isMounted = true;
    setLoading(true);

    const resolvedTownHallImage = getTownHallAsset(
      townhall,
      townhallWeaponLevel
    );

    if (user === "Guest") {
      setUserInfo(null);
      setUserInfoLoading(false);
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
    }

    setUserInfoLoading(true);

    Promise.all([
      preloadImage(resolvedTownHallImage).then(() => resolvedTownHallImage),
      fetch("/dashboard/user-info", { credentials: "include" })
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

        setUserInfoLoading(false);
        setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [dashboardLoaded, townhall, townhallWeaponLevel, user]);

  const Recruiter = () => {
    navigate("/recruit");
  };

  const Recruitee = () => {
    navigate("/looking-for-clan");
  };

  const Login = () => {
    navigate("/");
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

        {user === "Guest" ? (
          <div className="dashboard-guest-login-wrap">
            <button
              type="button"
              className="dashboard-btn dashboard-btn-secondary dashboard-stats-login-btn"
              onClick={Login}
            >
              Login
            </button>
          </div>
        ) : (
          <section className="dashboard-stats-panel">
            <div className="dashboard-stats-header">
              <h2>More stats from API</h2>
            </div>

            <div className="dashboard-stats-placeholder">
              <div className="dashboard-placeholder-block">
                <div className="dashboard-stat-box-content">
                  <p className="dashboard-stat-box-title">Player</p>
                  {userInfoLoading ? (
                    <p className="dashboard-stat-empty">Loading...</p>
                  ) : (
                    <>
                      <p className="dashboard-stat-line"><strong>Player Tag:</strong> {playerTag}</p>
                      <p className="dashboard-stat-line"><strong>Player Level:</strong> {playerLevel}</p>
                      <p className="dashboard-stat-line"><strong>League:</strong> {leagueName}</p>
                    </>
                  )}
                </div>
              </div>

              <div className="dashboard-placeholder-block dashboard-placeholder-wide">
                <div className="dashboard-stat-box-content">
                  <p className="dashboard-stat-box-title">Builder Base</p>
                  {userInfoLoading ? (
                    <p className="dashboard-stat-empty">Loading...</p>
                  ) : (
                    <>
                      <p className="dashboard-stat-line"><strong>Builder League:</strong> {builderLeagueName}</p>
                      <p className="dashboard-stat-line"><strong>Builder Hall:</strong> {builderHallLevel}</p>
                    </>
                  )}
                </div>
              </div>

              <div className="dashboard-placeholder-block">
                <div className="dashboard-stat-box-content">
                  <p className="dashboard-stat-box-title">Clan</p>
                  {userInfoLoading ? (
                    <p className="dashboard-stat-empty">Loading...</p>
                  ) : clanName ? (
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
        )}
      </section>
    </div>
  );
}

export default Dashboard;
