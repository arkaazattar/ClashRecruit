import './Footer.css';

function Footer() {
    
    return (
        <div className="footer">
            <p className="footer__copyright">© 2026 ClashRecruit</p>
            <label> 
                This material is unofficial and is not endorsed by Supercell.
                For more information see Supercell's Fan Content Policy:{' '}
                <a target="_blank" href="https://supercell.com/en/fan-content-policy/" rel="noopener noreferrer">www.supercell.com/fan-content-policy</a>.
            </label>
        </div>
    )
}

export default Footer; 
