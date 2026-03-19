import './Header.css';
import { Link, useNavigate } from 'react-router-dom';
import { useEffect, useRef, useState } from 'react';

function Header({ user , hasActiveListing}) {
    const [open, setOpen] = useState(false);
    const navigate = useNavigate();
    const isLoggedIn = Boolean(user && user !== "Guest");
    const displayUser = user || "Guest";
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

    const handleLogout = () => {
        sessionStorage.removeItem("player_name");
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
    
    const handleFindClan = () => {
        setOpen(false);
        navigate("/looking-for-clan")
    }

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
                    <button onClick={handleFindClan} className="dropdown-item">
                            Find a Clan
                    </button>
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
