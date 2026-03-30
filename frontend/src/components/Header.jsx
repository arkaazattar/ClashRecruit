import './Header.css';
import { Link, useNavigate } from 'react-router-dom';
import { useEffect, useRef, useState } from 'react';
import { AUTH_STATUS_CHANGED_EVENT } from '../utils/appEvents';
import logoWithoutText from '../assets/logo_without_text.png';

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
    
    const handleListings = () => {
        setOpen(false);
    };
    
    const handleFindClan = () => {
        setOpen(false);
    }

    return (
        <header className="header">
            <Link to='/' className='logo'>
                <img src={logoWithoutText} alt="ClashRecruit logo" className="logo-image" />
            </Link>

            <div className="header-right">
                {isLoggedIn && (
                    <Link to="/dashboard" className="header-nav-link">
                        Dashboard
                    </Link>
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
                            <span className="user-button-label">
                                {isLoggedIn ? 'Signed in as' : 'Browsing as'}
                            </span>
                            <span className="user-button-name">{displayUser} ▾</span>
                        </span>
                    </button>

                    <div
                        className={`dropdown-menu ${open ? "is-open" : "is-closed"}`}
                        aria-hidden={!open}
                    >
                    <Link to="/looking-for-clan" onClick={handleFindClan} className="dropdown-item">
                            Find a Clan
                    </Link>
                        {hasActiveListing && (
                            <Link to="/recruit" onClick={handleListings} className="dropdown-item">
                                My Listings
                            </Link>
                        )}
                        {isLoggedIn ?(
                            <button onClick={handleLogout} className="dropdown-item">
                                Logout
                            </button>
                        ): (
                            <Link to="/login" onClick={handleSignin} className="dropdown-item"> 
                                Login
                            </Link>
                        )}

                    </div>
                </div>
            </div>
        </header>
    );
}

export default Header;
