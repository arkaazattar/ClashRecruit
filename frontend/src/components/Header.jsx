import './Header.css';
import { Link } from 'react-router-dom';

function Header() {
    const user = sessionStorage.getItem("player_name");
    const handleClick = async (e) =>{
        
    }
    return (
        <div className="header">
            <Link to='/dashboard' className='logo'> ClashRecruit</Link>

            <button>{user}</button>
        
        </div>
    )
}

export default Header;