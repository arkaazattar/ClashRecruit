import { useState, useEffect, useRef } from "react";
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

function normalizeClanRoleLabel(roleValue) {
  if (!roleValue) {
    return "N/A";
  }

  const normalized = String(roleValue).trim().toLowerCase();

  if (normalized === "leader") return "Leader";
  if (normalized === "coleader" || normalized === "co-leader") return "Co-Leader";
  if (normalized === "admin") return "Elder";
  if (normalized === "member") return "Member";

  return normalized.charAt(0).toUpperCase() + normalized.slice(1);
}

function normalizeTagValue(tagValue) {
  if (!tagValue || tagValue === "N/A") {
    return null;
  }

  return String(tagValue).trim().replace(/^#+/, "");
}

function Dashboard() {
  usePageTitle("Dashboard | ClashRecruit")
  
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [townHallImage, setTownHallImage] = useState(null);
  const [userInfo, setUserInfo] = useState(null);
  const [copiedTag, setCopiedTag] = useState("");
  const copyResetTimerRef = useRef(null);
  const { user, townhall, townhallWeaponLevel, recruitStatus, hasActiveListing, sessionStateLoaded } = useOutletContext();
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

  const copyTag = async (tag) => {
    if (!tag) {
      return;
    }

    try {
      await navigator.clipboard.writeText(tag);
      setCopiedTag(tag);
      if (copyResetTimerRef.current) {
        clearTimeout(copyResetTimerRef.current);
      }
      copyResetTimerRef.current = setTimeout(() => {
        setCopiedTag("");
        copyResetTimerRef.current = null;
      }, 1200);
    } catch {
    }
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
  const normalizedPlayerTag = normalizeTagValue(playerTag);
  const normalizedClanTag = normalizeTagValue(clanTag);
  const clanRole = normalizeClanRoleLabel(clan?.role);
  const clanBadge = clan ? clan.badgeUrl : "";
  const clanDisplay = clanName || "No clan linked";
  const canRecruit = recruitStatus === true;
  const isInClan = Boolean(clan);
  const canManageListing = canRecruit;
  const listingExists = Boolean(hasActiveListing);
  const listingChip = getListingChipMeta();

  function getListingChipMeta() {
    if (!isInClan) {
      return { label: "No Clan", className: "is-idle" };
    }
    if (listingExists) {
      return { label: "Listing Active", className: "is-active" };
    }
    return { label: "No Active Listing", className: "is-idle" };
  }

  function renderListingContent() {
    if (!isInClan) {
      return (
        <>
          <div className="dashboard-listing-head">
            <p className="dashboard-listing-text">Join a clan to unlock recruiting features.</p>
          </div>
          <div className="dashboard-listing-actions">
            <button type="button" className="dashboard-link-btn dashboard-listing-btn is-primary" onClick={Recruitee}>
              Find a Clan
            </button>
          </div>
        </>
      );
    }

    if (!canManageListing && !listingExists) {
      return (
        <>
          <div className="dashboard-listing-head">
            <p className="dashboard-listing-text">Your clan doesn&apos;t have an active recruiting listing.</p>
          </div>
          <div className="dashboard-listing-actions">
            <button type="button" className="dashboard-link-btn dashboard-listing-btn is-primary" onClick={Recruitee}>
              Browse Listings
            </button>
          </div>
          <p className="dashboard-listing-helper">You need to be Elder or higher to create one.</p>
        </>
      );
    }

    if (!canManageListing && listingExists) {
      return (
        <>
          <div className="dashboard-listing-head">
            <p className="dashboard-listing-text">Your clan already has an active recruiting listing.</p>
          </div>
          <div className="dashboard-listing-actions">
            <button type="button" className="dashboard-link-btn dashboard-listing-btn is-primary" onClick={Recruitee}>
              Browse Listings
            </button>
          </div>
          <p className="dashboard-listing-helper">You need to be Elder or higher to manage it.</p>
        </>
      );
    }

    if (canManageListing && !listingExists) {
      return (
        <>
          <div className="dashboard-listing-head">
            <p className="dashboard-listing-text">Create a listing to start receiving interested players.</p>
          </div>
          <div className="dashboard-listing-actions">
            <button type="button" className="dashboard-link-btn dashboard-listing-btn is-primary" onClick={Recruiter}>
              Create Listing
            </button>
            <button type="button" className="dashboard-link-btn dashboard-listing-btn" onClick={Recruitee}>
              Browse Listings
            </button>
          </div>
        </>
      );
    }

    return (
      <>
        <div className="dashboard-listing-head">
          <p className="dashboard-listing-text">Your recruiting listing is live and visible to players.</p>
        </div>
        <div className="dashboard-listing-actions">
          <button type="button" className="dashboard-link-btn dashboard-listing-btn is-primary" onClick={Recruiter}>
            Manage Listing
          </button>
          <button type="button" className="dashboard-link-btn dashboard-listing-btn" onClick={Recruitee}>
            Browse Listings
          </button>
        </div>
      </>
    );
  }

  useEffect(() => {
    return () => {
      if (copyResetTimerRef.current) {
        clearTimeout(copyResetTimerRef.current);
      }
    };
  }, []);

  if (loading) {
    return <LoadingScreen />;
  }
  return (
    <div className="Dashboard">
      <section className="dashboard-layout">
        <section className="dashboard-hero">
          <aside className="dashboard-hero-left">
            <div className="dashboard-townhall-shell">
              {townHallImage ? (
                <img
                  src={townHallImage}
                  alt={`Town Hall level ${townhall}`}
                  className="dashboard-townhall-image"
                />
              ) : (
                <div className="dashboard-townhall-fallback">Town Hall</div>
              )}
            </div>
          </aside>

          <div className="dashboard-hero-main">
            <div className="dashboard-hero-copy">
              <p className="dashboard-eyebrow">Dashboard</p>
              <h1 className="dashboard-welcome">Welcome {normalizedUser || "Player"}</h1>
              <p className="dashboard-subtitle">
                Jump into clan search quickly, and manage recruiting when available.
              </p>
            </div>

            <div className="dashboard-actions">
              <button
                type="button"
                className="dashboard-btn dashboard-btn-primary"
                onClick={Recruitee}
              >
                Look for Clans
              </button>

              {canRecruit && (
                <button
                  type="button"
                  className="dashboard-btn dashboard-btn-secondary"
                  onClick={Recruiter}
                >
                  Recruit
                </button>
              )}
            </div>
          </div>

          <aside className="dashboard-hero-right">
            {clanBadge ? (
              <img
                src={clanBadge}
                alt={`${clanName} badge`}
                className="dashboard-panel-badge"
              />
            ) : (
              <div className="dashboard-clan-placeholder">Clan Badge</div>
            )}
            <p className="dashboard-clan-name">{clanDisplay}</p>
          </aside>
        </section>

        <section className="dashboard-stats-strip">
          <article className="dashboard-stat-tile">
            <p className="dashboard-stat-box-title">Tag</p>
            {normalizedPlayerTag ? (
              <div className="dashboard-tag-inline">
                <button
                  type="button"
                  className="dashboard-tag-copy-btn"
                  onClick={() => copyTag(normalizedPlayerTag)}
                >
                  {`#${normalizedPlayerTag}`}
                </button>
                <span className={`dashboard-tag-copied-inline${copiedTag === normalizedPlayerTag ? " is-visible" : ""}`}>
                  ✓ Copied
                </span>
              </div>
            ) : (
              <p className="dashboard-stat-line">#{playerTag}</p>
            )}
          </article>
          <article className="dashboard-stat-tile">
            <p className="dashboard-stat-box-title">Level</p>
            <p className="dashboard-stat-line">{playerLevel}</p>
          </article>
          <article className="dashboard-stat-tile">
            <p className="dashboard-stat-box-title">League</p>
            <p className="dashboard-stat-line">{leagueName}</p>
          </article>
          <article className="dashboard-stat-tile">
            <p className="dashboard-stat-box-title">Builder League</p>
            <p className="dashboard-stat-line">{builderLeagueName}</p>
          </article>
          <article className="dashboard-stat-tile">
            <p className="dashboard-stat-box-title">Builder Hall</p>
            <p className="dashboard-stat-line">{builderHallLevel}</p>
          </article>
        </section>

        <section className="dashboard-content-grid">
          <div className="dashboard-primary-column">
            <article className="dashboard-section-card dashboard-listing-card">
              <header className="dashboard-section-header dashboard-listing-header">
                <h2>Your Listing</h2>
                <span className={`dashboard-listing-chip ${listingChip.className}`}>{listingChip.label}</span>
              </header>
              <div className="dashboard-listing-body">
                {renderListingContent()}
              </div>
            </article>
          </div>

          <aside className="dashboard-secondary-column">
            <article className="dashboard-section-card dashboard-current-clan-card">
              <header className="dashboard-section-header">
                <h2>Current Clan</h2>
              </header>
              <div className="dashboard-current-clan-grid">
                <div className="dashboard-current-clan-row">
                  <span className="dashboard-current-label">Name</span>
                  <span className="dashboard-current-value">{clanDisplay}</span>
                </div>
                <div className="dashboard-current-clan-row">
                  <span className="dashboard-current-label">Tag</span>
                  {normalizedClanTag ? (
                    <div className="dashboard-tag-inline dashboard-tag-inline-right">
                      <button
                        type="button"
                        className="dashboard-current-value dashboard-tag-copy-btn dashboard-tag-copy-btn-inline"
                        onClick={() => copyTag(normalizedClanTag)}
                      >
                        {`#${normalizedClanTag}`}
                      </button>
                      <span className={`dashboard-tag-copied-inline${copiedTag === normalizedClanTag ? " is-visible" : ""}`}>
                        ✓ Copied
                      </span>
                    </div>
                  ) : (
                    <span className="dashboard-current-value">{clanTag}</span>
                  )}
                </div>
                <div className="dashboard-current-clan-row">
                  <span className="dashboard-current-label">Role</span>
                  <span className="dashboard-current-value">{clanRole}</span>
                </div>
              </div>
            </article>

            <article className="dashboard-section-card dashboard-saved-card">
              <header className="dashboard-section-header">
                <h2>Saved Clans</h2>
              </header>
              <div className="dashboard-saved-list">
                <div className="dashboard-saved-item">
                  <p className="dashboard-saved-name">Saved Clan</p>
                  <p className="dashboard-saved-meta">Quick access</p>
                </div>
                <div className="dashboard-saved-item">
                  <p className="dashboard-saved-name">Saved Clan</p>
                  <p className="dashboard-saved-meta">Quick access</p>
                </div>
                <div className="dashboard-saved-item">
                  <p className="dashboard-saved-name">Saved Clan</p>
                  <p className="dashboard-saved-meta">Quick access</p>
                </div>
                <button type="button" className="dashboard-link-btn dashboard-saved-footer-btn" onClick={Recruitee}>
                  View Clan Search
                </button>
              </div>
            </article>

          </aside>
        </section>
      </section>
    </div>
  );
}

export default Dashboard;
