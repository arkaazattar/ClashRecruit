import './Header.css';
import { Link, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';

function Header() {
    const [user, setUser] = useState(() => sessionStorage.getItem("player_name") || "Guest");
    const [hasActiveListing, setHasActiveListing] = useState(false);
    const [open, setOpen] = useState(false);
    const navigate = useNavigate();
    const isLoggedIn = Boolean(user && user !== "Guest");

    useEffect(() => {
        let isMounted = true;

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

        return () => {
            isMounted = false;
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
                <div className="dropdown">
                    <button className="user-button" onClick={toggleDropdown}>
                        {user} ▾
                    </button>

                    {open && (
                        <div className="dropdown-menu">
                            {isLoggedIn ?(
                                <button onClick={handleLogout} className="dropdown-item">
                                    Logout
                                </button>
                            ): (
                                <button onClick={handleSignin} className="dropdown-item"> 
                                    Login
                                </button>
                            )}

                            {hasActiveListing && (
                                <button onClick={handleListings} className="dropdown-item">
                                    My Listings
                                </button>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </header>
    );
}

export default Header;
