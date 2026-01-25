import { useEffect, useState } from "react";
import { useNavigate } from "react-router";

function Recruiter() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:5000/dashboard", {
      credentials: "include",
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.recruit_status !== true) {
          navigate("/dashboard", { replace: true });
        } else {
          setLoading(false);
        }
      })
      .catch(() => {
        navigate("/dashboard", { replace: true });
      });
  }, []);

  if (loading) return null;
  return <div>
    Recruiter Page
  </div>;
}

export default Recruiter;
