import { useState, useEffect, use } from "react";
import { useNavigate } from "react-router";
import "./LookingForClan.css";

function LookingForClan() {
    const navigate = useNavigate()
    const [clanList, setClanList] = useState([]);
    const [loading, setLoading] = useState(true);

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
    <p>Loading...</p>
  )
}

return (
  <form>
    <label> 
      Min Members:
      <input type="number"/>
      
      Max Members:
      <input type="number"/>

      Min Clan Level:
      <input type="number"/>

      Number of Clans:
      <input type="number"/>
    </label>

    
    <br></br>

    {clanList.map((clan) => (
        <button type="button" className="box" onClick={ () => navigate(`/${clan.clan_tag}`)}>
            <div key={clan.clan_tag}>
                <h3>{clan.clan_tag}</h3>
      
                <p>Townhall Requirement: {clan.requirements[2]}</p>
                <p>League Requirement: {clan.requirements[0]}</p>
                <p>Location: {clan.clan_info.location}</p>
                <p>{clan.clan_info.description}</p>
            </div>
        </button>
    ))}
  </form>
);
}


export default LookingForClan