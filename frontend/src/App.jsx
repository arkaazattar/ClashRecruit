import { useState } from "react";
import { useNavigate } from "react-router";
import "./App.css";
import usePageTitle from "./hooks/usePageTitle";

function App() {
  usePageTitle("ClashRecruit");
  const [playerTag, setPlayerTag] = useState("");
  const [apiToken, setApiToken] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const guesthandleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const guestResponse = await fetch("/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          playerTag: "Guest",
          apiToken: "None",
        }),
      });
      const guestData = await guestResponse.json();
      if (guestData.message === false) {
        sessionStorage.setItem("player_name", "Guest");
        navigate("/dashboard");
      } else {
        setError("Guest login failed. Please try again.");
      }
    } catch {
      setError("Network error. Please try again.");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const response = await fetch("/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          playerTag: playerTag,
          apiToken: apiToken,
        }),
      });

      const data = await response.json();
      if (data.message === true) {
        sessionStorage.setItem("player_name", data.player_name);
        navigate("/dashboard");
      } else {
        setError(data.receivedPlayerTag || "Login failed.");
      }
    } catch {
      setError("Network error. Please try again.");
    }
  };

  return (
    <div className="App">
      <form onSubmit={handleSubmit} className="login-form">
        <input
          id="playerTag"
          required
          type="text"
          autoComplete="on"
          placeholder="Player Tag"
          pattern="[A-Za-z0-9]+"
          title="Player Tag must contain only letters and numbers."
          value={playerTag}
          onChange={(e) => setPlayerTag(e.target.value)}
        />

        <input
          id="apiToken"
          required
          type="text"
          autoComplete="off"
          placeholder="API Token"
          value={apiToken}
          onChange={(e) => setApiToken(e.target.value)}
        />

        {error && <p className="login-error">{error}</p>}

        <button type="submit" className="primary-btn">Submit</button>
      </form>

      <button onClick={guesthandleSubmit} type="button" className="ghost-btn">
        Continue as Guest
      </button>
    </div>
  );
}

export default App;
