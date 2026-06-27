import { useState, useEffect, useRef, useCallback, useMemo } from "react";
import { useNavigate, useOutletContext, useSearchParams } from "react-router-dom";
import {
  defaultBuilderBaseLeagueOptions,
  normalizeBuilderBaseLeagueOptions
} from "./utils/builderBaseLeagues";
import { defaultLeagueOptions, normalizeLeagueOptions } from "./utils/recruiter";
import { formatWarFrequency, WAR_FREQUENCY_OPTIONS } from "./utils/warFrequency";
import usePageTitle from "./hooks/usePageTitle"
import LoadingScreen from "./components/LoadingScreen";
import "./LookingForClan.css";

const PAGE_SIZE = 10;
const PAGE_WINDOW_SIZE = 10;
const DEFAULT_SOURCE_SORT = "community";
const SOURCE_SORT_OPTIONS = new Set(["community", "discovered"]);

function toNumberOrNull(value) {
    return value === "" || value === null ? null : Number(value);
}

function parsePageParam(value) {
  const pageNumber = Number(value);
  return Number.isInteger(pageNumber) && pageNumber > 0 ? pageNumber : 1;
}

function parseSourceSortParam(value) {
  return SOURCE_SORT_OPTIONS.has(value) ? value : DEFAULT_SOURCE_SORT;
}

function readFilterParam(searchParams, name) {
  return searchParams.get(name)?.trim() || "";
}

function parseFiltersFromSearchParams(searchParams) {
  return {
    name: readFilterParam(searchParams, "name"),
    minTownhall: readFilterParam(searchParams, "minTownhall"),
    minLeague: readFilterParam(searchParams, "minLeague"),
    minMembers: readFilterParam(searchParams, "minMembers"),
    maxMembers: readFilterParam(searchParams, "maxMembers"),
    minClanLevel: readFilterParam(searchParams, "minClanLevel"),
    warFrequency: readFilterParam(searchParams, "warFrequency"),
    clanPoints: readFilterParam(searchParams, "clanPoints"),
    location: readFilterParam(searchParams, "location"),
    sourceSort: parseSourceSortParam(searchParams.get("sourceSort")),
  };
}

function hasActiveFilters(filters) {
  return Object.entries(filters).some(([key, value]) => (
    key !== "sourceSort" && String(value).trim() !== ""
  ));
}

