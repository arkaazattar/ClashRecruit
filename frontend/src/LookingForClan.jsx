import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import "./LookingForClan.css";

function LookingForClan() {
    const navigate = useNavigate()
    const [clanList, setClanList] = useState([]);
    const [loading, setLoading] = useState(true);

    const handleFilterSubmit = (e) => {
      e.preventDefault();
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

if (loading){
  return( 
    <p className="looking-loading">Loading...</p>
  )
}

return (
  <section className="looking-page">
    <div className="looking-header">
      <h2>Find a Clan</h2>
      <p>Browse active listings that match your profile.</p>
    </div>

    <form className="looking-filters" onSubmit={handleFilterSubmit}>
      <label>
        Min Members
        <input type="number"/>
      </label>

      <label>
        Max Members
        <input type="number"/>
      </label>

      <label>
        Min Clan Level
        <input type="number"/>
      </label>

      <div className="looking-filters-actions">
        <button type="submit" className="looking-filter-submit">
          Apply Filters
        </button>
      </div>
    </form>

    <div className="listing-grid">
      {clanList.map((clan) => (
        <button
          key={clan.clan_tag}
          type="button"
          className="listing-card"
          onClick={() => navigate(`/${clan.clan_tag}`)}
        >
          <div className="listing-top">
            <h3>{clan.clan_tag}</h3>
            <span className="listing-location">{clan.clan_info?.location || "Unknown"}</span>
          </div>

          <div className="listing-stats">
            <p><strong>Townhall:</strong> {clan.requirements?.[2] ?? 0}</p>
            <p><strong>League:</strong> {clan.requirements?.[0] ?? 0}</p>
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
