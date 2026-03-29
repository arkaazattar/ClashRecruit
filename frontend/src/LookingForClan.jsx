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
    const [clans, setClans] = useState([]);
    const [offset, setOffset] = useState(0);
    const [hasMore, setHasMore] = useState(true);
    const [isLoadingMore, setIsLoadingMore] = useState(false);
    const [hasAppliedFilters, setHasAppliedFilters] = useState(false);
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
    const isLoggedIn = Boolean(user && user !== "Guest");
    const savedTagSet = new Set(savedClanTags);

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
    }, [Filters.name]);

    async function getLocations(){
      const rsp = await fetch("/clash_locations");
      const locations = await rsp.json()
      setLocations(locations)
    }
    async function getClans(nextOffset = 0, append = false){
      const rsp = await fetch(`/recruitee?limit=${PAGE_SIZE}&offset=${nextOffset}`)
      const data = await rsp.json()
      if (append) {
        setClans((prev) => [...prev, ...data])
      } else {
        setClans(data)
      }
      setOffset(nextOffset + data.length)
      setHasMore(data.length === PAGE_SIZE)
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
        const loadJobs = [getClans(0, false), getLocations()];
        if (isLoggedIn) {
          loadJobs.push(getSavedClans());
        } else {
          setSavedClanTags([]);
        }

        await Promise.all(loadJobs);
        setLoading(false);
      };
      loadData();
    }, [isLoggedIn, getSavedClans, sessionStateLoaded]);

    const handleFilterSubmit = async (e) => {
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

      try {
        const response = await fetch("/recruitee", {
          method: "POST",
          signal: controller.signal,
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            filters: {
              name: Filters.name,
              minClanLevel: toNumberOrNull(Filters.minClanLevel),
              clanPoints: toNumberOrNull(Filters.clanPoints),
              warFrequency: Filters.warFrequency || null,
              location_id: Filters.location || null,
              requirements: {
                townhall: toNumberOrNull(Filters.minTownhall),
                league: toNumberOrNull(Filters.minLeague),
                members: {
                  max: toNumberOrNull(Filters.maxMembers),
                  min: toNumberOrNull(Filters.minMembers),
                },
              },
            },
          }),
        });

        const data = await response.json();
        if (controller.signal.aborted) {
          return;
        }
        setClans(data);
        setHasMore(false);
        setOffset(data.length);
        setIsLoadingMore(false);
      } catch (error) {
        if (error.name !== "AbortError") {
          throw error;
        }
      } finally {
        if (requestControllerRef.current === controller) {
          requestControllerRef.current = null;
        }
      }
    };



    const handleLoadMore = async () => {
      if (!hasMore || isLoadingMore || hasAppliedFilters) {
        return;
      }
      setIsLoadingMore(true);
      await getClans(offset, true);
      setIsLoadingMore(false);
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
            <option key={location.id} value={location.id}>
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
    {!hasAppliedFilters && hasMore && (
      <div className="listing-load-more-wrap">
        <button
          type="button"
          className="listing-load-more"
          onClick={handleLoadMore}
          disabled={isLoadingMore}
        >
          {isLoadingMore ? "Loading..." : "Load More"}
        </button>
      </div>
    )}

    
    </section>
);
}

export default LookingForClan
