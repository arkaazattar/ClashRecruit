import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import "./Recruiter.css";
import LoadingScreen from "./components/LoadingScreen";

const leagueOptions = [
  { value: 0, label: "Unranked" },
  { value: 1, label: "Skeleton 1" },
  { value: 2, label: "Skeleton 2" },
  { value: 3, label: "Skeleton 3" },
  { value: 4, label: "Barbarian 4" },
  { value: 5, label: "Barbarian 5" },
  { value: 6, label: "Barbarian 6" },
  { value: 7, label: "Archer 7" },
  { value: 8, label: "Archer 8" },
  { value: 9, label: "Archer 9" },
  { value: 10, label: "Wizard 10" },
  { value: 11, label: "Wizard 11" },
  { value: 12, label: "Wizard 12" },
  { value: 13, label: "Valkyrie 13" },
  { value: 14, label: "Valkyrie 14" },
  { value: 15, label: "Valkyrie 15" },
  { value: 16, label: "Witch 16" },
  { value: 17, label: "Witch 17" },
  { value: 18, label: "Witch 18" },
  { value: 19, label: "Golem 19" },
  { value: 20, label: "Golem 20" },
  { value: 21, label: "Golem 21" },
  { value: 22, label: "P.E.K.K.A 22" },
  { value: 23, label: "P.E.K.K.A 23" },
  { value: 24, label: "P.E.K.K.A 24" },
  { value: 25, label: "Electro Titan 25" },
  { value: 26, label: "Electro Titan 26" },
  { value: 27, label: "Electro Titan 27" },
  { value: 28, label: "Dragon 28" },
  { value: 29, label: "Dragon 29" },
  { value: 30, label: "Dragon 30" },
  { value: 31, label: "Electro Dragon 31" },
  { value: 32, label: "Electro Dragon 32" },
  { value: 33, label: "Electro Dragon 33" },
  { value: 34, label: "Legend League" }
];

