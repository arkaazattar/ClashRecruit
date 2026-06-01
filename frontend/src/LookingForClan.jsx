import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate, useOutletContext } from "react-router-dom";
import { formatWarFrequency, WAR_FREQUENCY_OPTIONS } from "./utils/warFrequency";
import usePageTitle from "./hooks/usePageTitle"
import LoadingScreen from "./components/LoadingScreen";
import "./LookingForClan.css";

const PAGE_SIZE = 10;

function toNumberOrNull(value) {
    return value === "" || value === null ? null : Number(value);
}

function normalizeClanTag(tagValue) {
    if (!tagValue) {
      return null;
    }

    const normalized = String(tagValue).trim().replace(/^#+/, "");
    if (!normalized) {
      return null;
    }

    return normalized;
}

function buildFilterPayload(filters) {
  return {
    filters: {
      name: filters.name,
      minClanLevel: toNumberOrNull(filters.minClanLevel),
      clanPoints: toNumberOrNull(filters.clanPoints),
      warFrequency: filters.warFrequency || null,
      location: filters.location || null,
      requirements: {
        townhall: toNumberOrNull(filters.minTownhall),
        league: toNumberOrNull(filters.minLeague),
        members: {
          max: toNumberOrNull(filters.maxMembers),
          min: toNumberOrNull(filters.minMembers),
        },
      },
    },
  };
}

function normalizeListingPayload(payload) {
  if (Array.isArray(payload)) {
    return {
      items: payload,
      total: payload.length,
    };
  }

  return {
    items: Array.isArray(payload?.items) ? payload.items : [],
    total: typeof payload?.total === "number" ? payload.total : 0,
  };
}

async function getResponseErrorMessage(response, fallbackMessage) {
  const payload = await response.json().catch(() => ({}));
  return formatApiErrorMessage(payload.error || payload.message || fallbackMessage);
}

function formatApiErrorMessage(message) {
  const trimmed = String(message || "").trim();
  if (!trimmed) {
    return "";
  }

  const fieldMessage = trimmed.match(
    /^([A-Za-z][A-Za-z0-9_.]*)(\s+(?:is|must|should|cannot)\b.*)$/
  );
  if (fieldMessage) {
    return `${formatFieldName(fieldMessage[1])}${fieldMessage[2]}`;
  }

  return trimmed.charAt(0).toUpperCase() + trimmed.slice(1);
}

function formatFieldName(fieldName) {
  const readable = fieldName
    .split(".")
    .map((part) => (
      part
        .replace(/_/g, " ")
        .replace(/([a-z0-9])([A-Z])/g, "$1 $2")
    ))
    .join(" ")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();

  return readable.charAt(0).toUpperCase() + readable.slice(1);
}

function LookingForClan() {
    usePageTitle("Find a Clan | ClashRecruit")
    
    const navigate = useNavigate();
    const { user, sessionStateLoaded } = useOutletContext();
    const hasMountedNameEffect = useRef(false);
    const debounceTimerRef = useRef(null);
    const requestControllerRef = useRef(null);
    const saveErrorTimerRef = useRef(null);
    const [savedClanTags, setSavedClanTags] = useState([]);
    const [saveErrorTag, setSaveErrorTag] = useState("");
    const [saveErrorText, setSaveErrorText] = useState("");
    const [savingClanTag, setSavingClanTag] = useState("");
    const [Locations, setLocations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [loadError, setLoadError] = useState("");
    const [filterError, setFilterError] = useState("");
    const [clans, setClans] = useState([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalResults, setTotalResults] = useState(0);
    const [hasAppliedFilters, setHasAppliedFilters] = useState(false);
    const [appliedFilterPayload, setAppliedFilterPayload] = useState(null);
    const [Filters, setFilters] = useState({
      name: "",
      minTownhall: "",
      minLeague: "",
      minMembers: "",
      maxMembers: "",
      minClanLevel: "",
      warFrequency: "",
      clanPoints: "",
      location: "",
    });
    const filtersRef = useRef(Filters);
    const isLoggedIn = Boolean(user && user !== "Guest");
    const savedTagSet = new Set(savedClanTags);

    useEffect(() => {
      filtersRef.current = Filters;
    }, [Filters]);

    useEffect(() => {
      return () => {
        if (debounceTimerRef.current) {
          clearTimeout(debounceTimerRef.current);
        }
        if (requestControllerRef.current) {
          requestControllerRef.current.abort();
        }
        if (saveErrorTimerRef.current) {
          clearTimeout(saveErrorTimerRef.current);
        }
      };
    }, []);

    const showInlineSaveError = (clanTag, message) => {
      setSaveErrorTag(clanTag);
      setSaveErrorText(message);
      if (saveErrorTimerRef.current) {
        clearTimeout(saveErrorTimerRef.current);
      }
      saveErrorTimerRef.current = setTimeout(() => {
        setSaveErrorTag("");
        setSaveErrorText("");
        saveErrorTimerRef.current = null;
      }, 2400);
    };
    
    const handleFilterChange = (e) => {
      const { name, value } = e.target;
      setFilters((prev) => ({
        ...prev,
        [name]: value,
      }));
    };

    const handleNameChange = (e) => {
      const { value } = e.target;
      setFilters((prev) => ({
        ...prev,
        name: value,
      }));
    };

    async function getLocations(){
      const rsp = await fetch("/clash_locations");
      if (!rsp.ok) {
        throw new Error("Failed to load locations.");
      }
      const locations = await rsp.json()
      setLocations(Array.isArray(locations) ? locations : [])
    }

    async function fetchClanPage(page, filterPayload = null, includeTotal = true) {
      const offset = (page - 1) * PAGE_SIZE;
      const url = `/recruitee?limit=${PAGE_SIZE}&offset=${offset}&includeTotal=${includeTotal ? 1 : 0}`;
      const response = filterPayload
        ? await fetch(url, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(filterPayload),
          })
        : await fetch(url);

      if (!response.ok) {
        throw new Error(
          await getResponseErrorMessage(response, "Failed to load clans.")
        );
      }

      const payload = await response.json();
      const normalized = normalizeListingPayload(payload);
      setClans(normalized.items);
      setCurrentPage(page);
      if (includeTotal) {
        setTotalResults(normalized.total);
      }
    }

    const getSavedClans = useCallback(async () => {
      if (!isLoggedIn) {
        setSavedClanTags([]);
        return;
      }

      const response = await fetch("/saved-clans", {
        credentials: "include",
      });

      if (!response.ok) {
        setSavedClanTags([]);
        return;
      }

      const data = await response.json();
      const tags = Array.isArray(data.saved_clans)
        ? data.saved_clans
            .map((savedClan) => normalizeClanTag(savedClan.clan_tag))
            .filter(Boolean)
        : [];
      setSavedClanTags(tags);
    }, [isLoggedIn]);

    useEffect(() => {
      if (!sessionStateLoaded) {
        return;
      }

      const loadData = async() => {
        setLoading(true);
        setLoadError("");

        try {
          const loadJobs = [fetchClanPage(1, null, true), getLocations()];
          if (isLoggedIn) {
            loadJobs.push(getSavedClans());
          } else {
            setSavedClanTags([]);
          }

          await Promise.all(loadJobs);
        } catch {
          setLoadError("Could not load clan listings right now. Please try again.");
        } finally {
          setLoading(false);
        }
      };
      loadData();
    }, [isLoggedIn, getSavedClans, sessionStateLoaded]);

    const handleFilterSubmit = useCallback(async (e) => {
      if (e) {
        e.preventDefault();
      }

      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }

      if (requestControllerRef.current) {
        requestControllerRef.current.abort();
      }
      const controller = new AbortController();
      requestControllerRef.current = controller;

      setHasAppliedFilters(true);
      setCurrentPage(1);
      setFilterError("");
      const activeFilters = filtersRef.current;
      const filterPayload = buildFilterPayload(activeFilters);
      setAppliedFilterPayload(filterPayload);

      try {
        const offset = 0;
        const response = await fetch(`/recruitee?limit=${PAGE_SIZE}&offset=${offset}&includeTotal=1`, {
          method: "POST",
          signal: controller.signal,
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(filterPayload),
        });
        if (!response.ok) {
          throw new Error(
            await getResponseErrorMessage(
              response,
              "Failed to fetch filtered clans."
            )
          );
        }
        const data = await response.json();
        if (controller.signal.aborted) {
          return;
        }
        const normalized = normalizeListingPayload(data);
        setClans(normalized.items);
        setTotalResults(normalized.total);
      } catch (error) {
        if (error.name !== "AbortError") {
          setFilterError(
            error.message || "Could not apply filters right now. Please try again."
          );
        }
      } finally {
        if (requestControllerRef.current === controller) {
          requestControllerRef.current = null;
        }
      }
    }, []);

    useEffect(() => {
      if (!hasMountedNameEffect.current) {
        hasMountedNameEffect.current = true;
        return;
      }
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
      debounceTimerRef.current = setTimeout(() => {
        handleFilterSubmit();
      }, 250);
    }, [Filters.name, handleFilterSubmit]);

    const handlePageChange = async (nextPage) => {
      if (nextPage < 1 || nextPage > totalPages || nextPage === currentPage) {
        return;
      }

      try {
        if (hasAppliedFilters) {
          await fetchClanPage(nextPage, appliedFilterPayload, false);
        } else {
          await fetchClanPage(nextPage, null, false);
        }
        setFilterError("");
      } catch {
        setFilterError("Could not load that page right now. Please try again.");
      }
    };

    const handleToggleSaveClan = async (clanTag) => {
      if (!isLoggedIn) {
        return;
      }

      const normalizedTag = normalizeClanTag(clanTag);
      if (!normalizedTag) {
        return;
      }

      setSavingClanTag(normalizedTag);
      setSaveErrorTag("");
      setSaveErrorText("");

      const isSaved = savedTagSet.has(normalizedTag);
      if (!isSaved && savedClanTags.length >= 10) {
        setSavingClanTag("");
        showInlineSaveError(normalizedTag, "Can only save 10!");
        return;
      }

      const encodedTag = encodeURIComponent(normalizedTag);

      try {
        if (isSaved) {
          const response = await fetch(`/saved-clans/${encodedTag}`, {
            method: "DELETE",
            credentials: "include",
          });
          const data = await response.json();

          if (!response.ok) {
            showInlineSaveError(normalizedTag, data.message || "Try again");
            return;
          }

          setSavedClanTags((prev) => prev.filter((tag) => tag !== normalizedTag));
          return;
        }

        const response = await fetch(`/saved-clans/${encodedTag}`, {
          method: "POST",
          credentials: "include",
        });
        const data = await response.json();

        if (!response.ok) {
          if (response.status === 409) {
            showInlineSaveError(normalizedTag, "Can only save 10!");
            return;
          }
          showInlineSaveError(normalizedTag, data.message || "Try again");
          return;
        }

        setSavedClanTags((prev) => (prev.includes(normalizedTag) ? prev : [...prev, normalizedTag]));
      } catch {
        showInlineSaveError(normalizedTag, "Network error");
      } finally {
        setSavingClanTag("");
      }
    };
    const totalPages = Math.max(1, Math.ceil(totalResults / PAGE_SIZE));
    const pageNumbers = Array.from({ length: totalPages }, (_, i) => i + 1);

if (!sessionStateLoaded || loading){
  return <LoadingScreen />;
}

return (
  <section className="looking-page">
    <div className="looking-header">
      <h2>Find a Clan</h2>
      <p>Browse active listings that match your profile.</p>
    </div>

    <form className="looking-filters" onSubmit={handleFilterSubmit}>
      <label>
        Name
        <input type="text" name="name" value={Filters.name} onChange={handleNameChange} />
      </label>

      <label>
        Min TH
        <input type="number" name="minTownhall" value={Filters.minTownhall} onChange={handleFilterChange} min={0} />
      </label>

      <label>
        Min League
        <input type="number" name="minLeague" value={Filters.minLeague} onChange={handleFilterChange} min={0} max={34} />
      </label>

      <label>
        Min Members
        <input type="number" name="minMembers" value={Filters.minMembers} onChange={handleFilterChange} min={0} max={50}/>
      </label>

      <label>
        Max Members
        <input type="number" name="maxMembers" value={Filters.maxMembers} onChange={handleFilterChange} min={Filters.minMembers || 0} max={50} />
      </label>

      <label>
        Min Clan Level
        <input type="number" name="minClanLevel" value={Filters.minClanLevel} onChange={handleFilterChange}  />
      </label>

      <label>
        War Frequency
        <select name="warFrequency" value={Filters.warFrequency} onChange={handleFilterChange}>
          <option value="">All</option>
          {WAR_FREQUENCY_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>

      <label>
        Min Clan Points
        <input type="number" name="clanPoints" value={Filters.clanPoints} onChange={handleFilterChange} />
      </label>

      <label>
        Location
        <select name="location" value={Filters.location} onChange={handleFilterChange}>
          <option value="">All Locations</option>
          {Locations.map((location) => (
            <option key={location.id ?? location.name} value={location.name}>
              {location.name}
            </option>
          ))}
        </select>
      </label>

      <div className="looking-filters-actions">
        <button type="submit" className="looking-filter-submit">
          Apply Filters
        </button>
      </div>
    </form>
    {loadError && (
      <p className="looking-request-error" role="status">{loadError}</p>
    )}
    {filterError && (
      <p className="looking-request-error" role="status">{filterError}</p>
    )}



    <div className="listing-grid">
      {clans.map((clan) => {
        const normalizedClanTag = normalizeClanTag(clan.clan_tag);
        const isSaved = normalizedClanTag ? savedTagSet.has(normalizedClanTag) : false;
        const isUpdatingSave = normalizedClanTag ? savingClanTag === normalizedClanTag : false;
        const hasSaveError = normalizedClanTag ? saveErrorTag === normalizedClanTag : false;

        return (
          <article
            key={clan.clan_tag}
            className="listing-card listing-card-clickable"
            onClick={() => navigate(`/looking-for-clan/${clan.clan_tag}`, {clanTag:clan.clan_tag})}
            role="button"
            tabIndex={0}
            onKeyDown={(event) => {
              if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                navigate(`/looking-for-clan/${clan.clan_tag}`, {clanTag:clan.clan_tag});
              }
            }}
          >
            <div className="listing-top">
              <h3>{clan.name || clan.clan_info?.name || clan.clan_tag}</h3>
              <span className="listing-location">{clan.clan_info?.location?.name || "Unknown"}</span>
            </div>

            <div className="listing-stats">
              <p><strong>Townhall:</strong> {clan.requirements?.[2] ?? "?"}</p>
              <p><strong>League:</strong> {clan.requirements?.[0] ?? "?"}</p>
              {clan.clan_info?.warFrequency !== "unknown" &&
                <p><strong>War Freq:</strong> {formatWarFrequency(clan.clan_info?.warFrequency)}</p>
              }
              <p><strong>Clan Points:</strong> {clan.clan_info?.clanPoints ?? 0}</p>
            </div>

            <p className="listing-description">
              {clan.clan_info?.description || "No description provided."}
            </p>

            <div className="listing-card-actions">
              {isLoggedIn && (
                <button
                  type="button"
                  className={`listing-action-btn listing-save-btn${isSaved ? " is-saved" : ""}${hasSaveError ? " has-error" : ""}`}
                  onClick={(event) => {
                    event.stopPropagation();
                    handleToggleSaveClan(clan.clan_tag);
                  }}
                  disabled={isUpdatingSave}
                >
                  {isUpdatingSave ? "Updating..." : (hasSaveError ? saveErrorText : (isSaved ? "Saved" : "Save"))}
                </button>
              )}
            </div>
          </article>
        );
      })}
    </div>
    {pageNumbers.length > 1 && (
      <div className="listing-pagination-wrap">
        {pageNumbers.map((pageNumber) => (
          <button
            key={pageNumber}
            type="button"
            className={`listing-page-btn ${pageNumber === currentPage ? "is-active" : ""}`}
            onClick={() => handlePageChange(pageNumber)}
          >
            {pageNumber}
          </button>
        ))}
      </div>
    )}

    
    </section>
);
}

export default LookingForClan
