import { useState } from "react";

function App() {
  const [playerTag, setPlayerTag] = useState("");
  const [apiToken, setApiToken] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault(); 

    // send input to Flask
    const response = await fetch("http://localhost:5000/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        playerTag: playerTag,
        apiToken: apiToken,
      }),
    });

    const data = await response.json();
    console.log(data); // do something with the response
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Player Tag"
        value={playerTag}
        onChange={(e) => setPlayerTag(e.target.value)}
      />
      <input
        type="text"
        placeholder="API Token"
        value={apiToken}
        onChange={(e) => setApiToken(e.target.value)}
      />
      <button type="submit">Submit</button>
    </form>
  );
}

export default App;
