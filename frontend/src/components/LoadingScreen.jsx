import "./LoadingScreen.css";

function LoadingScreen({ label = "Loading..." }) {
  return (
    <div className="loading-screen" role="status" aria-live="polite">
      <div className="loading-spinner" aria-hidden="true" />
      <p className="loading-label">{label}</p>
    </div>
  );
}

export default LoadingScreen;
