import './Header.css';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useEffect, useRef, useState } from 'react';
import {
    AUTH_STATUS_CHANGED_EVENT,
    OPEN_SAVED_CLANS_EVENT
} from '../utils/appEvents';
import logo from '../assets/clashrecruit.png';

function Header({ user , hasActiveListing}) {
    const [open, setOpen] = useState(false);
    const navigate = useNavigate();
    const normalizedUser = user === "Guest" ? null : user;
    const isLoggedIn = Boolean(normalizedUser);
    const displayUser = normalizedUser || "Guest";
    const dropdownRef = useRef(null);

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

    const handleLogout = async () => {
        sessionStorage.removeItem("player_name");
        sessionStorage.removeItem("session_state");
        sessionStorage.removeItem("dashboard_user_info");
        setOpen(false);

        await fetch("/logout", {
            method: "POST",
            credentials: "include"
        });

        window.dispatchEvent(new CustomEvent(AUTH_STATUS_CHANGED_EVENT));
        navigate("/");
    };
    
    const handleSignin = () => {
        setOpen(false);
    };

    const handleSavedClans = () => {
        setOpen(false);
        window.dispatchEvent(new CustomEvent(OPEN_SAVED_CLANS_EVENT));
    };

    const getNavLinkClassName = ({ isActive }) => (
        `header-nav-link${isActive ? " is-active" : ""}`
    );
    
    return (
        <header className="header">
            <div className="header-inner">
                <Link to='/' className='logo'>
                    <img src={logo} alt="ClashRecruit logo" className="logo-image" />
                </Link>

                <div className="header-right">
                    <NavLink to="/looking-for-clan" className={getNavLinkClassName}>
                        Find a Clan
                    </NavLink>
                    {isLoggedIn && (
                        <>
                            <NavLink to="/dashboard" className={getNavLinkClassName}>
                                Dashboard
                            </NavLink>
                            <NavLink to="/recruit" className={getNavLinkClassName}>
                                {hasActiveListing ? "View Listing" : "Recruit"}
                            </NavLink>
                        </>
                    )}
                    <span className="header-divider" aria-hidden="true"></span>
                    <div className="dropdown" ref={dropdownRef}>
                        <button
                            className="user-button"
                            onClick={toggleDropdown}
                            aria-expanded={open}
                            aria-haspopup="menu"
                        >
                            <span className="user-button-copy">
                                {isLoggedIn && (
                                    <span className="user-button-label">
                                        Signed in as
                                    </span>
                                )}
                                <span className="user-button-name">{displayUser} ▾</span>
                            </span>
                        </button>

                        <div
                            className={`dropdown-menu ${open ? "is-open" : "is-closed"}`}
                            aria-hidden={!open}
                        >
                            {isLoggedIn ?(
                                <>
                                    <button type="button" onClick={handleSavedClans} className="dropdown-item">
                                        Saved Clans
                                    </button>
                                    <button type="button" onClick={handleLogout} className="dropdown-item">
                                        Logout
                                    </button>
                                </>
                            ): (
                                <Link to="/login" onClick={handleSignin} className="dropdown-item"> 
                                    Login
                                </Link>
                            )}

                        </div>
                    </div>
                </div>
            </div>
        </header>
    );
}

export default Header;
