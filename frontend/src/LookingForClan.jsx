import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import "./LookingForClan.css";
import LoadingScreen from "./components/LoadingScreen";

function LookingForClan() {
    const navigate = useNavigate()
    const [clanList, setClanList] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState({
      name: "",
      minMembers: "",
      maxMembers: "",
      minClanLevel: "",
      warFrequency: "",
      clanPoints: "",
      location: "",
    });

    const handleFilterSubmit = (e) => {
      e.preventDefault();
    };

    const handleFilterChange = (e) => {
      const { name, value } = e.target;
      setFilters((prev) => ({
        ...prev,
        [name]: value,
      }));
    };

    useEffect(() => {
    fetch("/recruitee", {
      credentials: "include",
    })
      .then((res) => res.json())
      .then((data) => {
        setClanList(data);
        setLoading(false);
      })
  }, []);

const filteredClans = clanList.filter((clan) => {
  const details = clan.clan_info || {};
  const memberCount = details.member_count ?? 0;
  const clanLevel = details.clan_level ?? 0;
  const warFrequency = (details.war_frequency ?? details.warFrequency ?? "").toLowerCase();
  const normalizedWarFrequency = warFrequency.replace(/[^a-z]/g, "");
  const clanPoints = details.clan_points ?? details.clanPoints ?? 0;
  const location = (details.location ?? "").toLowerCase();
  const clanName = (details.name ?? clan.clan_tag ?? "").toLowerCase();

  if (filters.minMembers !== "" && memberCount < Number(filters.minMembers)) return false;
  if (filters.maxMembers !== "" && memberCount > Number(filters.maxMembers)) return false;
  if (filters.minClanLevel !== "" && clanLevel < Number(filters.minClanLevel)) return false;
  if (filters.clanPoints !== "" && clanPoints < Number(filters.clanPoints)) return false;
  if (filters.warFrequency && normalizedWarFrequency !== filters.warFrequency.toLowerCase()) return false;
  if (filters.location && !location.includes(filters.location.toLowerCase())) return false;
  if (filters.name && !clanName.includes(filters.name.toLowerCase())) return false;

  return true;
});

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
        <input type="text" name="name" value={filters.name} onChange={handleFilterChange} />
      </label>

      <label>
        Min Members
        <input type="number" name="minMembers" value={filters.minMembers} onChange={handleFilterChange} />
      </label>

      <label>
        Max Members
        <input type="number" name="maxMembers" value={filters.maxMembers} onChange={handleFilterChange} />
      </label>

      <label>
        Min Clan Level
        <input type="number" name="minClanLevel" value={filters.minClanLevel} onChange={handleFilterChange} />
      </label>

      <label>
        War Freq
        <select name="warFrequency" value={filters.warFrequency} onChange={handleFilterChange}>
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
        <input type="number" name="clanPoints" value={filters.clanPoints} onChange={handleFilterChange} />
      </label>

      <label>
        Location
        <select name="location" value={filters.location} onChange={handleFilterChange}>
          <option value="">All (full location list coming later)</option>
        </select>
      </label>

      <div className="looking-filters-actions">
        <button type="submit" className="looking-filter-submit">
          Apply Filters
        </button>
      </div>
    </form>

    <div className="listing-grid">
      {filteredClans.map((clan) => (
        <button
          key={clan.clan_tag}
          type="button"
          className="listing-card"
          onClick={() => navigate(`/looking-for-clan/${clan.clan_tag}`, {clanTag:clan.clan_tag})}
        >
          <div className="listing-top">
            <h3>{clan.clan_tag}</h3>
            <span className="listing-location">{clan.clan_info?.location || "Unknown"}</span>
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
  </section>
);
}


export default LookingForClan
