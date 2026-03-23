import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router";
import LoadingScreen from "./components/LoadingScreen";
import { formatWarFrequency } from "./utils/warFrequency";
import { leagueOptions } from "./utils/recruiter";
import "./Temp.css";

const leagueLabelByValue = new Map(leagueOptions.map((option) => [option.value, option.label]));

function getLeagueLabel(leagueValue) {
    const parsedValue = Number(leagueValue);
    const label = leagueLabelByValue.get(parsedValue);
    if (!label) {
        return `League ${leagueValue ?? "?"}`;
    }

    return label === "Legend League" ? label : `${label}+`;
}

function Temp() {
    const [Loading, setLoading] = useState(true);
    const [numClans, setNumClans] = useState(0);
    const [clans, setClans] = useState([]);
    const [copiedClanTag, setCopiedClanTag] = useState("");
    const copyResetTimerRef = useRef(null);
    const navigate = useNavigate();   

    useEffect(() => {
        async function loadTempPage(){
            try {
                const countResponse = await fetch("/database_count");
                const countData = await countResponse.json();
                setNumClans(countData.clan_count);
                
                const clanResponse = await fetch("/recruitee");
                const clanData = await clanResponse.json();
                setClans(clanData)
            } finally {
                setLoading(false);
            }
        }

        loadTempPage();
    }, [])

    const Search = () => {
        navigate("/looking-for-clan")
    }

    const ListClan = () => {
        navigate("/login")
    }

    const copyClan = async (clanTag) => {
        try {
            await navigator.clipboard.writeText(clanTag);
            setCopiedClanTag(clanTag);
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

    useEffect(() => {
        return () => {
            if (copyResetTimerRef.current) {
                clearTimeout(copyResetTimerRef.current);
            }
        };
    }, []);

    const previewClans = clans.slice(0, 4);

    if (Loading) {
        return <LoadingScreen />
    }

    return (
        <div className="temp">
            <section className="temp-hero">
                <div className="temp-hero-content">
                    <div className="temp-title">
                        ClashRecruit
                    </div>

                    <div className="temp-subtitle">
                        Find active clan listings fast, compare entry requirements, and move straight into your next home.
                    </div>
                    <span className="clan-count-title">
                        <span className="clan-count-dot" aria-hidden="true" />
                        {numClans} active clan listings
                    </span>

                    <div className="temp-buttons">
                        <button type="button" className="temp-btn temp-btn-primary" onClick={Search}>Search for Clans</button>
                        <button type="button" className="temp-btn temp-btn-secondary" onClick={ListClan}>List your clan</button>
                    </div>
                </div>
            </section>

            <section className="temp-clans">
                <h2 className="temp-clans-title">Featured Clans</h2>

                <div className="temp-clans-strip">
                    {previewClans.map((clan) => (
                        <article key={clan.clan_tag} className="temp-clan-card">
                            <div className="temp-clan-card-top">
                                <img
                                    className="temp-clan-badge"
                                    src={clan.clan_info?.badge}
                                    alt={`${clan.name || clan.clan_info?.name || clan.clan_tag} badge`}
                                />
                                <div className="temp-clan-heading">
                                    <h3 className="temp-clan-name">{clan.name || clan.clan_info?.name || clan.clan_tag}</h3>
                                    <p className="temp-clan-meta">
                                        <span>{clan.clan_info?.location?.name || "Unknown"}</span>
                                        <span>Level {clan.clan_info?.clan_level ?? "?"}</span>
                                        <span>{clan.clan_info?.member_count ?? "?"}/50</span>
                                    </p>
                                </div>
                            </div>

                            <div className="temp-clan-chips">
                                <span className="temp-chip temp-chip-th">TH{clan.requirements?.[2] ?? "?"}+</span>
                                <span className="temp-chip temp-chip-league">{getLeagueLabel(clan.requirements?.[0])}</span>
                                {clan.clan_info?.warFrequency && clan.clan_info?.warFrequency !== "unknown" ? (
                                    <span className="temp-chip temp-chip-war">War: {formatWarFrequency(clan.clan_info?.warFrequency)}</span>
                                ) : null}
                            </div>

                            <p className="temp-clan-footnote">
                                <button
                                    type="button"
                                    className={`temp-copy-btn${copiedClanTag === clan.clan_tag ? " is-copied" : ""}`}
                                    onClick={() => copyClan(clan.clan_tag)}
                                >
                                    {copiedClanTag === clan.clan_tag ? "Copied!" : `#${clan.clan_tag}`}
                                </button>
                            </p>
                        </article>
                    ))}
                </div>

                <div className="temp-load-more-wrap">
                    <button type="button" className="temp-btn temp-btn-primary" onClick={Search}>
                        See More
                    </button>
                </div>
            </section>

        </div>
    )
}

export default Temp;
