import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import "./Dashboard.css";
import LoadingScreen from "./components/LoadingScreen";

function Dashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [recruitStatus, setRecruitStatus] = useState(false);

  useEffect(() => {
    fetch("/dashboard", {
      credentials: "include",
    })
      .then((res) => res.json())
      .then((data) => {
        setRecruitStatus(data.recruit_status);
        setLoading(false)
      })
  }, []);

  const Recruiter = (e) => {
    e.preventDefault();
    navigate("/recruit");
  };

  const Recruitee = (e) => {
    e.preventDefault();
    navigate("/looking-for-clan");
  };

  if (loading) {
    return <LoadingScreen />;
  }
  return (
    
    <div className="Dashboard">
        <form>
        {recruitStatus === true && (
          <button
          type="button"
          className="buttons"
          onClick={Recruiter}
          >
            Recruit!
          </button>
        )}

        <button
          type="button"
          className="buttons"
          onClick={Recruitee}
          >
          Looking For Clan
        </button>
      </form>
    </div>
  );
}

export default Dashboard;
