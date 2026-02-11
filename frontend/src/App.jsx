import { useState } from "react";
import { useNavigate } from "react-router";
import "./App.css";

function App() {
  const [playerTag, setPlayerTag] = useState("");
  const [apiToken, setApiToken] = useState("");
  const navigate = useNavigate();

  const guesthandleSubmit = async (e) => {
    e.preventDefault()

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
    if (guestData.message == false){
      sessionStorage.setItem("player_name", "Guest")
      navigate("/dashboard")
    }
  }
  const handleSubmit = async (e) => {
    e.preventDefault(); 

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
    if (data.message == true){
      sessionStorage.setItem("player_name", data.player_name);
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

      <button onClick= {guesthandleSubmit} type="button">Continue as Guest</button>
      
    </div>
  );
}

export default App;
