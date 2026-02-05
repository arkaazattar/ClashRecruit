import { useEffect, useState } from "react";
import { useNavigate } from "react-router";

function Recruiter() {
  const navigate = useNavigate();
  const [requiredLeague, setRequiredLeague] = useState("");
  const [requiredTownhall, setRequiredTownhall] = useState("");
  const [maxTownhall, setmaxTownhall] = useState(0);
  
  
  async function getmaxTownhall(){
    const rsp = await fetch("/recruiter")
    const data = await rsp.json()
   setmaxTownhall(data.MAXTOWNHALL) 
  }
   useEffect(() => {
    getmaxTownhall();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault()
    // this needs to go to the api route for recuriter.

    const recruiterResponse = await fetch("/recruiter", {
        method: "POST",
        headers: {
        "Content-Type": "application/json",
      },
        credentials: "include",
        // placeholder values for now 
        body: JSON.stringify({
          "requiredLeague" : requiredLeague,
          "requiredBuilderhall" : null,
          "requiredTownhall" : requiredTownhall
        })
      }  
    ).then(
    )
    const recruiterData = await recruiterResponse.json()
    // log the rsp for testing
    console.log(recruiterData) 
  }
  
  return (
    
    <div>
    <form onSubmit={handleSubmit}>

      <label htmlFor="leagues">Enter Required League</label>
      <select
        id="leagues"
        name="required_league"
        value={requiredLeague}
        onChange={(e) => setRequiredLeague(Number(e.target.value))}
        required
      >
        <option value={""} disabled>
          -- Select an option --
        </option>

        <option value={0}>Unranked</option>

        <option value={1}>Skeleton 1</option>
        <option value={2}>Skeleton 2</option>
        <option value={3}>Skeleton 3</option>

        <option value={4}>Barbarian 4</option>
        <option value={5}>Barbarian 5</option>
        <option value={6}>Barbarian 6</option>

        <option value={7}>Archer 7</option>
        <option value={8}>Archer 8</option>
        <option value={9}>Archer 9</option>

        <option value={10}>Wizard 10</option>
        <option value={11}>Wizard 11</option>
        <option value={12}>Wizard 12</option>

        <option value={13}>Valkyrie 13</option>
        <option value={14}>Valkyrie 14</option>
        <option value={15}>Valkyrie 15</option>

        <option value={16}>Witch 16</option>
        <option value={17}>Witch 17</option>
        <option value={18}>Witch 18</option>

        <option value={19}>Golem 19</option>
        <option value={20}>Golem 20</option>
        <option value={21}>Golem 21</option>

        <option value={22}>P.E.K.K.A 22</option>
        <option value={23}>P.E.K.K.A 23</option>
        <option value={24}>P.E.K.K.A 24</option>

        <option value={25}>Electro Titan 25</option>
        <option value={26}>Electro Titan 26</option>
        <option value={27}>Electro Titan 27</option>

        <option value={28}>Dragon 28</option>
        <option value={29}>Dragon 29</option>
        <option value={30}>Dragon 30</option>

        <option value={31}>Electro Dragon 31</option>
        <option value={32}>Electro Dragon 32</option>
        <option value={33}>Electro Dragon 33</option>

        <option value={34}>Legend League</option>
      </select>
      <br/>
      <label htmlFor="townhall">Enter Required Townhall</label>
      <select
        id="townhall"
        name="required_townhall"
        value={requiredTownhall}
        onChange={(e) => setRequiredTownhall(Number(e.target.value))}
        required
      >
        <option value={""} disabled>
          -- Select an option --
        </option>
        <option value={0}>No Townhall Requirement</option>
        {Array.from({ length: maxTownhall }, (_, i) => (
          <option key={i} value={i + 1}>
            Townhall Level {i + 1}
          </option>
        ))}
      </select>
      <br/>
      <button>Submit</button>
      </form>
  </div>



)}

export default Recruiter;
