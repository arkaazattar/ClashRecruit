import './Header.css';
import { Link, useNavigate } from 'react-router-dom';
import { useEffect, useRef, useState } from 'react';

function Header() {
    const [user, setUser] = useState(() => sessionStorage.getItem("player_name") || "Guest");
    const [hasActiveListing, setHasActiveListing] = useState(false);
    const [open, setOpen] = useState(false);
    const navigate = useNavigate();
    const isLoggedIn = Boolean(user && user !== "Guest");
    const dropdownRef = useRef(null);

    useEffect(() => {
        let isMounted = true;
        const loadHeaderState = () => {
            fetch("/dashboard", { credentials: "include" })
                .then((res) => res.json())
                .then((data) => {
                    if (!isMounted) return;
                    const username = data.username || "Guest";
                    setUser(username);
                    setHasActiveListing(Boolean(data.has_active_listing));
                    sessionStorage.setItem("player_name", username);
                })
                .catch(() => {
                    if (!isMounted) return;
                    setHasActiveListing(false);
                });
        };

        const handleListingStatusChanged = (event) => {
            const nextValue = event.detail?.hasActiveListing;

            if (typeof nextValue === "boolean") {
                setHasActiveListing(nextValue);
                return;
            }

            loadHeaderState();
        };

        loadHeaderState();
        window.addEventListener("listing-status-changed", handleListingStatusChanged);

        return () => {
            isMounted = false;
            window.removeEventListener("listing-status-changed", handleListingStatusChanged);
        };
    }, []);

    useEffect(() => {
        const handleDocumentClick = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setOpen(false);
            }
        };

        document.addEventListener("mousedown", handleDocumentClick);

        return () => {
            document.removeEventListener("mousedown", handleDocumentClick);
        };
    }, []);
    
    const toggleDropdown = () => {
        setOpen(prev => !prev);
    };

    const handleLogout = () => {
        sessionStorage.removeItem("player_name");
        setUser("Guest");
        setHasActiveListing(false);
        setOpen(false);
        navigate("/");
    };
    
    const handleSignin = () => {
        setOpen(false);
        navigate("/");
    };
    
    const handleListings = () => {
        setOpen(false);
        navigate("/recruit");
    };

    return (
        <header className="header">
            <Link to='/dashboard' className='logo'>
                ClashRecruit
            </Link>

            <div className="header-right">
                <span className="header-divider" aria-hidden="true">|</span>
                <div className="dropdown" ref={dropdownRef}>
                    <button
                        className="user-button"
                        onClick={toggleDropdown}
                        aria-expanded={open}
                        aria-haspopup="menu"
                    >
                        {user} ▾
                    </button>

                    <div
                        className={`dropdown-menu ${open ? "is-open" : "is-closed"}`}
                        aria-hidden={!open}
                    >
                        {hasActiveListing && (
                            <button onClick={handleListings} className="dropdown-item">
                                My Listings
                            </button>
                        )}
                        {isLoggedIn ?(
                            <button onClick={handleLogout} className="dropdown-item">
                                Logout
                            </button>
                        ): (
                            <button onClick={handleSignin} className="dropdown-item"> 
                                Login
                            </button>
                        )}

                    </div>
                </div>
            </div>
        </header>
    );
}

export default Header;
