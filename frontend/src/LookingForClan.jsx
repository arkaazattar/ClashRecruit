import { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router";
import "./LookingForClan.css";
import LoadingScreen from "./components/LoadingScreen";

function LookingForClan() {
    const navigate = useNavigate()
    const [Locations, setLocations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [Filters, setFilters] = useState({
      name: null,
      minTownhall: null,
      minLeague: null,
      minMembers: null,
      maxMembers: null,
      minClanLevel: null,
      warFrequency: null,
      clanPoints: null,
      location: null,
    });
    
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

    useEffect(() => {
      getLocations();
      setLoading(false);
    }, []);

    const handleFilterSubmit = (e) => {
      e.preventDefault();
      fetch("/recruitee", {
        method: 'POST',
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          "filters": {
            "name": Filters.name,
            "minClanLevel": Number(Filters.minClanLevel),
            "clanPoints": Number(Filters.clanPoints),
            "warFrequency": Filters.warFrequency,
            "location": Filters.location,
            "requirements":{
              "townhall": Number(Filters.minTownhall),
              "league": Number(Filters.minLeague),
              "members": {
                "max": Number(Filters.maxMembers),
                "min": Number(Filters.minMembers),
                } 
             }
          }
        })
      }
      );
    }

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
        <input type="number" name="minTownhall" value={Filters.minTownhall} onChange={handleFilterChange} />
      </label>

      <label>
        Min League
        <input type="number" name="minLeague" value={Filters.minLeague} onChange={handleFilterChange} min={0} max={34} />
      </label>

      <label>
        Min Members
        <input type="number" name="minMembers" value={Filters.minMembers} onChange={handleFilterChange} />
      </label>

      <label>
        Max Members
        <input type="number" name="maxMembers" value={Filters.maxMembers} onChange={handleFilterChange} />
      </label>

      <label>
        Min Clan Level
        <input type="number" name="minClanLevel" value={Filters.minClanLevel} onChange={handleFilterChange} />
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
          <option value={null}>All Locations</option>
          {Locations.map((location) => (
            <option value={location.name}>
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



    {/* <div className="listing-grid">
      {visibleClans.map((clan) => (
        <button
          key={clan.clan_tag}
          type="button"
          className="listing-card"
          onClick={() => navigate(`/looking-for-clan/${clan.clan_tag}`, {clanTag:clan.clan_tag})}
        >
          <div className="listing-top">
            <h3>{clan.name || clan.clan_info?.name || clan.clan_tag}</h3>
            <span className="listing-location">{normalizeLocation(clan.clan_info?.location) || "Unknown"}</span>
          </div>

          <div className="listing-stats">
            <p><strong>Townhall:</strong> {clan.requirements?.[2] ?? 0}</p>
            <p><strong>League:</strong> {clan.requirements?.[0] ?? 0}</p>
            {clan.clan_info.warFrequency != "unknown" &&
              <p><strong>War Freq:</strong> {clan.clan_info?.warFrequency ?? clan.clan_info?.war_frequency ?? "unknown"}</p>
            }
            <p><strong>Clan Points:</strong> {clan.clan_info?.clanPoints ?? clan.clan_info?.clan_points ?? 0}</p>
          </div>

          <p className="listing-description">
            {clan.clan_info?.description || "No description provided."}
          </p>
        </button>
      ))}
    </div> */}

    
    </section>
);
}


export default LookingForClan
