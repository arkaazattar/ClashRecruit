import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./LookingForClan.css";
import LoadingScreen from "./components/LoadingScreen";

const PAGE_SIZE = 10;

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
  return isRandomMode ? clan.clanLevel ?? "N/A" : clan.requirements?.[2] ?? "N/A";
}

function getSecondaryStat(clan, isRandomMode) {
  return isRandomMode ? clan.members ?? "N/A" : clan.requirements?.[0] ?? "N/A";
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

function LookingForClan() {
    const navigate = useNavigate()
    const [Locations, setLocations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [clans, setClans] = useState([]);
    const [randomClans, setRandomClans] = useState([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalResults, setTotalResults] = useState(0);
    const [hasAppliedFilters, setHasAppliedFilters] = useState(false);
    const [appliedFilterPayload, setAppliedFilterPayload] = useState(null);
    const [isRandomMode, setIsRandomMode] = useState(false);
    const [randomError, setRandomError] = useState("");
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

    async function fetchClanPage(page, filterPayload = appliedFilterPayload) {
      const offset = (page - 1) * PAGE_SIZE;
      const url = `/recruitee?limit=${PAGE_SIZE}&offset=${offset}`;
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
      setClans(payload.items || []);
      setTotalResults(payload.total || 0);
      setCurrentPage(page);
    }

    async function fetchRandomClans() {
      const payload = buildRandomFilterPayload(Filters, Locations);
      const response = await fetch("/search_clans", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      setRandomClans(data.items || []);
      setRandomError((data.items || []).length ? "" : "No random clans matched these filters.");
    }

    const handleFilterSubmit = async (e) => {
      e.preventDefault();
      if (isRandomMode) {
        await fetchRandomClans();
        return;
      }

      setHasAppliedFilters(true);
      const payload = buildFilterPayload(Filters);
      setAppliedFilterPayload(payload);
      await fetchClanPage(1, payload);
    };

    const handlePageChange = async (nextPage) => {
      if (nextPage < 1 || nextPage > totalPages || nextPage === currentPage) {
        return;
      }

      if (hasAppliedFilters) {
        await fetchClanPage(nextPage, appliedFilterPayload);
      } else {
        await fetchClanPage(nextPage, null);
      }
    };

    const totalPages = Math.max(1, Math.ceil(totalResults / PAGE_SIZE));
    const pageNumbers = Array.from({ length: totalPages }, (_, i) => i + 1);
    const displayedClans = isRandomMode ? randomClans : clans;

if (loading){
  return <LoadingScreen />;
}

return (
  <section className="looking-page">
    <div className="looking-header">
      <h2>Find a Clan</h2>
      <p>Browse active listings that match your profile.</p>
    </div>

    <div className="looking-mode-toggle">
      <button
        type="button"
        className={`looking-mode-btn ${!isRandomMode ? "is-active" : ""}`}
        onClick={() => setIsRandomMode(false)}
      >
        Browse Listings
      </button>
      <button
        type="button"
        className={`looking-mode-btn ${isRandomMode ? "is-active" : ""}`}
        onClick={() => setIsRandomMode(true)}
      >
        Browse Random Clans
      </button>
    </div>

    <form className="looking-filters" onSubmit={handleFilterSubmit}>
      <label>
        Name
        <input type="text" name="name" value={Filters.name} onChange={handleFilterChange} />
      </label>

      <label>
        Min TH
        <input type="number" name="minTownhall" value={Filters.minTownhall} onChange={handleFilterChange} min={0} />
      </label>

      <label>
        Min League
        <input type="number" name="minLeague" value={Filters.minLeague} onChange={handleFilterChange} min={0} max={34} />
      </label>

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
      {isRandomMode && randomError && (
        <div className="looking-empty-state">
          <p>{randomError}</p>
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
              isRandomMode,
            },
          })}
        >
          <div className="listing-top">
            <h3>{getClanName(clan)}</h3>
            <span className="listing-location">{getClanLocation(clan)}</span>
          </div>

          <div className="listing-stats">
            <p><strong>{isRandomMode ? "Clan Level" : "Townhall"}:</strong> {getPrimaryStat(clan, isRandomMode)}</p>
            <p><strong>{isRandomMode ? "Members" : "League"}:</strong> {getSecondaryStat(clan, isRandomMode)}</p>
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
    {!isRandomMode && pageNumbers.length > 1 && (
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

    
    </section>
);
}

export default LookingForClan
