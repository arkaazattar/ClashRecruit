import Header from './Header.jsx';
import Footer from './Footer.jsx'
import { Outlet } from 'react-router-dom';
import { useEffect, useState } from 'react';


const Layout = () => {
    const [user, setUser] = useState(() => sessionStorage.getItem("player_name"));
    const [hasActiveListing, setHasActiveListing] = useState(false);
    const [recruitStatus, setRecruitStatus] = useState(false);
    const [townhall, setTownhall] = useState(null);
    const [townhallWeaponLevel, setTownhallWeaponLevel] = useState(0);
    const [dashboardLoaded, setDashboardLoaded] = useState(false);

    useEffect(() => {
        let isMounted = true;

        const loadDashboardState = () => {
            fetch("/dashboard", { credentials: "include" })
                .then((res) => res.json())
                .then((data) => {
                    if (!isMounted) return;

                    const username = data.username;
                    setUser(username);
                    setHasActiveListing(Boolean(data.has_active_listing));
                    setRecruitStatus(Boolean(data.recruit_status));
                    setTownhall(data.townhall);
                    setTownhallWeaponLevel(data.townhallWeaponLevel);
                    setDashboardLoaded(true);

                    sessionStorage.setItem("player_name", username);
                })
                .catch(() => {
                    if (!isMounted) return;
                    setHasActiveListing(false);
                    setRecruitStatus(false);
                    setDashboardLoaded(true);
                });
        };

        const handleListingStatusChanged = (event) => {
            const nextValue = event.detail?.hasActiveListing;

            if (typeof nextValue === "boolean") {
                setHasActiveListing(nextValue);
                return;
            }

            loadDashboardState();
        };

        loadDashboardState();
        window.addEventListener("listing-status-changed", handleListingStatusChanged);

        return () => {
            isMounted = false;
            window.removeEventListener("listing-status-changed", handleListingStatusChanged);
        };
    }, []);

    return (
        <div className="app-shell">
            <Header user={user} hasActiveListing={hasActiveListing}/>
            <main>
                <Outlet context={{ user, townhall, townhallWeaponLevel, recruitStatus, dashboardLoaded }} />
            </main>
            <Footer />
        </div>
    )
}

export default Layout;