function buildListingSearchParams(filters, page) {
  const nextParams = new URLSearchParams();

  Object.entries(filters).forEach(([key, value]) => {
    if (key === "sourceSort") {
      return;
    }

    const normalizedValue = String(value ?? "").trim();
    if (normalizedValue) {
      nextParams.set(key, normalizedValue);
    }
  });

  if (filters.sourceSort && filters.sourceSort !== DEFAULT_SOURCE_SORT) {
    nextParams.set("sourceSort", filters.sourceSort);
  }

  if (page > 1) {
    nextParams.set("page", String(page));
  }

  return nextParams;
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

function formatBuilderBaseLeague(value, labels) {
  const leagueId = Number(value);
  return labels.get(leagueId) || "Unknown";
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
    const [searchParams, setSearchParams] = useSearchParams();
    const { user, sessionStateLoaded } = useOutletContext();
    const debounceTimerRef = useRef(null);
    const requestControllerRef = useRef(null);
    const saveErrorTimerRef = useRef(null);
    const copyResetTimerRef = useRef(null);
    const hasLoadedListingsRef = useRef(false);
    const [savedClanTags, setSavedClanTags] = useState([]);
    const [saveErrorTag, setSaveErrorTag] = useState("");
    const [saveErrorText, setSaveErrorText] = useState("");
    const [savingClanTag, setSavingClanTag] = useState("");
    const [copiedClanTag, setCopiedClanTag] = useState("");
    const [Locations, setLocations] = useState([]);
    const [builderBaseLeagueOptions, setBuilderBaseLeagueOptions] = useState(
      defaultBuilderBaseLeagueOptions
    );
    const [leagueOptions, setLeagueOptions] = useState(defaultLeagueOptions);
    const [loading, setLoading] = useState(true);
    const [loadError, setLoadError] = useState("");
    const [filterError, setFilterError] = useState("");
    const [clans, setClans] = useState([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalResults, setTotalResults] = useState(0);
    const [Filters, setFilters] = useState(() => parseFiltersFromSearchParams(searchParams));
    const filtersRef = useRef(Filters);
    const searchParamsKey = searchParams.toString();
    const isLoggedIn = Boolean(user && user !== "Guest");
    const savedTagSet = new Set(savedClanTags);
    const builderBaseLeagueLabels = useMemo(
      () => new Map(
        builderBaseLeagueOptions.map((option) => [option.value, option.label])
      ),
      [builderBaseLeagueOptions]
    );

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
        if (copyResetTimerRef.current) {
          clearTimeout(copyResetTimerRef.current);
        }
      };
    }, []);

    const copyClanTag = async (tag, event) => {
      event.stopPropagation();
      const normalizedTag = normalizeClanTag(tag);
      if (!normalizedTag) {
        return;
      }

      try {
        await navigator.clipboard.writeText(normalizedTag);
        setCopiedClanTag(normalizedTag);
        if (copyResetTimerRef.current) {
          clearTimeout(copyResetTimerRef.current);
        }
        copyResetTimerRef.current = setTimeout(() => {
          setCopiedClanTag("");
          copyResetTimerRef.current = null;
        }, 1200);
      } catch {
      }
    };

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

    const updateListingUrl = useCallback((filters, page = 1, options = {}) => {
      const nextParams = buildListingSearchParams(filters, page);
      if (nextParams.toString() === searchParamsKey) {
        return;
      }

      setSearchParams(nextParams, { replace: Boolean(options.replace) });
    }, [searchParamsKey, setSearchParams]);
    
    const handleFilterChange = (e) => {
      const { name, value } = e.target;
      setFilters((prev) => ({
        ...prev,
        [name]: value,
      }));
    };

    const handleNameChange = (e) => {
      const { value } = e.target;
      const nextFilters = {
        ...filtersRef.current,
        name: value,
      };

      setFilters((prev) => ({
        ...prev,
        name: value,
      }));

      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
      debounceTimerRef.current = setTimeout(() => {
        updateListingUrl(nextFilters, 1, { replace: true });
      }, 250);
    };

    const getLocations = useCallback(async () => {
      const rsp = await fetch("/clash_locations");
      if (!rsp.ok) {
        throw new Error("Failed to load locations.");
      }
      const locations = await rsp.json()
      setLocations(Array.isArray(locations) ? locations : [])
    }, []);

    const getMetadata = useCallback(async () => {
      const response = await fetch("/recruitee/metadata");
      if (!response.ok) {
        throw new Error("Failed to load metadata.");
      }

      const metadata = await response.json();
      setBuilderBaseLeagueOptions(
        normalizeBuilderBaseLeagueOptions(metadata.builderBaseLeagueOptions)
      );
      setLeagueOptions(normalizeLeagueOptions(metadata.leagueOptions));
    }, []);

    const fetchClanPage = useCallback(async (page, filters, signal) => {
    const offset = (page - 1) * PAGE_SIZE;
      const sourceSort = parseSourceSortParam(filters.sourceSort);
      const sourceSortParam = encodeURIComponent(sourceSort);
      const url = `/recruitee?limit=${PAGE_SIZE}&offset=${offset}&includeTotal=1&sourceSort=${sourceSortParam}`;
      const filterPayload = buildFilterPayload(filters);
      const response = hasActiveFilters(filters)
        ? await fetch(url, {
            method: "POST",
            signal,
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(filterPayload),
          })
        : await fetch(url, { signal });

      if (!response.ok) {
        throw new Error(
          await getResponseErrorMessage(response, "Failed to load clans.")
        );
      }

      const payload = await response.json();
      const normalized = normalizeListingPayload(payload);
      setClans(normalized.items);
      setCurrentPage(page);
      setTotalResults(normalized.total);
      return normalized;
    }, []);

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
        setLoadError("");

        try {
          const loadJobs = [getLocations(), getMetadata()];
          if (isLoggedIn) {
            loadJobs.push(getSavedClans());
          } else {
            setSavedClanTags([]);
          }

          await Promise.all(loadJobs);
        } catch {
          setLoadError("Could not load clan listings right now. Please try again.");
        }
      };
      loadData();
    }, [isLoggedIn, getLocations, getMetadata, getSavedClans, sessionStateLoaded]);

    useEffect(() => {
      if (!sessionStateLoaded) {
        return;
      }

      const urlFilters = parseFiltersFromSearchParams(searchParams);
      const urlPage = parsePageParam(searchParams.get("page"));
      const normalizedParams = buildListingSearchParams(urlFilters, urlPage);

      setFilters(urlFilters);
      if (normalizedParams.toString() !== searchParamsKey) {
        setSearchParams(normalizedParams, { replace: true });
        return;
      }

      if (requestControllerRef.current) {
        requestControllerRef.current.abort();
      }

      const controller = new AbortController();
      requestControllerRef.current = controller;
      if (!hasLoadedListingsRef.current) {
        setLoading(true);
      }
      setFilterError("");

      fetchClanPage(urlPage, urlFilters, controller.signal)
        .then((normalized) => {
          if (controller.signal.aborted) {
            return;
          }

          const lastPage = Math.max(1, Math.ceil(normalized.total / PAGE_SIZE));
          if (urlPage > lastPage) {
            updateListingUrl(urlFilters, lastPage, { replace: true });
          }
        })
        .catch((error) => {
          if (error.name !== "AbortError") {
            setFilterError(
              error.message || "Could not load clans right now. Please try again."
            );
          }
        })
        .finally(() => {
          if (requestControllerRef.current === controller) {
            requestControllerRef.current = null;
          }
          if (!controller.signal.aborted) {
            hasLoadedListingsRef.current = true;
            setLoading(false);
          }
        });
    }, [fetchClanPage, searchParams, searchParamsKey, sessionStateLoaded, setSearchParams, updateListingUrl]);

    const handleFilterSubmit = useCallback((e) => {
      if (e) {
        e.preventDefault();
      }

      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }

      updateListingUrl(filtersRef.current, 1);
    }, [updateListingUrl]);

    const handlePageChange = (nextPage) => {
      if (nextPage < 1 || nextPage > totalPages || nextPage === currentPage) {
        return;
      }

      updateListingUrl(parseFiltersFromSearchParams(searchParams), nextPage);
      window.scrollTo({ top: 0, behavior: "smooth" });
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
    const pageWindowStart = (
      Math.floor((currentPage - 1) / PAGE_WINDOW_SIZE) * PAGE_WINDOW_SIZE
    ) + 1;
    const pageWindowEnd = Math.min(
      pageWindowStart + PAGE_WINDOW_SIZE - 1,
      totalPages
    );
    const pageNumbers = Array.from(
      { length: pageWindowEnd - pageWindowStart + 1 },
      (_, i) => pageWindowStart + i
    );
    const hasPreviousPageWindow = pageWindowStart > 1;
    const hasNextPageWindow = pageWindowEnd < totalPages;

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
        <select name="minLeague" value={Filters.minLeague} onChange={handleFilterChange}>
          <option value="">Any League</option>
          {leagueOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
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

      <label>
        Sort
        <select name="sourceSort" value={Filters.sourceSort} onChange={handleFilterChange}>
          <option value="community">Community listings first</option>
          <option value="discovered">Discovered clans first</option>
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
              <div className="listing-title-stack">
                <h3>{clan.name || clan.clan_info?.name || clan.clan_tag}</h3>
                {normalizedClanTag && (
                  <button
                    type="button"
                    className="listing-tag-copy-btn"
                    onClick={(event) => copyClanTag(normalizedClanTag, event)}
                    aria-label={`Copy clan tag ${normalizedClanTag}`}
                  >
                    {`#${normalizedClanTag}`}
                    <span className={`listing-tag-copied${copiedClanTag === normalizedClanTag ? " is-visible" : ""}`}>
                      Copied
                    </span>
                  </button>
                )}
              </div>
              <span className="listing-location">{clan.clan_info?.location?.name || "Unknown"}</span>
            </div>

            <div className="listing-stats">
              <p><strong>Townhall:</strong> {clan.requirements?.[2] ?? "?"}</p>
              <p><strong>League:</strong> {clan.requirements?.[0] ?? "?"}</p>
              <p><strong>Builder League:</strong> {formatBuilderBaseLeague(clan.requirements?.[1] ?? 0, builderBaseLeagueLabels)}</p>
              {clan.clan_info?.warFrequency !== "unknown" &&
                <p><strong>War Freq:</strong> {formatWarFrequency(clan.clan_info?.warFrequency)}</p>
              }
              <p><strong>Clan Points:</strong> {clan.clan_info?.clanPoints ?? 0}</p>
            </div>

            {clan.clan_info?.description && <p className="listing-description">
              {clan.clan_info.description}
            </p>}

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
    {totalPages > 1 && (
      <div className="listing-pagination-wrap" aria-label="Clan listing pages">
        {hasPreviousPageWindow && (
          <button
            type="button"
            className="listing-page-btn listing-page-arrow"
            onClick={() => handlePageChange(pageWindowStart - PAGE_WINDOW_SIZE)}
            aria-label="Previous 10 pages"
          >
            &lt;
          </button>
        )}
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
        {hasNextPageWindow && (
          <button
            type="button"
            className="listing-page-btn listing-page-arrow"
            onClick={() => handlePageChange(pageWindowEnd + 1)}
            aria-label="Next 10 pages"
          >
            &gt;
          </button>
        )}
      </div>
    )}

    
    </section>
);
}

export default LookingForClan
