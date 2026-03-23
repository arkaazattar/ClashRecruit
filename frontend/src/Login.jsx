import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { AUTH_STATUS_CHANGED_EVENT } from "./utils/appEvents";
import usePageTitle from "./hooks/usePageTitle";
import LoadingScreen from "./components/LoadingScreen";
import clashrecruit_api_token_mp4 from "./assets/clashrecruit_api_token.mp4";
import "./Login.css";

function Login() {
  usePageTitle("ClashRecruit");
  const [isVideoReady, setIsVideoReady] = useState(false);
  const [playerTag, setPlayerTag] = useState("");
  const [apiToken, setApiToken] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    let mounted = true;
    const preloadVideo = document.createElement("video");
    preloadVideo.preload = "auto";
    preloadVideo.muted = true;
    preloadVideo.playsInline = true;
    preloadVideo.src = clashrecruit_api_token_mp4;


    const markReady = () => {
      if (mounted) {
        setIsVideoReady(true);
      }
    };

    if (preloadVideo.readyState >= HTMLMediaElement.HAVE_CURRENT_DATA) {
      markReady();
      return () => {
        mounted = false;
      };
    }

    preloadVideo.addEventListener("loadeddata", markReady, { once: true });
    preloadVideo.addEventListener("error", markReady, { once: true });
    preloadVideo.load();

    return () => {
      mounted = false;
      preloadVideo.removeEventListener("loadeddata", markReady);
      preloadVideo.removeEventListener("error", markReady);
      preloadVideo.src = "";
    };
  }, []);

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
        window.dispatchEvent(new CustomEvent(AUTH_STATUS_CHANGED_EVENT));
        navigate("/");
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
        window.dispatchEvent(new CustomEvent(AUTH_STATUS_CHANGED_EVENT));
        navigate("/");
      } else {
        setError(data.receivedPlayerTag || "Login failed.");
      }
    } catch {
      setError("Network error. Please try again.");
    }
  };

  if (!isVideoReady) {
    return <LoadingScreen />;
  }

  return (
    <div className="App">
      <div className="login-container">
        <div className="login-left">
          <h2 className="login-help-title">Having trouble finding your API token?</h2>
          <video
            className="login-help-media"
            autoPlay
            muted
            loop
            playsInline
            preload="metadata"
            aria-label="Animated guide showing where to find your Clash of Clans API token"
          >
            <source src={clashrecruit_api_token_mp4} type="video/mp4" />
          </video>
          <p className="login-help-copy">
            Use this guide to find your API token in Clash of Clans, then paste it into the sign-in form.
          </p>
        </div>
        
        <div className="Divider" />

        <div className="login-right">
          <div className="login-intro">
            <h1 className="login-title">Sign in to ClashRecruit</h1>
            <p className="login-subtitle">
              Enter your player tag and API token to access your dashboard.
            </p>
          </div>

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
            Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
}

export default Login;
