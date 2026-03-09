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

function LookingForClan() {
    const navigate = useNavigate()
    const [Locations, setLocations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [clans, setClans] = useState([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalResults, setTotalResults] = useState(0);
    const [hasAppliedFilters, setHasAppliedFilters] = useState(false);
    const [appliedFilterPayload, setAppliedFilterPayload] = useState(null);
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

    const handleFilterSubmit = async (e) => {
      e.preventDefault();
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

if (loading){
  return <LoadingScreen />;
}

return (
  <section className="looking-page">
    <div className="looking-header">
      <h2>Find a Clan</h2>
      <p>Browse active listings that match your profile.</p>
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
      {clans.map((clan) => (
        <button
          key={clan.clan_tag}
          type="button"
          className="listing-card"
          onClick={() => navigate(`/looking-for-clan/${clan.clan_tag}`, {clanTag:clan.clan_tag})}
        >
          <div className="listing-top">
            <h3>{clan.name || clan.clan_info?.name || clan.clan_tag}</h3>
            <span className="listing-location">{(clan.clan_info.location["name"])}</span>
          </div>

          <div className="listing-stats">
            <p><strong>Townhall:</strong> {clan.requirements[2]}</p>
            <p><strong>League:</strong> {clan.requirements[0]}</p>
            {clan.clan_info.warFrequency !== "unknown" &&
              <p><strong>War Freq:</strong> {clan.clan_info["warFrequency"]}</p>
            }
            <p><strong>Clan Points:</strong> {clan.clan_info["clanPoints"]}</p>
          </div>

          <p className="listing-description">
            {clan.clan_info["description"] || "No description provided."}
          </p>
        </button>
      ))}
    </div>
    {pageNumbers.length > 1 && (
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
