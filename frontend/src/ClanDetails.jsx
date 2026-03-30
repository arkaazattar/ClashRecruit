import "./ClanDetails.css";
import { Link, useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { formatWarFrequency } from "./utils/warFrequency";

function normalizeLocation(rawLocation) {
    if (!rawLocation) return "";
    if (typeof rawLocation === "string") return rawLocation.trim();
    if (typeof rawLocation === "object") return (rawLocation.name || "").trim();
    return "";
}

function ClanDetails() {
    const { clanTag } = useParams();
    const [clanInfo, setClanInfo] = useState(null);
    const [error, setError] = useState("");

    useEffect(() => {
        fetch("/recruitee", {
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
    }, [clanTag]);

    if (error) {
        return <section className="clan-details-page">{error}</section>;
    }

    if (!clanInfo) {
        return <section className="clan-details-page">Loading clan details...</section>;
    }

    const requirements = clanInfo.requirements || [];
    const details = clanInfo.clan_info || {};

    return (
        <section className="clan-details-page">
            <Link className="clan-back-btn" to="/looking-for-clan">
                Back to listings
            </Link>

            <div className="clan-details-card">
                <div className="clan-details-header">
                    <img className="clan-badge" src={details.badge} alt="Clan badge" />
                    <div>
                        <h2>{clanInfo.name || details.name || clanInfo.clan_tag}</h2>
                        <p className="clan-location">{normalizeLocation(details.location) || "Unknown location"}</p>
                    </div>
                </div>

                <p className="clan-description">{details.description || "No clan description provided."}</p>

                <div className="clan-stats-grid">
                    <div><span>Clan Level</span><strong>{details.clan_level ?? 0}</strong></div>
                    <div><span>Members</span><strong>{details.member_count ?? 0}</strong></div>
                    <div><span>Type</span><strong>{details.type || "unknown"}</strong></div>
                    <div><span>War Frequency</span><strong>{formatWarFrequency(details.warFrequency ?? details.war_frequency)}</strong></div>
                    <div><span>Clan Points</span><strong>{details.clanPoints ?? details.clan_points ?? 0}</strong></div>
                    <div><span>Required League</span><strong>{requirements[0] ?? 0}</strong></div>
                    <div><span>Required Builder Trophies</span><strong>{requirements[1] ?? 0}</strong></div>
                    <div><span>Required Town Hall</span><strong>{requirements[2] ?? 0}</strong></div>
                </div>

                <div className="clan-meta">
                    <p><strong>Clan Tag:</strong> {clanInfo.clan_tag}</p>
                    <p><strong>Posted by:</strong> {clanInfo.player_tag}</p>
                    <p><strong>Last updated:</strong> {new Date(clanInfo.last_updated).toLocaleDateString()}</p>
                    <p><strong>Expires:</strong> {new Date(clanInfo.expires).toLocaleDateString()}</p>
                </div>
            </div>
        </section>
    );
}

export default ClanDetails
