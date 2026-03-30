import { useRef, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./LookingForClan.css";
import LoadingScreen from "./components/LoadingScreen";

const PAGE_SIZE = 10;
const VIEW_MODE = {
  LISTINGS: "listings",
  LIVE_API: "live_api",
};

function toNumberOrNull(value) {
    return value === "" || value === null ? null : Number(value);
}

function buildFilterPayload(Filters) {
  return {
    filters: {
      name: Filters.name,
      minClanLevel: toNumberOrNull(Filters.minClanLevel),
      clanPoints: toNumberOrNull(Filters.clanPoints),
      warFrequency: Filters.warFrequency || null,
      location: Filters.location || null,
      requirements: {
        townhall: toNumberOrNull(Filters.minTownhall),
        league: toNumberOrNull(Filters.minLeague),
        members: {
          max: toNumberOrNull(Filters.maxMembers),
          min: toNumberOrNull(Filters.minMembers),
        },
      },
    },
  };
}

function buildRandomFilterPayload(Filters, locations) {
  const selectedLocation = locations.find((location) => location.name === Filters.location);

  return Object.fromEntries(
    Object.entries({
      limit: PAGE_SIZE,
      name: Filters.name || undefined,
      minMembers: toNumberOrNull(Filters.minMembers),
      maxMembers: toNumberOrNull(Filters.maxMembers),
      minClanLevel: toNumberOrNull(Filters.minClanLevel),
      minClanPoints: toNumberOrNull(Filters.clanPoints),
      warFrequency: Filters.warFrequency || undefined,
      locationId: selectedLocation?.id,
    }).filter(([, value]) => value !== undefined && value !== null && value !== "")
  );
}

function getClanKey(clan, index) {
  return clan.clan_tag || clan.tag || `clan-${index}`;
}

function getClanName(clan) {
  return clan.name || clan.clan_info?.name || clan.clan_tag || clan.tag || "Unknown clan";
}

function getClanLocation(clan) {
  return clan.clan_info?.location?.name || clan.location?.name || clan.location || "Unknown location";
}

function getClanDescription(clan) {
  return clan.clan_info?.description || clan.description || "No description provided.";
}

function getPrimaryStat(clan, isRandomMode) {
  if (isRandomMode) {
    return clan.clan_info?.clan_level ?? clan.clanLevel ?? "N/A";
  }

  return clan.requirements?.[2] ?? "N/A";
}

function getSecondaryStat(clan, isRandomMode) {
  if (isRandomMode) {
    return clan.clan_info?.member_count ?? clan.members ?? "N/A";
  }

  return clan.requirements?.[0] ?? "N/A";
}

function getWarFrequency(clan) {
  return clan.clan_info?.warFrequency || clan.warFrequency || "unknown";
}

function getClanPoints(clan) {
  return clan.clan_info?.clanPoints ?? clan.clanPoints ?? "N/A";
}

function getClanTag(clan, index) {
  return (clan.clan_tag || clan.tag || `clan-${index}`).replace(/^#/, "");
}

function getClanSourceLabel(clan) {
  if (clan.source === "clash_api_import") {
    return "Imported from API";
  }

  if (clan.source === "live_listing") {
    return "Live listing";
  }

  return "";
}

function getRandomClanErrorMessage(data) {
  if (data?.error) {
    return data.error;
  }

  if (data?.reason === "badRequest" && data?.message === "At least one filtering parameter must exist") {
    return "Add at least one Clash API filter before searching.";
  }

  return "Failed to search Clash API clans.";
}

function LookingForClan() {
    const navigate = useNavigate()
    const listingPageCacheRef = useRef({});
    const [Locations, setLocations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [clans, setClans] = useState([]);
    const [randomClans, setRandomClans] = useState([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalResults, setTotalResults] = useState(0);
    const [hasAppliedFilters, setHasAppliedFilters] = useState(false);
    const [appliedFilterPayload, setAppliedFilterPayload] = useState(null);
    const [viewMode, setViewMode] = useState(VIEW_MODE.LISTINGS);
    const [apiSearchError, setApiSearchError] = useState("");
    const [apiSearchAfter, setApiSearchAfter] = useState(null);
    const [hasApiSearchResults, setHasApiSearchResults] = useState(false);
    const [Filters, setFilters] = useState({
      name: "",
      minTownhall: "",
      minLeague: "",
      minMembers: "",
      maxMembers: "",
      minClanLevel: "",
      warFrequency: "",
      clanPoints: "",
      location: "",
    });
    
    useEffect(() => {
      const loadData = async() => {
        const response = await fetch(`/recruitee?limit=${PAGE_SIZE}&offset=0`);
        const payload = await response.json();
        setClans(payload.items || []);
        setTotalResults(payload.total || 0);
        setCurrentPage(1);
        await getLocations();
        setLoading(false);
      };
      loadData();
    }, []);
    
    const handleFilterChange = (e) => {
      const { name, value } = e.target;
      setFilters((prev) => ({
        ...prev,
        [name]: value,
      }));
    };

    async function getLocations(){
      const rsp = await fetch("/clash_locations");
      const locations = await rsp.json()
      setLocations(locations)
    }

    function getListingCacheKey(page, filterPayload) {
      return JSON.stringify({
        page,
        filterPayload: filterPayload || null,
      });
    }

    async function fetchListingPageData(page, filterPayload = appliedFilterPayload, includeTotal = true) {
      const cacheKey = getListingCacheKey(page, filterPayload);
      const cached = listingPageCacheRef.current[cacheKey];
      if (cached && (!includeTotal || typeof cached.total === "number")) {
        return cached;
      }

      const offset = (page - 1) * PAGE_SIZE;
      const url = `/recruitee?limit=${PAGE_SIZE}&offset=${offset}&includeTotal=${includeTotal ? 1 : 0}`;
      const response = filterPayload
        ? await fetch(url, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(filterPayload),
          })
        : await fetch(url);

      const payload = await response.json();
      listingPageCacheRef.current[cacheKey] = payload;
      return payload;
    }

    async function prefetchListingPage(page, filterPayload = appliedFilterPayload) {
      if (page < 1) {
        return;
      }

      const cacheKey = getListingCacheKey(page, filterPayload);
      if (listingPageCacheRef.current[cacheKey]) {
        return;
      }

      try {
        await fetchListingPageData(page, filterPayload, false);
      } catch {
        // Ignore background prefetch failures and let interactive fetch handle them.
      }
    }

    async function fetchClanPage(page, filterPayload = appliedFilterPayload, includeTotal = true) {
      const payload = await fetchListingPageData(page, filterPayload, includeTotal);
      setClans(payload.items || []);
      if (typeof payload.total === "number") {
        setTotalResults(payload.total);
      }
      setCurrentPage(page);

      const totalForPrefetch = typeof payload.total === "number" ? payload.total : totalResults;
      const totalPagesForPrefetch = Math.max(1, Math.ceil((totalForPrefetch || 0) / PAGE_SIZE));
      if (page < totalPagesForPrefetch) {
        void prefetchListingPage(page + 1, filterPayload);
      }
    }

    async function fetchRandomClans(after = null, append = false) {
      const payload = buildRandomFilterPayload(Filters, Locations);
      if (after) {
        payload.after = after;
      }

      const response = await fetch("/search_clans", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) {
        if (!append) {
          setRandomClans([]);
          setHasApiSearchResults(false);
          setApiSearchAfter(null);
        }
        setApiSearchError(getRandomClanErrorMessage(data));
        return;
      }
      const nextItems = data.items || [];
      setRandomClans((prev) => append ? [...prev, ...nextItems] : nextItems);
      setApiSearchAfter(data.after || null);
      setHasApiSearchResults(true);
      setApiSearchError(nextItems.length ? "" : "No Clash API clans matched these filters.");
    }

    const handleFilterSubmit = async (e) => {
      e.preventDefault();
      if (viewMode === VIEW_MODE.LIVE_API) {
        await fetchRandomClans(null, false);
        return;
      }

      setHasAppliedFilters(true);
      const payload = buildFilterPayload(Filters);
      setAppliedFilterPayload(payload);
      listingPageCacheRef.current = {};
      await fetchClanPage(1, payload);
    };

    const handlePageChange = async (nextPage) => {
      if (nextPage < 1 || nextPage > totalPages || nextPage === currentPage) {
        return;
      }

      if (hasAppliedFilters) {
        await fetchClanPage(nextPage, appliedFilterPayload, false);
      } else {
        await fetchClanPage(nextPage, null, false);
      }
    };

    const totalPages = Math.max(1, Math.ceil(totalResults / PAGE_SIZE));
    const pageNumbers = Array.from({ length: totalPages }, (_, i) => i + 1);
    const isListingsMode = viewMode === VIEW_MODE.LISTINGS;
    const isApiSearchMode = viewMode === VIEW_MODE.LIVE_API;
    const displayedClans = isApiSearchMode ? randomClans : clans;

if (loading){
  return <LoadingScreen />;
}

return (
  <section className="looking-page">
    <div className="looking-header">
      <h2>Find a Clan</h2>
      <p>
        {isApiSearchMode
          ? "Search clans directly from the Clash of Clans API."
          : "Browse live listings and imported API clans together."}
      </p>
    </div>

    <div className="looking-mode-toggle">
      <button
        type="button"
        className={`looking-mode-btn ${isListingsMode ? "is-active" : ""}`}
        onClick={() => setViewMode(VIEW_MODE.LISTINGS)}
      >
        Browse Listings
      </button>
      <button
        type="button"
        className={`looking-mode-btn ${isApiSearchMode ? "is-active" : ""}`}
        onClick={() => setViewMode(VIEW_MODE.LIVE_API)}
      >
        Search Clash API
      </button>
    </div>

    <form className="looking-filters" onSubmit={handleFilterSubmit}>
      <label>
        Name
        <input type="text" name="name" value={Filters.name} onChange={handleFilterChange} />
      </label>

      {isListingsMode && (
        <label>
          Min TH
          <input type="number" name="minTownhall" value={Filters.minTownhall} onChange={handleFilterChange} min={0} />
        </label>
      )}

      {isListingsMode && (
        <label>
          Min League
          <input type="number" name="minLeague" value={Filters.minLeague} onChange={handleFilterChange} min={0} max={34} />
        </label>
      )}

      <label>
        Min Members
        <input type="number" name="minMembers" value={Filters.minMembers} onChange={handleFilterChange} min={0} max={50}/>
      </label>

      <label>
        Max Members
        <input type="number" name="maxMembers" value={Filters.maxMembers} onChange={handleFilterChange} min={Filters.minMembers || 0} max={50} />
      </label>

      <label>
        Min Clan Level
        <input type="number" name="minClanLevel" value={Filters.minClanLevel} onChange={handleFilterChange}  />
      </label>

      <label>
        War Freq
        <select name="warFrequency" value={Filters.warFrequency} onChange={handleFilterChange}>
          <option value="">All</option>
          <option value="always">Always</option>
          <option value="oncePerWeek">Once a week</option>
          <option value="twicePerWeek">Twice a week</option>
          <option value="rarely">Rarely</option>
          <option value="never">Never</option>
          <option value="unknown">Unknown</option>
        </select>
      </label>

      <label>
        Min Clan Points
        <input type="number" name="clanPoints" value={Filters.clanPoints} onChange={handleFilterChange} />
      </label>

      <label>
        Location
        <select name="location" value={Filters.location} onChange={handleFilterChange}>
          <option value="">All Locations</option>
          {Locations.map((location) => (
            <option key={location.id ?? location.name} value={location.name}>
              {location.name}
            </option>
          ))}
        </select>
      </label>

    <div className="looking-filters-actions">
        <button type="submit" className="looking-filter-submit">
          Apply Filters
        </button>
      </div>
    </form>



    <div className="listing-grid">
    {isApiSearchMode && apiSearchError && (
        <div className="looking-empty-state">
          <p>{apiSearchError}</p>
        </div>
      )}

      {displayedClans.map((clan, index) => (
        <button
          key={getClanKey(clan, index)}
          type="button"
          className="listing-card"
          onClick={() => navigate(`/looking-for-clan/${getClanTag(clan, index)}/`, {
            state: {
              clanInfo: clan,
              isRandomMode: isApiSearchMode,
              isImportedMode: clan.source === "clash_api_import",
            },
          })}
        >
          <div className="listing-top">
            <div>
              <h3>{getClanName(clan)}</h3>
              {!isApiSearchMode && getClanSourceLabel(clan) && (
                <span className="listing-location">{getClanSourceLabel(clan)}</span>
              )}
            </div>
            <span className="listing-location">{getClanLocation(clan)}</span>
          </div>

          <div className="listing-stats">
            <p><strong>{isApiSearchMode ? "Clan Level" : "Townhall"}:</strong> {getPrimaryStat(clan, isApiSearchMode)}</p>
            <p><strong>{isApiSearchMode ? "Members" : "League"}:</strong> {getSecondaryStat(clan, isApiSearchMode)}</p>
            {getWarFrequency(clan) !== "unknown" &&
              <p><strong>War Freq:</strong> {getWarFrequency(clan)}</p>
            }
            <p><strong>Clan Points:</strong> {getClanPoints(clan)}</p>
          </div>

          <p className="listing-description">
            {getClanDescription(clan)}
          </p>
        </button>
      ))}
    </div>
    {isListingsMode && pageNumbers.length > 1 && (
      <div className="listing-pagination-wrap">
        {pageNumbers.map((pageNumber) => (
          <button
            key={pageNumber}
            type="button"
            className={`listing-page-btn ${pageNumber === currentPage ? "is-active" : ""}`}
            onClick={() => handlePageChange(pageNumber)}
          >
            {pageNumber}
          </button>
        ))}
      </div>
    )}

    {isApiSearchMode && hasApiSearchResults && (
      <div className="listing-pagination-wrap">
        <button
          type="button"
          className="listing-page-btn"
          onClick={() => fetchRandomClans(apiSearchAfter, true)}
          disabled={!apiSearchAfter}
        >
          {apiSearchAfter ? "Load More" : "No More Results"}
        </button>
      </div>
    )}

    
    </section>
);
}

export default LookingForClan
