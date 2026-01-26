import { useState } from "react";
import { useNavigate } from "react-router";
import "./App.css";

function App() {
  const [playerTag, setPlayerTag] = useState("");
  const [apiToken, setApiToken] = useState("");
  const navigate = useNavigate();

  const guesthandleSubmit = (e) => {
    e.preventDefault()
    navigate("/dashboard")
  }
  const handleSubmit = async (e) => {
    e.preventDefault(); 

    // send input to Flask
    const response = await fetch("http://localhost:5000/", {
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
    if (data.message == true){
      navigate("/dashboard")
    }
    else { //testing
      console.log(data.receivedPlayerTag)
    }
  };

  return (
    <div className="App">
      <form onSubmit={handleSubmit}>
        <input
          required
          type="text"
          placeholder="Player Tag"
          value={playerTag}
          onChange={(e) => setPlayerTag(e.target.value)}
        />
        <input
          required
          type="text"
          placeholder="API Token"
          value={apiToken}
          onChange={(e) => setApiToken(e.target.value)}
        />
        <button type="submit">Submit</button>
      </form>

      <form onClick={guesthandleSubmit}>
        <button type="button">Continue as Guest</button>
      </form>
    </div>
  );
}

export default App;
