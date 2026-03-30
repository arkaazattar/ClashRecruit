import "./ClanDetails.css";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { useEffect, useState } from "react";

function normalizeLocation(rawLocation) {
    if (!rawLocation) return "";
    if (typeof rawLocation === "string") return rawLocation.trim();
    if (typeof rawLocation === "object") return (rawLocation.name || "").trim();
    return "";
}

function getDetails(clanInfo) {
    return clanInfo.clan_info || {
        badge: clanInfo.badgeUrls?.large || clanInfo.badgeUrls?.medium || clanInfo.badgeUrls?.small || "",
        name: clanInfo.name,
        location: clanInfo.location,
        description: clanInfo.description,
        clan_level: clanInfo.clanLevel,
        member_count: clanInfo.members,
        type: clanInfo.type,
        warFrequency: clanInfo.warFrequency,
        clanPoints: clanInfo.clanPoints,
    };
}

function ClanDetails() {
    const { clanTag } = useParams();
    const navigate = useNavigate();
    const location = useLocation();
    const [clanInfo, setClanInfo] = useState(null);
    const [error, setError] = useState("");
    const stateClanInfo = location.state?.clanInfo;
    const isRandomMode = location.state?.isRandomMode;
    const isImportedMode = location.state?.isImportedMode;

    useEffect(() => {
        if (stateClanInfo) {
            setClanInfo(stateClanInfo);
            setError("");
            return;
        }

        const endpoint = isImportedMode ? "/imported_clans" : "/recruitee";

        fetch(endpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            credentials: "include",
            body: JSON.stringify({
                clanTag: clanTag,
            }),
        })
            .then((res) => {
                if (!res.ok) {
                    throw new Error("Failed to load clan details.");
                }
                return res.json();
            })
            .then((data) => {
                setClanInfo(data);
                setError("");
            })
            .catch((err) => {
                setError(err.message);
            });
    }, [clanTag, stateClanInfo, isImportedMode]);

    if (error) {
        return <section className="clan-details-page">{error}</section>;
    }

    if (!clanInfo) {
        return <section className="clan-details-page">Loading clan details...</section>;
    }

    const requirements = clanInfo.requirements || [];
    const details = getDetails(clanInfo);
    const clanIdentifier = clanInfo.clan_tag || clanInfo.tag || clanTag;

    return (
        <section className="clan-details-page">
            <button className="clan-back-btn" type="button" onClick={() => navigate("/looking-for-clan/")}>
                Back to listings
            </button>

            <div className="clan-details-card">
                <div className="clan-details-header">
                    {details.badge && <img className="clan-badge" src={details.badge} alt="Clan badge" />}
                    <div>
                        <h2>{clanInfo.name || details.name || clanIdentifier}</h2>
                        <p className="clan-location">{normalizeLocation(details.location) || "Unknown location"}</p>
                    </div>
                </div>

                <p className="clan-description">{details.description || "No clan description provided."}</p>

                <div className="clan-stats-grid">
                    <div><span>Clan Level</span><strong>{details.clan_level ?? 0}</strong></div>
                    <div><span>Members</span><strong>{details.member_count ?? 0}</strong></div>
                    <div><span>Type</span><strong>{details.type || "unknown"}</strong></div>
                    <div><span>War Frequency</span><strong>{details.warFrequency ?? details.war_frequency ?? "unknown"}</strong></div>
                    <div><span>Clan Points</span><strong>{details.clanPoints ?? details.clan_points ?? 0}</strong></div>
                    <div><span>Required League</span><strong>{requirements[0] ?? 0}</strong></div>
                    <div><span>Required Builder Trophies</span><strong>{requirements[1] ?? 0}</strong></div>
                    <div><span>Required Town Hall</span><strong>{requirements[2] ?? 0}</strong></div>
                </div>

                <div className="clan-meta">
                    <p><strong>Clan Tag:</strong> {clanIdentifier}</p>
                    {!isRandomMode && clanInfo.player_tag && <p><strong>Posted by:</strong> {clanInfo.player_tag}</p>}
                    {!isRandomMode && clanInfo.last_updated && <p><strong>Last updated:</strong> {new Date(clanInfo.last_updated).toLocaleDateString()}</p>}
                    {!isRandomMode && clanInfo.expires && <p><strong>Expires:</strong> {new Date(clanInfo.expires).toLocaleDateString()}</p>}
                    {clanInfo.source === "clash_api_import" && <p><strong>Source:</strong> Imported Clash of Clans API</p>}
                    {isRandomMode && clanInfo.source !== "clash_api_import" && <p><strong>Source:</strong> Clash of Clans API</p>}
                </div>
            </div>
        </section>
    );
}

export default ClanDetails
