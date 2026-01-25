import { useState } from "react";
import { useNavigate } from "react-router";
import "./Dashboard.css"

function Dashboard() {
  const navigate = useNavigate();

  const Recruiter = () => {
    navigate("/recruit");
  };

  const Recruitee = () => {
    navigate("/looking-for-clan");
  };

  return (
    <div className="Dashboard">
        <form>
            <button className="buttons" onClick={Recruiter}>Recruit!</button>
            <button className="buttons" onClick={Recruitee}>Looking For Clan</button>
        </form>

    </div>
    
  );
}

export default Dashboard;
