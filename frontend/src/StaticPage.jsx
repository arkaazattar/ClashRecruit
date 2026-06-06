import { Link } from "react-router-dom";
import usePageTitle from "./hooks/usePageTitle";
import "./StaticPage.css";

const pages = {
  about: {
    title: "About ClashRecruit",
    eyebrow: "About",
    intro: "A focused recruiting hub for Clash of Clans players and clan leaders.",
    sections: [
      {
        title: "What this is",
        body: "ClashRecruit helps clans publish recruiting listings and gives players a cleaner way to compare clans by requirements, activity, and war style."
      },
      {
        title: "Who it is for",
        body: "The app is built for leaders who want better visibility and players who want enough context to choose a clan before joining."
      },
      {
        title: "Current status",
        body: "This page is a rough layout placeholder while the final product copy is being written."
      }
    ]
  },
  faq: {
    title: "Frequently Asked Questions",
    eyebrow: "FAQ",
    intro: "Quick answers for common ClashRecruit workflows.",
    sections: [
      {
        title: "How do I list my clan?",
        body: "Sign in with your player tag and API token, then use the dashboard to create or manage a recruiting listing."
      },
      {
        title: "How do I find a clan?",
        body: "Use the clan search page to browse active listings and filter by town hall, league, location, and activity preferences."
      },
      {
        title: "Is ClashRecruit official?",
        body: "No. ClashRecruit is an unofficial fan project and is not endorsed by Supercell."
      }
    ]
  },
  contact: {
    title: "Contact",
    eyebrow: "Contact",
    intro: "A rough contact page for support, project questions, and bug reports.",
    sections: [
      {
        title: "General questions",
        body: "Add the preferred support email, form, or community contact method here."
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
  },
  discord: {
    title: "Discord",
    eyebrow: "Community",
    intro: "A placeholder page for the ClashRecruit Discord community link.",
    sections: [
      {
        title: "Join the community",
        body: "Add the Discord invite, community guidelines, and support channels here once they are ready."
      },
      {
        title: "What to share",
        body: "Players can ask recruiting questions, report listing issues, or share feedback on the app."
      }
    ]
  },
  privacy: {
    title: "Privacy Policy",
    eyebrow: "Legal",
    intro: "Last Updated: June 6, 2026",
    layout: "legal",
    sections: [
      {
        title: "Introduction",
        body: [
          "ClashRecruit is a web app that helps Clash of Clans players and clans connect for recruitment.",
          "This Privacy Policy explains how ClashRecruit collects, uses, stores, shares, and protects information when users access or use the service. ClashRecruit is currently operated as a hobby project."
        ]
      },
      {
        title: "Data Collection",
        body: [
          "ClashRecruit does not require user registration or account creation.",
          "ClashRecruit may collect or process Clash of Clans player tags, Clash of Clans API tokens entered by users for account ownership verification, Clash of Clans player and clan information retrieved through the Clash of Clans API, user-generated clan listings and related listing metadata, saved or favorited clans associated with a player tag, creator identifiers tied to clan listings, IP-based rate limiting identifiers, session cookie data used to maintain session state, and listing ownership tokens or similar pseudonymous identifiers used to maintain functionality and prevent abuse.",
          "Clash of Clans API tokens are used only temporarily for verification with the Clash of Clans API and are discarded after verification. ClashRecruit does not store Clash of Clans API tokens.",
          "ClashRecruit does not collect user messaging or private communication data. However, it does process user-generated clan listings and related metadata.",
          "ClashRecruit does not collect government ID, financial data, precise location, health data, children's data, private messages, or other sensitive data."
        ]
      },
      {
        title: "Data Usage",
        body: [
          "ClashRecruit uses collected information to verify that a user owns a Clash of Clans account, retrieve Clash of Clans player and clan information, allow users to create, update, extend, delete, browse, save, and favorite clan listings, display public clan listings to other users, maintain session state, apply rate limits and protect the service from abuse, and respond to privacy-related requests."
        ]
      },
      {
        title: "Cookies",
        body: [
          "ClashRecruit uses cookies for session functionality.",
          "ClashRecruit does not use analytics cookies and does not currently use analytics tools."
        ]
      },
      {
        title: "Third Parties",
        body: [
          "ClashRecruit uses the Clash of Clans API / Supercell to verify Clash of Clans account ownership and retrieve Clash of Clans player and clan information.",
          "Data shared with the Clash of Clans API / Supercell includes the Clash of Clans player tag and Clash of Clans API token entered by the user.",
          "ClashRecruit uses MongoDB Atlas as its database provider to store clan listings, saved clan records, player tags associated with saved clans or listing ownership, and related metadata required for core functionality.",
          "ClashRecruit does not sell user data."
        ]
      },
      {
        title: "Data Sharing",
        body: [
          "Clan listings may be visible to other users of ClashRecruit.",
          "ClashRecruit shares data with the Clash of Clans API / Supercell only as needed to verify account ownership and retrieve Clash of Clans player or clan information.",
          "ClashRecruit uses MongoDB Atlas as its database provider to store clan listings, saved clan records, player tags associated with saved clans or listing ownership, and related metadata required for core functionality.",
          "ClashRecruit does not sell personal data."
        ]
      },
      {
        title: "Retention",
        body: [
          "Clan listings are kept for one week unless the user extends or deletes the listing.",
          "Saved clan records and listing ownership metadata are retained until the user deletes the associated saved clan or listing.",
          "Session cookies are temporary and used for session management.",
          "IP-based rate limiting data is retained temporarily on a rolling short-term basis for security and abuse prevention purposes.",
          "Users do not have ClashRecruit accounts, so account deletion is not available. Users may manually delete their clan listings and saved clans."
        ]
      },
      {
        title: "Security",
        body: [
          "ClashRecruit uses HTTPS for the deployed service.",
          "ClashRecruit uses TLS encryption in transit for all network communications through MongoDB Atlas and supported infrastructure.",
          "Stored database data is encrypted at rest by MongoDB Atlas using provider-managed encryption keys. Customer-managed encryption keys are not enabled.",
          "ClashRecruit does not use end-to-end encryption, client-side encryption, or user-managed encryption keys.",
          "ClashRecruit does not collect passwords, so password hashing is not applicable.",
          "ClashRecruit uses access controls so users can update or delete their own listings."
        ]
      },
      {
        title: "User Rights",
        body: [
          "Users may delete their clan listings and saved clans through ClashRecruit functionality. Users may also contact ClashRecruit to request deletion of any data associated with them where applicable.",
          "Users may correct or update their clan listings through ClashRecruit functionality.",
          "Users may contact ClashRecruit with privacy-related questions."
        ]
      },
      {
        title: "Contact",
        body: [
          <>
            For privacy-related questions or requests, contact ClashRecruit by email at{" "} 
            <a href="mailto:clashrecruitsupport@gmail.com">
              clashrecruitsupport@gmail.com 
            </a>{" "}
            or through our{" "}
            <a href="https://discord.gg/9zTNTfVhBD"
              target="_blank"
              rel="noopener noreferrer"
            >
              Discord
            </a>
            .
          </>
        ]
      },
      {
        title: "Disclaimer",
        body: [
          "ClashRecruit is an unofficial fan-made service and is not affiliated with, endorsed by, sponsored by, or specifically approved by Supercell. Clash of Clans and related names, marks, and assets are the property of Supercell. Use of Supercell-related content is intended to comply with Supercell's Fan Content Policy."
        ]
      }
    ]
  },
  terms: {
    title: "Terms of Service",
    eyebrow: "Legal",
    intro: "A placeholder layout for the future ClashRecruit terms of service.",
    sections: [
      {
        title: "Use of the service",
        body: "Outline acceptable use, account responsibilities, and expectations for listing content."
      },
      {
        title: "Unofficial fan project",
        body: "Clarify that ClashRecruit is unofficial and not endorsed by Supercell."
      },
      {
        title: "Changes and availability",
        body: "Describe how terms may change and that features may be updated, paused, or removed."
      }
    ]
  }
};

function StaticPage({ page }) {
  const content = pages[page];
  const isLegalLayout = content.layout === "legal";

  usePageTitle(`${content.title} | ClashRecruit`);

  return (
    <div className={`static-page${isLegalLayout ? " static-page--legal" : ""}`}>
      <section className="static-page__hero">
        <span className="static-page__eyebrow">{content.eyebrow}</span>
        <h1>{content.title}</h1>
        <p>{content.intro}</p>
      </section>

      <section className="static-page__content" aria-label={`${content.title} content`}>
        {content.sections.map((section) => (
          <article className="static-page__section" key={section.title}>
            <h2>{section.title}</h2>
            {(Array.isArray(section.body) ? section.body : [section.body]).map((paragraph) => (
              <p key={paragraph}>{paragraph}</p>
            ))}
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
