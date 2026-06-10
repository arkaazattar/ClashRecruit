import { useEffect, useRef, useState } from "react";
import { Link, useOutletContext } from "react-router-dom";
import LoadingScreen from "./components/LoadingScreen";
import { formatWarFrequency } from "./utils/warFrequency";
import { leagueOptions } from "./utils/recruiter";
import usePageTitle from "./hooks/usePageTitle"
import "./Landing.css";

const leagueLabelByValue = new Map(leagueOptions.map((option) => [option.value, option.label]));

function getLeagueLabel(leagueValue) {
    const parsedValue = Number(leagueValue);
    const label = leagueLabelByValue.get(parsedValue);
    if (!label) {
        return `League ${leagueValue ?? "?"}`;
    }

    return label === "Legend League" ? label : `${label}+`;
}

function Landing() {
    usePageTitle("ClashRecruit");
    const { user } = useOutletContext();
    const [Loading, setLoading] = useState(true);
    const [numClans, setNumClans] = useState(0);
    const [clans, setClans] = useState([]);
    const [copiedClanTag, setCopiedClanTag] = useState("");
    const copyResetTimerRef = useRef(null);
    const featuredClansRef = useRef(null);

    useEffect(() => {
        async function loadLandingPage(){
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

        loadLandingPage();
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
        <div className="landing">
            <section className="landing-hero">
                <div className="landing-hero-content">
                    <div className="landing-title">
                        ClashRecruit
                    </div>

                    <div className="landing-subtitle">
                            Looking to promote your clan or join a new one? Discover clans and post listings in one place.
                    </div>
                    <span className="clan-count-title">
                        <span className="clan-count-dot" aria-hidden="true" />
                        {numClans} active clan listings
                    </span>

                    
                    <div className="landing-buttons">
                        <Link to="/looking-for-clan" className="landing-btn landing-btn-primary">Search for Clans</Link>
                        <Link to={listClanPath} className="landing-btn landing-btn-secondary">List your clan</Link>
                    </div>
                </div>

                <div className="landing-block">
                    <div className="landing-cards">
                        <h3 className="landing-card-title">Looking for a clan?</h3>
                        <p className="landing-card-copy">
                            Browse active listings
                            <br />
                            by requirements
                            <br />
                            and war style.
                        </p>
                        <Link to="/looking-for-clan" className="landing-card-link">→ Search for clans</Link>
                    </div>
                    <div className="landing-cards">
                        <h3 className="landing-card-title">Recruiting players?</h3>
                        <p className="landing-card-copy">
                            Post your clan and
                            <br />
                            make it easier to
                            <br />
                            discover.
                        </p>
                        <Link to={listClanPath} className="landing-card-link">→ List your clan</Link>
                    </div>
                </div>

                <div className="landing-scroll-cue-wrap">
                    <button
                        type="button"
                        className="landing-scroll-cue"
                        onClick={scrollToFeatured}
                        aria-label="Browse featured clans"
                    >
                        <span className="landing-scroll-cue-icon" aria-hidden="true">↓</span>
                    </button>
                    <p className="landing-scroll-cue-label">Browse featured clans</p>
                </div>
            </section>

            <section className="landing-clans" ref={featuredClansRef}>
                <h2 className="landing-clans-title">Featured Clans</h2>

                <div className="landing-clans-strip">
                    {previewClans.map((clan) => (
                        <article key={clan.clan_tag} className="landing-clan-card">
                            <Link to={`/looking-for-clan/${clan.clan_tag}`} className="landing-clan-card-link">
                                <div className="landing-clan-card-top">
                                    <img
                                        className="landing-clan-badge"
                                        src={clan.clan_info?.badge}
                                        alt={`${clan.name || clan.clan_info?.name || clan.clan_tag} badge`}
                                    />
                                    <div className="landing-clan-heading">
                                        <h3 className="landing-clan-name">{clan.name || clan.clan_info?.name || clan.clan_tag}</h3>
                                        <p className="landing-clan-meta">
                                            <span>{clan.clan_info?.location?.name || "Unknown"}</span>
                                            <span>Level {clan.clan_info?.clan_level ?? "?"}</span>
                                            <span>{clan.clan_info?.member_count ?? "?"}/50</span>
                                        </p>
                                    </div>
                                </div>
                                <div className="landing-clan-chips">
                                    <span className="landing-chip landing-chip-th">TH{clan.requirements?.[2] ?? "?"}+</span>
                                    <span className="landing-chip landing-chip-league">{getLeagueLabel(clan.requirements?.[0])}</span>
                                    {clan.clan_info?.warFrequency && clan.clan_info?.warFrequency !== "unknown" ? (
                                        <span className="landing-chip landing-chip-war">War: {formatWarFrequency(clan.clan_info?.warFrequency)}</span>
                                    ) : null}
                                </div>
                            </Link>

                            <p className="landing-clan-footnote">
                                <span className="landing-copy-wrap">
                                    <button
                                        type="button"
                                        className="landing-copy-btn"
                                        onClick={() => copyClan(clan.clan_tag)}
                                    >
                                        {`#${clan.clan_tag}`}
                                    </button>
                                    <span className={`landing-copy-inline${copiedClanTag === clan.clan_tag ? " is-visible" : ""}`}>
                                        ✓ Copied
                                    </span>
                                </span>
                            </p>
                        </article>
                    ))}
                </div>

                <div className="landing-load-more-wrap">
                    <Link to="/looking-for-clan" className="landing-btn landing-btn-primary">
                        See More
                    </Link>
                </div>
            </section>

        </div>
    )
}

export default Landing;
