import './Header.css';
import { Link } from 'react-router-dom';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Header() {
    const user = sessionStorage.getItem("player_name");
    const isLoggedIn = Boolean(user && user !== "Guest");
    const [open, setOpen] = useState(false);
    const navigate = useNavigate();
    
    const toggleDropdown = () => {
        setOpen(prev => !prev);
    };

    const handleLogout = (e) => {
        sessionStorage.removeItem("player_name");
        navigate("/");
    }
    
    const handleSignin = (e) => {
        navigate("/");
    }
    
    const handleListings = (e) => {

    }

    return (
        <div className="header">
            <Link to='/dashboard' className='logo'>
                ClashRecruit
            </Link>

            <div className="dropdown">
                <button onClick={toggleDropdown}>
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

                        <button onClick={handleListings} className="dropdown-item">
                            My Listings
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}

export default Header;
