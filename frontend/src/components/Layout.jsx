import Header from './Header.jsx';
import { Outlet } from 'react-router-dom';
import { useEffect, useState } from 'react';


const Layout = () => {
    const [user, setUser] = useState(() => sessionStorage.getItem("player_name"));
    const [hasActiveListing, setHasActiveListing] = useState(false);
    const [recruitStatus, setRecruitStatus] = useState(false);
    const [townhall, setTownhall] = useState(null);
    const [townhallWeaponLevel, setTownhallWeaponLevel] = useState(0);

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

                    sessionStorage.setItem("player_name", username);
                })
                .catch(() => {
                    if (!isMounted) return;
                    setHasActiveListing(false);
                    setRecruitStatus(false);
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
        <div>
            <Header user={user} hasActiveListing={hasActiveListing}/>
            <main>
                <Outlet context={{ user, townhall, townhallWeaponLevel,  recruitStatus }} />
            </main>

        </div>
    )
}

export default Layout;
