import Header from './Header.jsx';
import Footer from './Footer.jsx'
import SavedClansModal from './SavedClansModal.jsx';
import { Outlet } from 'react-router-dom';
import { useEffect, useState } from 'react';
import {
    AUTH_STATUS_CHANGED_EVENT,
    LISTING_STATUS_CHANGED_EVENT,
    OPEN_SAVED_CLANS_EVENT
} from '../utils/appEvents';

function normalizeUser(userValue) {
    if (!userValue || userValue === "Guest" || userValue === "null" || userValue === "undefined") {
        return null;
    }

    return userValue;
}

function readStoredUser() {
    return normalizeUser(sessionStorage.getItem("player_name"));
}

function readStoredShellState() {
    const fallback = {
        user: readStoredUser(),
        hasActiveListing: false,
        recruitStatus: false,
        townhall: null,
        townhallWeaponLevel: 0
    };

    try {
        const storedValue = sessionStorage.getItem("session_state");
        if (!storedValue) {
            return fallback;
        }

        const parsed = JSON.parse(storedValue);
        return {
            user: normalizeUser(parsed.username),
            hasActiveListing: Boolean(parsed.has_active_listing),
            recruitStatus: Boolean(parsed.recruit_status),
            townhall: parsed.townhall ?? null,
            townhallWeaponLevel: parsed.townhallWeaponLevel ?? 0
        };
    } catch {
        return fallback;
    }
}

function storeShellState(data) {
    const username = normalizeUser(data.username);

    if (username) {
        sessionStorage.setItem("player_name", username);
        sessionStorage.setItem("session_state", JSON.stringify(data));
    } else {
        sessionStorage.removeItem("player_name");
        sessionStorage.removeItem("session_state");
        sessionStorage.removeItem("dashboard_user_info");
    }
}

const Layout = () => {
    const storedShellState = readStoredShellState();
    const [user, setUser] = useState(() => storedShellState.user);
    const [hasActiveListing, setHasActiveListing] = useState(
        () => storedShellState.hasActiveListing
    );
    const [recruitStatus, setRecruitStatus] = useState(
        () => storedShellState.recruitStatus
    );
    const [townhall, setTownhall] = useState(
        () => storedShellState.townhall
    );
    const [townhallWeaponLevel, setTownhallWeaponLevel] = useState(
        () => storedShellState.townhallWeaponLevel
    );
    const [sessionStateLoaded, setSessionStateLoaded] = useState(false);
    const [savedClansModalOpen, setSavedClansModalOpen] = useState(false);

    useEffect(() => {
        let isMounted = true;

        const loadSessionState = ({ resetBeforeLoad = false } = {}) => {
            if (resetBeforeLoad) {
                setUser(readStoredUser());
                setHasActiveListing(false);
                setRecruitStatus(false);
                setTownhall(null);
                setTownhallWeaponLevel(0);
                setSessionStateLoaded(false);
                sessionStorage.removeItem("session_state");
                sessionStorage.removeItem("dashboard_user_info");
            }

            fetch("/session-state", { credentials: "include" })
                .then((res) => {
                    if (!res.ok) {
                        return null;
                    }

                    return res.json();
                })
                .then((data) => {
                    if (!isMounted) return;
                    if (!data) {
                        setSessionStateLoaded(true);
                        return;
                    }

                    const username = normalizeUser(data.username);
                    setUser(username);
                    setHasActiveListing(Boolean(data.has_active_listing));
                    setRecruitStatus(Boolean(data.recruit_status));
                    setTownhall(data.townhall);
                    setTownhallWeaponLevel(data.townhallWeaponLevel);
                    setSessionStateLoaded(true);
                    storeShellState(data);
                })
                .catch(() => {
                    if (!isMounted) return;
                    setSessionStateLoaded(true);
                });
        };

        const handleListingStatusChanged = (event) => {
            const nextValue = event.detail?.hasActiveListing;

            if (typeof nextValue === "boolean") {
                setHasActiveListing(nextValue);
                return;
            }

            loadSessionState();
        };

        const handleAuthStatusChanged = () => {
            loadSessionState({ resetBeforeLoad: true });
        };

        const handleOpenSavedClans = () => {
            setSavedClansModalOpen(true);
        };

        loadSessionState();
        window.addEventListener(LISTING_STATUS_CHANGED_EVENT, handleListingStatusChanged);
        window.addEventListener(AUTH_STATUS_CHANGED_EVENT, handleAuthStatusChanged);
        window.addEventListener(OPEN_SAVED_CLANS_EVENT, handleOpenSavedClans);

        return () => {
            isMounted = false;
            window.removeEventListener(LISTING_STATUS_CHANGED_EVENT, handleListingStatusChanged);
            window.removeEventListener(AUTH_STATUS_CHANGED_EVENT, handleAuthStatusChanged);
            window.removeEventListener(OPEN_SAVED_CLANS_EVENT, handleOpenSavedClans);
        };
    }, []);

    return (
        <div className="app-shell">
            <Header user={user} hasActiveListing={hasActiveListing}/>
            <main>
                <Outlet context={{ user, townhall, townhallWeaponLevel, recruitStatus, hasActiveListing, sessionStateLoaded }} />
            </main>
            <SavedClansModal
                open={savedClansModalOpen}
                onClose={() => setSavedClansModalOpen(false)}
            />
            <Footer />
        </div>
    )
}

export default Layout;
