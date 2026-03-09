import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { useOutletContext } from "react-router-dom";
import "./Recruiter.css";
import LoadingScreen from "./components/LoadingScreen";
import { leagueOptions } from "./utils/recruiter";

function Recruiter() {
  const navigate = useNavigate();
  const { recruitStatus } = useOutletContext();
  const [loading, setLoading] = useState(true);
  const [requiredLeague, setRequiredLeague] = useState("");
  const [requiredBuilderLeague, setRequiredBuilderLeague] = useState("");
  const [requiredTownhall, setRequiredTownhall] = useState("");
  const [clanDescription, setClanDescription] = useState("");
  const [maxTownhall, setmaxTownhall] = useState(0);
  const [status, setStatus] = useState(null);
  const [updateExpiry, setUpdateExpiry] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [Listing, setListing] = useState("View Listing");

  useEffect(() => {
    let isMounted = true;

    async function loadRecruiterPage() {
      try {
        if (!recruitStatus) {
          navigate("/dashboard");
          return;
        }

        const recruiterResponse = await fetch("/recruiter", {
          credentials: "include"
        });

        if (!isMounted) {
          return;
        }

        if (recruiterResponse.status === 403) {
          navigate("/dashboard");
          return;
        }

        const recruiterData = await recruiterResponse.json();

        if (!isMounted) {
          return;
        }

        setmaxTownhall(recruiterData.MAXTOWNHALL);
        setRequiredLeague(recruiterData.oldRequiredLeague);
        setRequiredBuilderLeague(recruiterData.oldRequiredBuilderLeague);
        setRequiredTownhall(recruiterData.oldRequiredTownhall);
        setClanDescription(recruiterData.clanDescription);
        setStatus(recruiterData.status);
        setLoading(false);
      } catch {
        if (isMounted) {
          navigate("/dashboard");
        }
      }
    }

    loadRecruiterPage();

    return () => {
      isMounted = false;
    };
  }, [navigate, recruitStatus]);

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
          <input
            id="recruiter-view-listing-toggle"
            className="recruiter-listing-toggle-input"
            type="checkbox"
            onChange={(e) => {
              setListing(e.target.checked ? "Close Listing" : "View Listing");
              setSuccessMessage("");
            }}
          />
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
            <label
              className="recruiter-primary recruiter-listing-toggle"
              htmlFor="recruiter-view-listing-toggle"
            >
              {Listing}
            </label>
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

          <div
            className={`recruiter-delete-confirm ${showDeleteConfirm ? "is-open" : ""}`}
            aria-hidden={!showDeleteConfirm}
          >
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
        </div>
      </section>
    )
  );
}

export default Recruiter;
