import { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router";
import "./LookingForClan.css";
import LoadingScreen from "./components/LoadingScreen";

const PAGE_SIZE = 10;

function normalizeLocation(rawLocation) {
  if (!rawLocation) return "";
  if (typeof rawLocation === "string") return rawLocation.trim();
  if (typeof rawLocation === "object") return (rawLocation.name || "").trim();
  return "";
}

function getLocationId(rawLocation) {
  if (!rawLocation || typeof rawLocation !== "object") return "";
  const id = rawLocation.id;
  return id === null || id === undefined ? "" : String(id);
}

function LookingForClan() {
    const navigate = useNavigate()
    const [clanList, setClanList] = useState([]);
    const [allLocations, setAllLocations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);
    const [draftFilters, setDraftFilters] = useState({
      name: "",
      minLeague: "",
      minMembers: "",
      maxMembers: "",
      minClanLevel: "",
      warFrequency: "",
      clanPoints: "",
      locationId: "",
    });
    const [appliedFilters, setAppliedFilters] = useState({
      name: "",
      minLeague: "",
      minMembers: "",
      maxMembers: "",
      minClanLevel: "",
      warFrequency: "",
      clanPoints: "",
      locationId: "",
    });

    const handleFilterSubmit = (e) => {
      e.preventDefault();
      setAppliedFilters(draftFilters);
      setVisibleCount(PAGE_SIZE);
    };

    const handleFilterChange = (e) => {
      const { name, value } = e.target;
      setDraftFilters((prev) => ({
        ...prev,
        [name]: value,
      }));
    };

    useEffect(() => {
    Promise.allSettled([
      fetch("/recruitee", { credentials: "include" }),
      fetch("/clash_locations", { credentials: "include" }),
    ])
      .then(async ([clansResult, locationsResult]) => {
        if (clansResult.status === "fulfilled" && clansResult.value.ok) {
          const clansData = await clansResult.value.json();
          setClanList(Array.isArray(clansData) ? clansData : []);
        } else {
          setClanList([]);
        }

        if (locationsResult.status === "fulfilled" && locationsResult.value.ok) {
          const locationsData = await locationsResult.value.json();
          setAllLocations(Array.isArray(locationsData) ? locationsData : []);
        } else {
          setAllLocations([]);
        }
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

useEffect(() => {
  setVisibleCount(PAGE_SIZE);
}, [clanList.length]);

const locationOptions = useMemo(() => {
  const uniqueLocations = new Set();

  allLocations.forEach((location) => {
    if (location?.id !== undefined && location?.id !== null && location?.name) {
      uniqueLocations.add(JSON.stringify({ id: String(location.id), name: location.name }));
    }
  });

  clanList.forEach((clan) => {
    const locationName = normalizeLocation(clan.clan_info?.location);
    const locationId = getLocationId(clan.clan_info?.location);
    if (locationName && locationId) {
      uniqueLocations.add(JSON.stringify({ id: locationId, name: locationName }));
    }
  });

  return Array.from(uniqueLocations)
    .map((location) => JSON.parse(location))
    .sort((a, b) => a.name.localeCompare(b.name));
}, [allLocations, clanList]);

const locationNameById = useMemo(() => {
  return new Map(locationOptions.filter((location) => location.id).map((location) => [location.id, location.name.toLowerCase()]));
}, [locationOptions]);

const filteredClans = clanList.filter((clan) => {
  const details = clan.clan_info || {};
  const requiredLeague = clan.requirements?.[0] ?? 0;
  const memberCount = details.member_count ?? 0;
  const clanLevel = details.clan_level ?? 0;
  const warFrequency = (details.war_frequency ?? details.warFrequency ?? "").toLowerCase();
  const normalizedWarFrequency = warFrequency.replace(/[^a-z]/g, "");
  const clanPoints = details.clan_points ?? details.clanPoints ?? 0;
  const location = normalizeLocation(details.location).toLowerCase();
  const locationId = getLocationId(details.location);
  const clanName = (details.name ?? clan.clan_tag ?? "").toLowerCase();

  if (appliedFilters.minLeague !== "" && requiredLeague < Number(appliedFilters.minLeague)) return false;
  if (appliedFilters.minMembers !== "" && memberCount < Number(appliedFilters.minMembers)) return false;
  if (appliedFilters.maxMembers !== "" && memberCount > Number(appliedFilters.maxMembers)) return false;
  if (appliedFilters.minClanLevel !== "" && clanLevel < Number(appliedFilters.minClanLevel)) return false;
  if (appliedFilters.clanPoints !== "" && clanPoints < Number(appliedFilters.clanPoints)) return false;
  if (appliedFilters.warFrequency && normalizedWarFrequency !== appliedFilters.warFrequency.toLowerCase()) return false;
  if (appliedFilters.locationId) {
    if (locationId) {
      if (locationId !== appliedFilters.locationId) return false;
    } else {
      const selectedLocationName = locationNameById.get(appliedFilters.locationId);
      if (!selectedLocationName || location !== selectedLocationName) return false;
    }
  }
  if (appliedFilters.name && !clanName.includes(appliedFilters.name.toLowerCase())) return false;

  return true;
});

const visibleClans = filteredClans.slice(0, visibleCount);
const canLoadMore = visibleClans.length < filteredClans.length;

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
        <input type="text" name="name" value={draftFilters.name} onChange={handleFilterChange} />
      </label>

      <label>
        Min League
        <input type="number" name="minLeague" value={draftFilters.minLeague} onChange={handleFilterChange} min={0} max={34} />
      </label>

      <label>
        Min Members
        <input type="number" name="minMembers" value={draftFilters.minMembers} onChange={handleFilterChange} />
      </label>

      <label>
        Max Members
        <input type="number" name="maxMembers" value={draftFilters.maxMembers} onChange={handleFilterChange} />
      </label>

      <label>
        Min Clan Level
        <input type="number" name="minClanLevel" value={draftFilters.minClanLevel} onChange={handleFilterChange} />
      </label>

      <label>
        War Freq
        <select name="warFrequency" value={draftFilters.warFrequency} onChange={handleFilterChange}>
          <option value="">All</option>
          <option value="always">Always</option>
          <option value="onceperweek">Once a week</option>
          <option value="morethanonceperweek">More than once a week</option>
          <option value="never">Never</option>
          <option value="unknown">Unknown</option>
        </select>
      </label>

      <label>
        Min Clan Points
        <input type="number" name="clanPoints" value={draftFilters.clanPoints} onChange={handleFilterChange} />
      </label>

      <label>
        Location
        <select name="locationId" value={draftFilters.locationId} onChange={handleFilterChange}>
          <option value="">All Locations</option>
          {locationOptions.map((location) => (
            <option key={`${location.id}-${location.name}`} value={location.id}>
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
      {visibleClans.map((clan) => (
        <button
          key={clan.clan_tag}
          type="button"
          className="listing-card"
          onClick={() => navigate(`/looking-for-clan/${clan.clan_tag}`, {clanTag:clan.clan_tag})}
        >
          <div className="listing-top">
            <h3>{clan.clan_tag}</h3>
            <span className="listing-location">{normalizeLocation(clan.clan_info?.location) || "Unknown"}</span>
          </div>

          <div className="listing-stats">
            <p><strong>Townhall:</strong> {clan.requirements?.[2] ?? 0}</p>
            <p><strong>League:</strong> {clan.requirements?.[0] ?? 0}</p>
            <p><strong>War Freq:</strong> {clan.clan_info?.warFrequency ?? clan.clan_info?.war_frequency ?? "unknown"}</p>
            <p><strong>Clan Points:</strong> {clan.clan_info?.clanPoints ?? clan.clan_info?.clan_points ?? 0}</p>
          </div>

          <p className="listing-description">
            {clan.clan_info?.description || "No description provided."}
          </p>
        </button>
      ))}
    </div>

    {canLoadMore && (
      <div className="listing-load-more-wrap">
        <button
          type="button"
          className="listing-load-more"
          onClick={() => setVisibleCount((prev) => prev + PAGE_SIZE)}
        >
          Load 10 More Clans
        </button>
      </div>
    )}
  </section>
);
}


export default LookingForClan
