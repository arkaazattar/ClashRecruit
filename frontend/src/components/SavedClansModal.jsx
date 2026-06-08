import { Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import './SavedClansModal.css';

function normalizeSavedClanTag(tagValue) {
    if (!tagValue) {
        return null;
    }

    const normalized = String(tagValue).trim().replace(/^#+/, "");
    if (!normalized) {
        return null;
    }

    return normalized;
}

function SavedClansModal({ open, onClose }) {
    const [savedClans, setSavedClans] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [actionError, setActionError] = useState("");
    const [removingSavedClanTag, setRemovingSavedClanTag] = useState("");

    useEffect(() => {
        if (!open) {
            return undefined;
        }

        let isMounted = true;
        setLoading(true);
        setError("");
        setActionError("");

        fetch("/saved-clans", { credentials: "include" })
            .then(async (res) => {
                if (!res.ok) {
                    throw new Error("Saved clans are temporarily unavailable.");
                }

                return res.json();
            })
            .then((data) => {
                if (!isMounted) {
                    return;
                }

                setSavedClans(Array.isArray(data.saved_clans) ? data.saved_clans : []);
            })
            .catch((requestError) => {
                if (!isMounted) {
                    return;
                }

                setSavedClans([]);
                setError(requestError.message || "Saved clans are temporarily unavailable.");
            })
            .finally(() => {
                if (isMounted) {
                    setLoading(false);
                }
            });

        return () => {
            isMounted = false;
        };
    }, [open]);

    useEffect(() => {
        if (!open) {
            return undefined;
        }

        const previousOverflow = document.body.style.overflow;
        const handleEscClose = (event) => {
            if (event.key === "Escape") {
                onClose();
            }
        };

        document.body.style.overflow = "hidden";
        window.addEventListener("keydown", handleEscClose);

        return () => {
            document.body.style.overflow = previousOverflow;
            window.removeEventListener("keydown", handleEscClose);
        };
    }, [open, onClose]);

    const removeSavedClan = async (clanTag) => {
        const normalizedTag = normalizeSavedClanTag(clanTag);
        if (!normalizedTag || removingSavedClanTag) {
            return;
        }

        setRemovingSavedClanTag(normalizedTag);
        setActionError("");

        try {
            const response = await fetch(`/saved-clans/${encodeURIComponent(normalizedTag)}`, {
                method: "DELETE",
                credentials: "include",
            });

            if (!response.ok) {
                throw new Error("Could not remove saved clan.");
            }

            setSavedClans((currentSavedClans) => (
                currentSavedClans.filter((savedClan) => (
                    normalizeSavedClanTag(savedClan.clan_tag) !== normalizedTag
                ))
            ));
        } catch (requestError) {
            setActionError(requestError.message || "Could not remove saved clan.");
        } finally {
            setRemovingSavedClanTag("");
        }
    };

    if (!open) {
        return null;
    }

    return (
        <div className="saved-clans-modal-overlay" onClick={onClose} role="presentation">
            <section
                className="saved-clans-modal"
                role="dialog"
                aria-modal="true"
                aria-label="Saved Clans"
                onClick={(event) => event.stopPropagation()}
            >
                <header className="saved-clans-modal-header">
                    <h2>Saved Clans</h2>
                    <button
                        type="button"
                        className="saved-clans-modal-close"
                        onClick={onClose}
                        aria-label="Close saved clans modal"
                    >
                        <span aria-hidden="true">&times;</span>
                    </button>
                </header>

                <div className="saved-clans-modal-list">
                    {loading && (
                        <p className="saved-clans-empty">Loading saved clans...</p>
                    )}
                    {error && (
                        <p className="saved-clans-empty">{error}</p>
                    )}
                    {actionError && (
                        <p className="saved-clans-action-error">{actionError}</p>
                    )}
                    {!loading && !error && savedClans.length === 0 && (
                        <p className="saved-clans-empty">Save clans from search to keep a shortlist here.</p>
                    )}
                    {!loading && !error && savedClans.map((savedClan, index) => {
                        const savedClanTag = normalizeSavedClanTag(savedClan.clan_tag);
                        const savedClanName = savedClan.name || savedClan.clan_info?.name || savedClanTag || "Saved Clan";
                        const savedClanLocation = savedClan.clan_info?.location?.name;
                        const savedClanMeta = savedClan.listing_available
                            ? (savedClanLocation || "Listing active")
                            : "Listing no longer available";
                        const canOpenListing = Boolean(savedClan.listing_available && savedClanTag);
                        const isRemoving = savedClanTag === removingSavedClanTag;

                        return (
                            <div key={savedClanTag || `${savedClanName}-${index}`} className="saved-clans-item">
                                {canOpenListing ? (
                                    <Link
                                        to={`/looking-for-clan/${savedClanTag}`}
                                        className="saved-clans-item-content saved-clans-item-clickable"
                                        onClick={onClose}
                                    >
                                        <div className="saved-clans-text">
                                            <p className="saved-clans-name">{savedClanName}</p>
                                            <p className="saved-clans-meta">{savedClanMeta}</p>
                                        </div>
                                        <span className="saved-clans-row-icon" aria-hidden="true">&rsaquo;</span>
                                    </Link>
                                ) : (
                                    <div className="saved-clans-item-content">
                                        <div className="saved-clans-text">
                                            <p className="saved-clans-name">{savedClanName}</p>
                                            <p className="saved-clans-meta">{savedClanMeta}</p>
                                        </div>
                                    </div>
                                )}
                                {savedClanTag ? (
                                    <button
                                        type="button"
                                        className="saved-clans-remove-btn"
                                        onClick={() => removeSavedClan(savedClanTag)}
                                        disabled={isRemoving}
                                        aria-label={`Remove ${savedClanName} from saved clans`}
                                        title="Remove saved clan"
                                    >
                                        <span aria-hidden="true">&times;</span>
                                    </button>
                                ) : null}
                            </div>
                        );
                    })}
                </div>
            </section>
        </div>
    );
}

export default SavedClansModal;
