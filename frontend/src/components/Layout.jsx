import Header from './Header.jsx';
import Footer from './Footer.jsx'
import { Outlet } from 'react-router-dom';
import { useEffect, useState } from 'react';
import {
    AUTH_STATUS_CHANGED_EVENT,
    LISTING_STATUS_CHANGED_EVENT
} from '../utils/appEvents';


const Layout = () => {
    const [user, setUser] = useState(() => sessionStorage.getItem("player_name"));
    const [hasActiveListing, setHasActiveListing] = useState(false);
    const [recruitStatus, setRecruitStatus] = useState(false);
    const [townhall, setTownhall] = useState(null);
    const [townhallWeaponLevel, setTownhallWeaponLevel] = useState(0);
    const [sessionStateLoaded, setSessionStateLoaded] = useState(false);

    useEffect(() => {
        let isMounted = true;

        const loadSessionState = ({ resetBeforeLoad = false } = {}) => {
            if (resetBeforeLoad) {
                setUser(sessionStorage.getItem("player_name"));
                setHasActiveListing(false);
                setRecruitStatus(false);
                setTownhall(null);
                setTownhallWeaponLevel(0);
                setSessionStateLoaded(false);
            }

            fetch("/session-state", { credentials: "include" })
                .then((res) => res.json())
                .then((data) => {
                    if (!isMounted) return;

                    const username = data.username;
                    setUser(username);
                    setHasActiveListing(Boolean(data.has_active_listing));
                    setRecruitStatus(Boolean(data.recruit_status));
                    setTownhall(data.townhall);
                    setTownhallWeaponLevel(data.townhallWeaponLevel);
                    setSessionStateLoaded(true);

                    sessionStorage.setItem("player_name", username);
                })
                .catch(() => {
                    if (!isMounted) return;
                    setHasActiveListing(false);
                    setRecruitStatus(false);
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

        loadSessionState();
        window.addEventListener(LISTING_STATUS_CHANGED_EVENT, handleListingStatusChanged);
        window.addEventListener(AUTH_STATUS_CHANGED_EVENT, handleAuthStatusChanged);

        return () => {
            isMounted = false;
            window.removeEventListener(LISTING_STATUS_CHANGED_EVENT, handleListingStatusChanged);
            window.removeEventListener(AUTH_STATUS_CHANGED_EVENT, handleAuthStatusChanged);
        };
    }, []);

    return (
        <div className="app-shell">
            <Header user={user} hasActiveListing={hasActiveListing}/>
            <main>
                <Outlet context={{ user, townhall, townhallWeaponLevel, recruitStatus, sessionStateLoaded }} />
            </main>
            <Footer />
        </div>
    )
}

export default Layout;
