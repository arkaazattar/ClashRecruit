import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useOutletContext } from "react-router-dom";
import {
  defaultBuilderBaseLeagueOptions,
  normalizeBuilderBaseLeagueOptions
} from "./utils/builderBaseLeagues";
import { defaultLeagueOptions, normalizeLeagueOptions } from "./utils/recruiter";
import { LISTING_STATUS_CHANGED_EVENT } from "./utils/appEvents";
import usePageTitle from "./hooks/usePageTitle"
import LoadingScreen from "./components/LoadingScreen";
import "./Recruiter.css";

function Recruiter() {
  usePageTitle("Recruit | ClashRecruit")
  const navigate = useNavigate();
  const { recruitStatus, sessionStateLoaded } = useOutletContext();
  const [loading, setLoading] = useState(true);
  const [requiredLeague, setRequiredLeague] = useState("");
  const [requiredBuilderLeague, setRequiredBuilderLeague] = useState("");
  const [requiredTownhall, setRequiredTownhall] = useState("");
  const [builderBaseLeagueOptions, setBuilderBaseLeagueOptions] = useState(
    defaultBuilderBaseLeagueOptions
  );
  const [leagueOptions, setLeagueOptions] = useState(defaultLeagueOptions);
  const [clanDescription, setClanDescription] = useState("");
  const [maxTownhall, setmaxTownhall] = useState(0);
  const [status, setStatus] = useState(null);
  const [updateExpiry, setUpdateExpiry] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [loadError, setLoadError] = useState("");
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [Listing, setListing] = useState("View Listing");
  const deleteNavigateTimerRef = useRef(null);

  useEffect(() => {
    let isMounted = true;

    async function loadRecruiterPage() {
      try {
        if (!sessionStateLoaded) {
          return;
        }

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

        if (!recruiterResponse.ok) {
          const errorData = await recruiterResponse.json().catch(() => ({}));
          setLoadError(
            errorData.message || "Please try again shortly."
          );
          setLoading(false);
          return;
        }

        const recruiterData = await recruiterResponse.json();

        if (!isMounted) {
          return;
        }

        setmaxTownhall(recruiterData.MAXTOWNHALL);
        setBuilderBaseLeagueOptions(
          normalizeBuilderBaseLeagueOptions(
            recruiterData.builderBaseLeagueOptions
          )
        );
        setLeagueOptions(normalizeLeagueOptions(recruiterData.leagueOptions));
        setRequiredLeague(recruiterData.oldRequiredLeague);
        setRequiredBuilderLeague(recruiterData.oldRequiredBuilderLeague);
        setRequiredTownhall(recruiterData.oldRequiredTownhall);
        setClanDescription(recruiterData.clanDescription);
        setStatus(recruiterData.status);
        setListing(recruiterData.status ? "Close Listing" : "View Listing");
        setLoadError("");
        setLoading(false);
      } catch {
        if (isMounted) {
          setLoadError("Please try again shortly.");
          setLoading(false);
        }
      }
    }

    loadRecruiterPage();

    return () => {
      isMounted = false;
      if (deleteNavigateTimerRef.current) {
        clearTimeout(deleteNavigateTimerRef.current);
      }
    };
  }, [navigate, recruitStatus, sessionStateLoaded]);

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
    setListing(recruiterData.status ? "Close Listing" : "View Listing");
    setSuccessMessage(recruiterData.message);

    if (recruiterResponse.ok) {
      window.dispatchEvent(
        new CustomEvent(LISTING_STATUS_CHANGED_EVENT, {
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
    if (response.ok && data.status !== undefined) {
      setStatus(data.status);
    }
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
      window.dispatchEvent(
        new CustomEvent(LISTING_STATUS_CHANGED_EVENT, {
          detail: { hasActiveListing: false }
        })
      );
      deleteNavigateTimerRef.current = setTimeout(() => {
        navigate("/dashboard");
      }, 1200);
    }
  }


  if (loading) {
    return <LoadingScreen />;
  }

  if (loadError) {
    return (
      <section className="recruiter-page recruiter-error-page">
        <div className="recruiter-header">
          <h2>Recruit Players</h2>
          <p>{loadError}</p>
        </div>

        <div className="recruiter-error-links">
          <a href="/recruit">Try again</a>
          <Link
            to="/dashboard"
          >
            Return to dashboard
          </Link>
        </div>
      </section>
    );
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
              <label htmlFor="builderleagues">Required Builder Base League</label>
              <select
                id="builderleagues"
                name="builderleagues"
                value={requiredBuilderLeague}
                onChange={(e) => setRequiredBuilderLeague(Number(e.target.value))}
              >
                {builderBaseLeagueOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
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
            defaultChecked={Boolean(status)}
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
            <Link
              className="recruiter-secondary recruiter-secondary-link"
              to="/dashboard"
            >
              Dashboard
            </Link>
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
                <label htmlFor="builderleagues">Required Builder Base League</label>
                <select
                  id="builderleagues"
                  name="builderleagues"
                  value={requiredBuilderLeague}
                  onChange={(e) =>
                    setRequiredBuilderLeague(Number(e.target.value))
                  }
                >
                  {builderBaseLeagueOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
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
