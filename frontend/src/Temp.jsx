import { useEffect, useRef, useState } from "react";
import { Link, useOutletContext } from "react-router-dom";
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
    const { user } = useOutletContext();
    const [Loading, setLoading] = useState(true);
    const [numClans, setNumClans] = useState(0);
    const [clans, setClans] = useState([]);
    const [copiedClanTag, setCopiedClanTag] = useState("");
    const copyResetTimerRef = useRef(null);
    const featuredClansRef = useRef(null);

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
    const isLoggedIn = Boolean(user && user !== "Guest");
    const listClanPath = isLoggedIn ? "/dashboard" : "/login";

    const scrollToFeatured = () => {
        featuredClansRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    };

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
                            text text text text
                    </div>
                    <span className="clan-count-title">
                        <span className="clan-count-dot" aria-hidden="true" />
                        {numClans} active clan listings
                    </span>

                    
                    <div className="temp-buttons">
                        <Link to="/looking-for-clan" className="temp-btn temp-btn-primary">Search for Clans</Link>
                        <Link to={listClanPath} className="temp-btn temp-btn-secondary">List your clan</Link>
                    </div>
                </div>

                <div className="temp-block">
                    <div className="temp-cards">
                        <h3 className="temp-card-title">Looking for a clan?</h3>
                        <p className="temp-card-copy">
                            Browse active listings
                            <br />
                            by requirements
                            <br />
                            and war style.
                        </p>
                        <Link to="/looking-for-clan" className="temp-card-link">→ Search for clans</Link>
                    </div>
                    <div className="temp-cards">
                        <h3 className="temp-card-title">Recruiting players?</h3>
                        <p className="temp-card-copy">
                            Post your clan and
                            <br />
                            make it easier to
                            <br />
                            discover.
                        </p>
                        <Link to={listClanPath} className="temp-card-link">→ List your clan</Link>
                    </div>
                </div>

                <div className="temp-scroll-cue-wrap">
                    <button
                        type="button"
                        className="temp-scroll-cue"
                        onClick={scrollToFeatured}
                        aria-label="Browse featured clans"
                    >
                        <span className="temp-scroll-cue-icon" aria-hidden="true">↓</span>
                    </button>
                    <p className="temp-scroll-cue-label">Browse featured clans</p>
                </div>
            </section>

            <section className="temp-clans" ref={featuredClansRef}>
                <h2 className="temp-clans-title">Featured Clans</h2>

                <div className="temp-clans-strip">
                    {previewClans.map((clan) => (
                        <article key={clan.clan_tag} className="temp-clan-card">
                            <Link to={`/looking-for-clan/${clan.clan_tag}`} className="temp-clan-card-link">
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
                            </Link>

                            <p className="temp-clan-footnote">
                                <span className="temp-copy-wrap">
                                    <button
                                        type="button"
                                        className="temp-copy-btn"
                                        onClick={() => copyClan(clan.clan_tag)}
                                    >
                                        {`#${clan.clan_tag}`}
                                    </button>
                                    <span className={`temp-copy-inline${copiedClanTag === clan.clan_tag ? " is-visible" : ""}`}>
                                        ✓ Copied
                                    </span>
                                </span>
                            </p>
                        </article>
                    ))}
                </div>

                <div className="temp-load-more-wrap">
                    <Link to="/looking-for-clan" className="temp-btn temp-btn-primary">
                        See More
                    </Link>
                </div>
            </section>

        </div>
    )
}

export default Temp;
