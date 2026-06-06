import { Link } from "react-router-dom";
import usePageTitle from "./hooks/usePageTitle";
import "./StaticPage.css";

const pages = {
  contact: {
    title: "Contact",
    eyebrow: "Contact",
    intro: "For support, project questions, bug reports, and clan listing issues.",
    sections: [
      {
        title: "General questions",
        body: "For support or project questions, email clashrecruitsupport@gmail.com or reach out through the ClashRecruit Discord."
      },
      {
        title: "Report a bug",
        body: "Describe what happened, what you expected, whether it happens every time, and include your browser, page URL, screenshots, or any clan or player tag involved."
      },
      {
        title: "Clan listing issues",
        body: "For problems with a clan listing, include the clan tag and a short description of the issue."
      }
    ]
  }
};

function StaticPage({ page }) {
  const content = pages[page];

  usePageTitle(`${content.title} | ClashRecruit`);

  return (
    <div className="static-page">
      <section className="static-page__hero">
        <span className="static-page__eyebrow">{content.eyebrow}</span>
        <h1>{content.title}</h1>
        <p>{content.intro}</p>
      </section>

      <section className="static-page__content" aria-label={`${content.title} content`}>
        {content.sections.map((section) => (
          <article className="static-page__section" key={section.title}>
            <h2>{section.title}</h2>
            <p>{section.body}</p>
          </article>
        ))}
      </section>

      <div className="static-page__actions">
        <Link to="/" className="static-page__button">
          Back to Home
        </Link>
      </div>
    </div>
  );
}

export default StaticPage;
