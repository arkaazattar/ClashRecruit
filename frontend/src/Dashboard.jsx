import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import "./Dashboard.css";

function Dashboard() {
  const navigate = useNavigate();

  const [recruitStatus, setRecruitStatus] = useState(false);

  useEffect(() => {
    fetch("/dashboard", {
      credentials: "include",
    })
      .then((res) => res.json())
      .then((data) => {
        setRecruitStatus(data.recruit_status);
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
