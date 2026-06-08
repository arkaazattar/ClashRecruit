import { useState, useEffect, useRef } from "react";
import { Link, useOutletContext } from "react-router-dom";
import LoadingScreen from "./components/LoadingScreen";
import usePageTitle from "./hooks/usePageTitle";
import "./Dashboard.css";

const townHallAssets = require.context("./assets", false, /\.webp$/);
const townHallAssetOverrides = {
  12: "./Town_Hall12-5.webp",
  13: "./Town-hall-13-5.webp",
  14: "./Town_Hall14-5.webp",
  15: "./Town_Hall15-5.webp",
};

function getTownHallAsset(townhallLevel, weaponLevel) {
  if (!townhallLevel) {
    return null;
  }

  const level = Number(townhallLevel);
  const weapon = Number(weaponLevel);
  const assetNames = [];

  if (!Number.isFinite(level)) {
    return null;
  }

  if (level === 17) {
    if (weapon) {
      assetNames.push(`./Town_Hall17-${weapon}.webp`);
    }
    assetNames.push("./Town_Hall17-5.webp");
  }

  if (townHallAssetOverrides[level]) {
    assetNames.push(townHallAssetOverrides[level]);
  }

  assetNames.push(`./Town_Hall${level}.webp`);

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

function readStoredUserInfo(username) {
  if (!username) {
    return null;
  }

  try {
    const storedValue = sessionStorage.getItem("dashboard_user_info");
    if (!storedValue) {
      return null;
    }

    const parsed = JSON.parse(storedValue);
    if (parsed.username !== username || !parsed.data) {
      return null;
    }

    return normalizeUserInfo(parsed.data);
  } catch {
    return null;
  }
}

function storeUserInfo(username, data) {
  if (!username) {
    sessionStorage.removeItem("dashboard_user_info");
    return;
  }

  sessionStorage.setItem(
    "dashboard_user_info",
    JSON.stringify({ username, data })
  );
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

function normalizeSavedClanTag(tagValue) {
  if (!tagValue) {
    return null;
  }

  const normalized = String(tagValue).trim().replace(/^#+/, "");
  if (!normalized) {
    return null;
  }

  return normalized;
}

function Dashboard() {
  usePageTitle("Dashboard | ClashRecruit")
  const { user, townhall, townhallWeaponLevel, recruitStatus, hasActiveListing, sessionStateLoaded } = useOutletContext();
  const normalizedUser = user === "Guest" ? null : user;

  const [loading, setLoading] = useState(true);
  const [townHallImage, setTownHallImage] = useState(null);
  const [userInfo, setUserInfo] = useState(
    () => readStoredUserInfo(normalizedUser)
  );
  const [savedClans, setSavedClans] = useState([]);
  const [savedClansError, setSavedClansError] = useState("");
  const [savedClansActionError, setSavedClansActionError] = useState("");
  const [savedClansModalOpen, setSavedClansModalOpen] = useState(false);
  const [removingSavedClanTag, setRemovingSavedClanTag] = useState("");
  const [copiedTag, setCopiedTag] = useState("");
  const copyResetTimerRef = useRef(null);

  useEffect(() => {
    if (!sessionStateLoaded) {
      setTownHallImage(null);
      return undefined;
    }

    let isMounted = true;
    const resolvedTownHallImage = getTownHallAsset(
      townhall,
      townhallWeaponLevel
    );

    preloadImage(resolvedTownHallImage).then(() => {
      if (isMounted) {
        setTownHallImage(resolvedTownHallImage);
      }
    });

    return () => {
      isMounted = false;
    };
  }, [sessionStateLoaded, townhall, townhallWeaponLevel]);

  useEffect(() => {
    if (!sessionStateLoaded) {
      setLoading(true);
      return;
    }

    let isMounted = true;
    setLoading(true);
    setUserInfo(readStoredUserInfo(normalizedUser));

    Promise.all([
      fetch("/session-state/user-info", { credentials: "include" })
        .then((res) => {
          if (!res.ok) {
            return undefined;
          }

          return res.json();
        })
        .then((data) => {
          if (data === undefined) {
            return undefined;
          }

          storeUserInfo(normalizedUser, data);
          return normalizeUserInfo(data);
        })
        .catch(() => undefined),
      fetch("/saved-clans", { credentials: "include" })
        .then(async (res) => {
          if (!res.ok) {
            throw new Error("Saved clans are temporarily unavailable.");
          }
          return res.json();
        })
        .then((data) => {
          const savedClanList = Array.isArray(data.saved_clans) ? data.saved_clans : [];
          return { savedClanList, savedError: "" };
        })
        .catch((error) => ({
          savedClanList: [],
          savedError: error.message || "Saved clans are temporarily unavailable.",
        })),
    ])
      .then(([nextUserInfo, nextSaved]) => {
        if (!isMounted) {
          return;
        }

        if (nextUserInfo !== undefined) {
          setUserInfo(nextUserInfo);
        }
        setSavedClans(nextSaved.savedClanList);
        setSavedClansError(nextSaved.savedError);
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
  }, [sessionStateLoaded, normalizedUser]);

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
  const isInClan = Boolean(clan);
  const canManageListing = recruitStatus === true;
  const listingExists = Boolean(hasActiveListing);
  const listingChip = getListingChipMeta();
  const clanListingPath = normalizedClanTag && listingExists ? `/looking-for-clan/${normalizedClanTag}` : "";
  const hasSavedClans = savedClans.length > 0;
  const savedClansPreview = savedClans.slice(0, 2);
  const remainingSavedClansCount = Math.max(savedClans.length - savedClansPreview.length, 0);

  const openSavedClansModal = () => {
    setSavedClansModalOpen(true);
  };

  const closeSavedClansModal = () => {
    setSavedClansModalOpen(false);
  };

  const removeSavedClan = async (clanTag) => {
    const normalizedTag = normalizeSavedClanTag(clanTag);
    if (!normalizedTag || removingSavedClanTag) {
      return;
    }

    setRemovingSavedClanTag(normalizedTag);
    setSavedClansActionError("");

    try {
      const response = await fetch(`/saved-clans/${encodeURIComponent(normalizedTag)}`, {
        method: "DELETE",
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Could not remove saved clan.");
      }

      setSavedClans((currentSavedClans) => (
        currentSavedClans.filter((savedClan) => (
          normalizeSavedClanTag(savedClan.clan_tag) !== normalizedTag
        ))
      ));
    } catch (error) {
      setSavedClansActionError(error.message || "Could not remove saved clan.");
    } finally {
      setRemovingSavedClanTag("");
    }
  };

  function renderSavedClanRow(savedClan, keyPrefix, index) {
    const savedClanTag = normalizeSavedClanTag(savedClan.clan_tag);
    const savedClanTagForRoute = savedClanTag || "";
    const savedClanName = savedClan.name || savedClan.clan_info?.name || savedClanTag || "Saved Clan";
    const savedClanLocation = savedClan.clan_info?.location?.name;
    const savedClanMeta = savedClan.listing_available
      ? (savedClanLocation || "Listing active")
      : "Listing no longer available";
    const rowKeyBase = savedClanTagForRoute || `${savedClanName}-${index}`;
    const rowKey = `${keyPrefix}-${rowKeyBase}`;
    const canOpenListing = Boolean(savedClan.listing_available && savedClanTagForRoute);
    const isRemoving = savedClanTag === removingSavedClanTag;
    const removeButton = savedClanTag ? (
      <button
        type="button"
        className="dashboard-saved-remove-btn"
        onClick={() => removeSavedClan(savedClanTag)}
        disabled={isRemoving}
        aria-label={`Remove ${savedClanName} from saved clans`}
        title="Remove saved clan"
      >
        <span aria-hidden="true">×</span>
      </button>
    ) : null;

    return (
      <div key={rowKey} className="dashboard-saved-item">
        {canOpenListing ? (
          <Link
            to={`/looking-for-clan/${savedClanTagForRoute}`}
            className="dashboard-saved-item-content dashboard-saved-item-clickable"
          >
            <div className="dashboard-saved-text">
              <p className="dashboard-saved-name">{savedClanName}</p>
              <p className="dashboard-saved-meta">{savedClanMeta}</p>
            </div>
            <span className="dashboard-saved-row-icon" aria-hidden="true">›</span>
          </Link>
        ) : (
          <div className="dashboard-saved-item-content">
            <div className="dashboard-saved-text">
              <p className="dashboard-saved-name">{savedClanName}</p>
              <p className="dashboard-saved-meta">{savedClanMeta}</p>
            </div>

            {savedClanTag ? (
              <div className="dashboard-tag-inline dashboard-tag-inline-right dashboard-saved-tag-wrap">
                <button
                  type="button"
                  className="dashboard-current-value dashboard-tag-copy-btn dashboard-tag-copy-btn-inline"
                  onClick={() => copyTag(savedClanTag)}
                >
                  {`#${savedClanTag}`}
                </button>
                <span className={`dashboard-tag-copied-inline${copiedTag === savedClanTag ? " is-visible" : ""}`}>
                  ✓ Copied
                </span>
              </div>
            ) : null}
          </div>
        )}
        {removeButton}
      </div>
    );
  }

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
            <Link to="/looking-for-clan" className="dashboard-link-btn dashboard-listing-btn is-primary">
              Find a Clan
            </Link>
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
            <Link to="/looking-for-clan" className="dashboard-link-btn dashboard-listing-btn is-primary">
              Browse Listings
            </Link>
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
            <Link to="/looking-for-clan" className="dashboard-link-btn dashboard-listing-btn is-primary">
              Browse Listings
            </Link>
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
            <Link to="/recruit" className="dashboard-link-btn dashboard-listing-btn is-primary">
              Create Listing
            </Link>
            <Link to="/looking-for-clan" className="dashboard-link-btn dashboard-listing-btn">
              Browse Listings
            </Link>
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
          <Link to="/recruit" className="dashboard-link-btn dashboard-listing-btn is-primary">
            Manage Listing
          </Link>
          <Link to="/looking-for-clan" className="dashboard-link-btn dashboard-listing-btn">
            Browse Listings
          </Link>
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

  useEffect(() => {
    if (!savedClansModalOpen) {
      return undefined;
    }

    const previousOverflow = document.body.style.overflow;
    const handleEscClose = (event) => {
      if (event.key === "Escape") {
        closeSavedClansModal();
      }
    };

    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", handleEscClose);

    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", handleEscClose);
    };
  }, [savedClansModalOpen]);

  if (loading) {
    return <LoadingScreen />;
  }
  return (
    <div className="Dashboard">
      <div className="dashboard-atmosphere" aria-hidden="true" />
      <section className="dashboard-layout">
        <section className="dashboard-hero">
          <div className="dashboard-hero-layer dashboard-hero-layer-one" aria-hidden="true" />
          <div className="dashboard-hero-layer dashboard-hero-layer-two" aria-hidden="true" />
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

          </div>

          <aside className="dashboard-hero-right">
            {clanListingPath ? (
              <Link to={clanListingPath} className="dashboard-clan-link">
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
                <p className="dashboard-clan-role">{clanRole}</p>
              </Link>
            ) : (
              <div className="dashboard-clan-summary">
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
                <p className="dashboard-clan-role">{clanRole}</p>
              </div>
            )}
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
            <article className="dashboard-section-card dashboard-saved-card">
              <header className="dashboard-section-header">
                <h2>Saved Clans</h2>
              </header>
              <div className="dashboard-saved-list">
                {savedClansError && (
                  <p className="dashboard-saved-empty">{savedClansError}</p>
                )}

                {savedClansActionError && (
                  <p className="dashboard-saved-action-error">{savedClansActionError}</p>
                )}

                {!savedClansError && !hasSavedClans && (
                  <p className="dashboard-saved-empty">Save clans from search to keep a shortlist here.</p>
                )}

                {!savedClansError && hasSavedClans && savedClansPreview.map((savedClan, index) => (
                  renderSavedClanRow(savedClan, "preview", index)
                ))}

                {!savedClansError && remainingSavedClansCount > 0 && (
                  <p className="dashboard-saved-more">{`+${remainingSavedClansCount} more saved`}</p>
                )}

                {!savedClansError && hasSavedClans && (
                  <button type="button" className="dashboard-link-btn dashboard-saved-footer-btn" onClick={openSavedClansModal}>
                    {`View all ${savedClans.length} saved clans`}
                  </button>
                )}

              </div>
            </article>

          </aside>
        </section>
      </section>

      {savedClansModalOpen && (
        <div className="dashboard-saved-modal-overlay" onClick={closeSavedClansModal} role="presentation">
          <section
            className="dashboard-saved-modal"
            role="dialog"
            aria-modal="true"
            aria-label="Saved Clans"
            onClick={(event) => event.stopPropagation()}
          >
            <header className="dashboard-saved-modal-header">
              <h2>Saved Clans</h2>
              <button
                type="button"
                className="dashboard-saved-modal-close"
                onClick={closeSavedClansModal}
                aria-label="Close saved clans modal"
              >
                <span aria-hidden="true">×</span>
              </button>
            </header>

            <div className="dashboard-saved-modal-list">
              {savedClansActionError && (
                <p className="dashboard-saved-action-error">{savedClansActionError}</p>
              )}
              {savedClans.map((savedClan, index) => renderSavedClanRow(savedClan, "modal", index))}
            </div>
          </section>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
