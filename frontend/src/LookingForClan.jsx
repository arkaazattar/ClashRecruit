import { useState, useEffect, use } from "react";
import { useNavigate } from "react-router";
import "./LookingForClan.css";

function LookingForClan() {
    const navigate = useNavigate() // use for header when we make it
    const [clanList, setClanList] = useState([]);
    
    useEffect(() => {
    fetch("http://localhost:5000/recruitee", {
      credentials: "include",
    })
      .then((res) => res.json())
      .then((data) => {
        setClanList(data);
      })
  }, []);

return (
  <form>

    {clanList.map((clan, index) => (
        <button type="button" className="box" onClick={ () => navigate(`/${clan.clan_tag}`)}>
            <div key={clan.clan_tag ?? index}>
                <h3>{clan.clan_tag}</h3>
                <p>Townhall Requirement: {clan.requirements[2]}</p>
            </div>
        </button>
    ))}
  </form>
);
}


export default LookingForClan