function Recruiter() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [requiredLeague, setRequiredLeague] = useState("");
  const [requiredBuilderLeague, setRequiredBuilderLeague] = useState("");
  const [requiredTownhall, setRequiredTownhall] = useState("");
  const [clanDescription, setClanDescription] = useState("");
  const [maxTownhall, setmaxTownhall] = useState(0);
  const [status, setStatus] = useState(null);
  const [updateBox, setUpdateBox] = useState(false);
  const [updateExpiry, setUpdateExpiry] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  async function getmaxTownhall() {
    const rsp = await fetch("/recruiter");
    const data = await rsp.json();

    setmaxTownhall(data.MAXTOWNHALL);
    setRequiredLeague(data.oldRequiredLeague);
    setRequiredBuilderLeague(data.oldRequiredBuilderLeague);
    setRequiredTownhall(data.oldRequiredTownhall);
    setClanDescription(data.clanDescription);
    setStatus(data.status);
    setLoading(false);
  }

  useEffect(() => {
    getmaxTownhall();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSuccessMessage("");

    const recruiterResponse = await fetch("/recruiter", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      credentials: "include",
      body: JSON.stringify({
        status: "new",
        requiredLeague: Number(requiredLeague),
        requiredBuilderLeague: Number(requiredBuilderLeague),
        requiredTownhall: Number(requiredTownhall),
        description: clanDescription
      })
    });

    const recruiterData = await recruiterResponse.json();
    setStatus(recruiterData.status);
    setSuccessMessage(recruiterData.message);

    if (recruiterResponse.ok) {
      window.dispatchEvent(
        new CustomEvent("listing-status-changed", {
          detail: { hasActiveListing: true }
        })
      );
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    setSuccessMessage("");

    const response = await fetch("/recruiter", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      credentials: "include",
      body: JSON.stringify({
        status: "update",
        requiredLeague: Number(requiredLeague),
        requiredBuilderLeague: Number(requiredBuilderLeague),
        requiredTownhall: Number(requiredTownhall),
        description: clanDescription,
        expiry: status,
        updateExpiry: updateExpiry
      })
    });    
    const data = await response.json();
    setStatus(data.status);
    setUpdateBox(true);
    setSuccessMessage(data.message ?? "");
  };

  const handleDeleteListing = async (e) => {
    const response = await fetch("/recruiter", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      credentials: "include",
      body: JSON.stringify({
        status: "removeListing"
      })}
    )
    const data = await response.json()
    setSuccessMessage(data.message)
    setShowDeleteConfirm(false);

    if (response.ok) {
      setStatus(null);
      setUpdateBox(false);
      window.dispatchEvent(
        new CustomEvent("listing-status-changed", {
          detail: { hasActiveListing: false }
        })
      );
    }
  }


  if (loading) {
    return <LoadingScreen />;
  }

  return (
    status === null ? (
      <section className="recruiter-page">
        <div className="recruiter-header">
          <h2>Recruit Players</h2>
          <p>Create your clan entry and define requirement thresholds.</p>
        </div>

        <form className="recruiter-card" onSubmit={handleSubmit}>
          <div className="recruiter-fields">
            <div className="recruiter-field">
              <label htmlFor="townhall">Required Townhall</label>
              <select
                id="townhall"
                name="required_townhall"
                value={requiredTownhall}
                onChange={(e) => setRequiredTownhall(Number(e.target.value))}
                required
              >
                <option value={""} disabled>
                  -- Select an option --
                </option>
                <option value={0}>No Townhall Requirement</option>
                {Array.from({ length: maxTownhall }, (_, i) => (
                  <option key={i} value={i + 1}>
                    Townhall Level {i + 1}
                  </option>
                ))}
              </select>
            </div>

            <div className="recruiter-field">
              <label htmlFor="leagues">Required League</label>
              <select
                id="leagues"
                name="required_league"
                value={requiredLeague}
                onChange={(e) => setRequiredLeague(Number(e.target.value))}
                required
              >
                <option value={""} disabled>
                  -- Select an option --
                </option>
                {leagueOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="recruiter-field">
              <label htmlFor="builderleagues">Required Builder Trophies</label>
              <input
                id="builderleagues"
                type="number"
                name="builderleagues"
                value={requiredBuilderLeague}
                onChange={(e) => setRequiredBuilderLeague(Number(e.target.value))}
                max={6700}
                min={0}
                placeholder="Minimum trophies (e.g. 3200)"
              />
            </div>
          </div>

          <div className="recruiter-field">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              name="description"
              rows={4}
              maxLength="250"
              defaultValue={clanDescription}
              onChange={(e) => setClanDescription(e.target.value)}
            />
          </div>

          <div className="recruiter-actions">
            <button className="recruiter-primary">Submit Listing</button>
          </div>

          {successMessage && (
            <p className="recruiter-success-message">{successMessage}</p>
          )}
        </form>
      </section>
    ) : (
      <section className="recruiter-page">
        <div className="recruiter-header">
          <h2>Recruit Players</h2>
          <p>Your clan listing is active.</p>
        </div>

        <div className="recruiter-card recruiter-status-card">
          <p className="recruiter-status-title">Listing already exists.</p>
          <p className="recruiter-status-expiry">
            Set to expire on:{" "}
            {status
              ? new Date(status).toLocaleString(undefined, {
                  dateStyle: "medium",
                  timeStyle: "short"
                })
              : "Unknown"}
          </p>

          <div className="recruiter-actions">
            <button
              className="recruiter-primary"
              type="button"
              onClick={() => {
                setUpdateBox(!updateBox);
                setSuccessMessage("");
              }}
            >
              View Listing
            </button>
            <button
              className="recruiter-secondary"
              onClick={() => navigate("/dashboard")}
            >
              Dashboard
            </button>
            <button
              className="recruiter-danger"
              type="button"
              onClick={() => setShowDeleteConfirm(true)}
            >
              Delete Listing
            </button>
          </div>

          {showDeleteConfirm && (
            <div className="recruiter-delete-confirm">
              <p className="recruiter-delete-confirm-text">
                Are you sure you want to delete this listing?
              </p>
              <div className="recruiter-actions recruiter-delete-actions">
                <button 
                  className="recruiter-danger" 
                  type="button"
                  onClick={handleDeleteListing}
                  >
                  Confirm Delete
                </button>
                <button
                  className="recruiter-secondary"
                  type="button"
                  onClick={() => setShowDeleteConfirm(false)}
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {successMessage && (
            <p className="recruiter-success-message">{successMessage}</p>
          )}

          {updateBox && (
            <form
              className="recruiter-card recruiter-status-card recruiter-update-box"
              onSubmit={handleUpdate}
            >
              <div className="recruiter-fields">
                <div className="recruiter-field">
                  <label htmlFor="townhall">Required Townhall</label>
                  <select
                    id="townhall"
                    name="required_townhall"
                    value={requiredTownhall}
                    onChange={(e) =>
                      setRequiredTownhall(Number(e.target.value))
                    }
                    required
                  >
                    <option value={""} disabled>
                      -- Select an option --
                    </option>
                    <option value={0}>No Townhall Requirement</option>
                    {Array.from({ length: maxTownhall }, (_, i) => (
                      <option key={i} value={i + 1}>
                        Townhall Level {i + 1}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="recruiter-field">
                  <label htmlFor="leagues">Required League</label>
                  <select
                    id="leagues"
                    name="required_league"
                    value={requiredLeague}
                    onChange={(e) => setRequiredLeague(Number(e.target.value))}
                    required
                  >
                    <option value={""} disabled>
                      -- Select an option --
                    </option>
                    {leagueOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="recruiter-field">
                  <label htmlFor="builderleagues">Required Builder Trophies</label>
                  <input
                    id="builderleagues"
                    type="number"
                    name="builderleagues"
                    value={requiredBuilderLeague}
                    onChange={(e) =>
                      setRequiredBuilderLeague(Number(e.target.value))
                    }
                    max={6700}
                    min={0}
                    placeholder="Minimum trophies (e.g. 3200)"
                  />
                </div>

                <div className="recruiter-field recruiter-field-full">
                  <label htmlFor="description">Description</label>
                  <textarea
                    id="description"
                    name="description"
                    rows={4}
                    maxLength="250"
                    defaultValue={clanDescription}
                    onChange={(e) => setClanDescription(e.target.value)}
                  />
                </div>

                <div className="recruiter-update-controls">
                  <div className="recruiter-checkbox">
                    <label>Extend Expiry</label>
                    <input
                      type="checkbox"
                      onChange={(e) => setUpdateExpiry(e.target.checked)}
                    />
                  </div>

                  <div className="recruiter-actions recruiter-update-actions">
                    <button
                      className="recruiter-primary"
                      type="submit"
                    >
                      Update Listing
                    </button>
                  </div>
                </div>
              </div>

              {successMessage && (
                <p className="recruiter-success-message">{successMessage}</p>
              )}
            </form>
          )}
        </div>
      </section>
    )
  );
}

export default Recruiter;
