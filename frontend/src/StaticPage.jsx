import { useState } from "react";
import usePageTitle from "./hooks/usePageTitle";
import discordLogo from "./assets/Discord-Symbol-White.png";
import "./StaticPage.css";

const supportEmail = "clashrecruitsupport@gmail.com";
const discordUrl = "https://discord.gg/9zTNTfVhBD";

const pages = {
  contact: {
    eyebrow: "Contact Us",
  }
};

function StaticPage({ page }) {
  const content = pages[page];
  const pageTitle = content.title || content.eyebrow;
  const [copiedEmail, setCopiedEmail] = useState(false);

  usePageTitle(`${pageTitle} | ClashRecruit`);

  const copyEmail = async () => {
    if (navigator.clipboard) {
      await navigator.clipboard.writeText(supportEmail);
    } else {
      const emailField = document.createElement("textarea");
      emailField.value = supportEmail;
      emailField.setAttribute("readonly", "");
      emailField.style.position = "absolute";
      emailField.style.left = "-9999px";
      document.body.appendChild(emailField);
      emailField.select();
      document.execCommand("copy");
      document.body.removeChild(emailField);
    }

    setCopiedEmail(true);
    window.setTimeout(() => setCopiedEmail(false), 700);
  };

  const handleEmailCopy = async (event) => {
    event.stopPropagation();
    await copyEmail();
  };

  return (
    <div className="static-page static-page--contact">
      <section className="static-page__hero">
        <span className="static-page__eyebrow">{content.eyebrow}</span>
        <h1>{content.title}</h1>
        <p>{content.intro}</p>
      </section>

      <section className="static-page__content" aria-label={`${pageTitle} content`}>
        <div className="static-page__contact-grid">
          <div className="static-page__section static-page__contact-card">
            <a
              className="static-page__contact-main"
              target="_blank"
              href={`mailto:${supportEmail}`}
              aria-label={`Email ${supportEmail}`}
            >
              <span className="static-page__contact-icon" aria-hidden="true">@</span>
              <h2>Email</h2>
              <p>
                Send support questions, bug reports, project questions, or clan listing issues by email. Include what
                happened, what page you were on, and any clan or player tag involved.
              </p>
            </a>
            <button
              type="button"
              className="static-page__contact-action"
              onClick={handleEmailCopy}
              aria-label={`Copy support email address ${supportEmail}`}
            >
              <span className={copiedEmail ? "is-copied" : ""}>{supportEmail}</span>
            </button>
          </div>

          <a
            className="static-page__section static-page__contact-card"
            href={discordUrl}
            target="_blank"
            rel="noopener noreferrer"
          >
            <span className="static-page__contact-icon static-page__contact-icon--discord" aria-hidden="true">
              <img src={discordLogo} alt="" />
            </span>
            <h2>Discord</h2>
            <p>
              Join the ClashRecruit Discord for community help, faster discussion, and follow-up questions about
              recruiting, listings, or site feedback.
            </p>
            <span className="static-page__contact-action">
              <span>ClashRecruit Discord</span>
            </span>
          </a>
        </div>
      </section>
    </div>
  );
}

export default StaticPage;
