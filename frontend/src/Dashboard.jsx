import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import "./Dashboard.css";
import LoadingScreen from "./components/LoadingScreen";

function Dashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [recruitStatus, setRecruitStatus] = useState(false);
  const [username, setUsername] = useState("Guest");

  useEffect(() => {
    fetch("/dashboard", {
      credentials: "include",
    })
      .then((res) => res.json())
      .then((data) => {
        setRecruitStatus(data.recruit_status);
        setUsername(data.username || "Guest");
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
      <section className="dashboard-panel">
        <p className="dashboard-welcome">Welcome {username}</p>
        <form className="dashboard-form">
          {recruitStatus === true && (
            <button
              type="button"
              className="dashboard-btn dashboard-btn-primary"
              onClick={Recruiter}
            >
              Recruit!
            </button>
          )}

          <button
            type="button"
            className="dashboard-btn dashboard-btn-secondary"
            onClick={Recruitee}
          >
            Looking For Clan
          </button>
        </form>
      </section>
    </div>
  );
}

export default Dashboard;
