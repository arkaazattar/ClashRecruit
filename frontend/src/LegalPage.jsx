import { Link } from "react-router-dom";
import usePageTitle from "./hooks/usePageTitle";
import "./StaticPage.css";

const legalPages = {
  privacy: {
    title: "Privacy Policy",
    eyebrow: "Legal",
    intro: "Last Updated: June 6, 2026",
    sections: [
      {
        title: "Introduction",
        body: [
          <>ClashRecruit is a web app that helps Clash of Clans players and clans connect for recruitment.</>,
          <>This Privacy Policy explains how ClashRecruit collects, uses, stores, shares, and protects information when users access or use the service. ClashRecruit is currently operated as a hobby project.</>
        ]
      },
      {
        title: "Data Collection",
        body: [
          <>ClashRecruit does not require user registration or account creation.</>,
          <>ClashRecruit may collect or process Clash of Clans player tags, Clash of Clans API tokens entered by users for account ownership verification, Clash of Clans player and clan information retrieved through the Clash of Clans API, user-generated clan listings and related listing metadata, saved or favorited clans associated with a player tag, creator identifiers tied to clan listings, IP-based rate limiting identifiers, session cookie data used to maintain session state, and listing ownership tokens or similar pseudonymous identifiers used to maintain functionality and prevent abuse.</>,
          <>Clash of Clans API tokens are used only temporarily for verification with the Clash of Clans API and are discarded after verification. ClashRecruit does not store Clash of Clans API tokens.</>,
          <>ClashRecruit does not collect user messaging or private communication data. However, it does process user-generated clan listings and related metadata.</>,
          <>ClashRecruit does not collect government ID, financial data, precise location, health data, children's data, private messages, or other sensitive data.</>
        ]
      },
      {
        title: "Data Usage",
        body: [
          <>ClashRecruit uses collected information to verify that a user owns a Clash of Clans account, retrieve Clash of Clans player and clan information, allow users to create, update, extend, delete, browse, save, and favorite clan listings, display public clan listings to other users, maintain session state, apply rate limits and protect the service from abuse, and respond to privacy-related requests.</>
        ]
      },
      {
        title: "Cookies",
        body: [
          <>ClashRecruit uses cookies for session functionality.</>,
          <>ClashRecruit does not use analytics cookies and does not currently use analytics tools.</>
        ]
      },
      {
        title: "Third Parties",
        body: [
          <>ClashRecruit uses the Clash of Clans API / Supercell to verify Clash of Clans account ownership and retrieve Clash of Clans player and clan information.</>,
          <>Data shared with the Clash of Clans API / Supercell includes the Clash of Clans player tag and Clash of Clans API token entered by the user.</>,
          <>ClashRecruit uses MongoDB Atlas as its database provider to store clan listings, saved clan records, player tags associated with saved clans or listing ownership, and related metadata required for core functionality.</>,
          <>ClashRecruit does not sell user data.</>
        ]
      },
      {
        title: "Data Sharing",
        body: [
          <>Clan listings may be visible to other users of ClashRecruit.</>,
          <>ClashRecruit shares data with the Clash of Clans API / Supercell only as needed to verify account ownership and retrieve Clash of Clans player or clan information.</>,
          <>ClashRecruit uses MongoDB Atlas as its database provider to store clan listings, saved clan records, player tags associated with saved clans or listing ownership, and related metadata required for core functionality.</>,
          <>ClashRecruit does not sell personal data.</>
        ]
      },
      {
        title: "Retention",
        body: [
          <>Clan listings are kept for one week unless the user extends or deletes the listing.</>,
          <>Saved clan records and listing ownership metadata are retained until the user deletes the associated saved clan or listing.</>,
          <>Session cookies are temporary and used for session management.</>,
          <>IP-based rate limiting data is retained temporarily on a rolling short-term basis for security and abuse prevention purposes.</>,
          <>Users do not have ClashRecruit accounts, so account deletion is not available. Users may manually delete their clan listings and saved clans.</>
        ]
      },
      {
        title: "Security",
        body: [
          <>ClashRecruit uses HTTPS for the deployed service.</>,
          <>ClashRecruit uses TLS encryption in transit for all network communications through MongoDB Atlas and supported infrastructure.</>,
          <>Stored database data is encrypted at rest by MongoDB Atlas using provider-managed encryption keys. Customer-managed encryption keys are not enabled.</>,
          <>ClashRecruit does not use end-to-end encryption, client-side encryption, or user-managed encryption keys.</>,
          <>ClashRecruit does not collect passwords, so password hashing is not applicable.</>,
          <>ClashRecruit uses access controls so users can update or delete their own listings.</>
        ]
      },
      {
        title: "User Rights",
        body: [
          <>Users may delete their clan listings and saved clans through ClashRecruit functionality. Users may also contact ClashRecruit to request deletion of any data associated with them where applicable.</>,
          <>Users may correct or update their clan listings through ClashRecruit functionality.</>,
          <>Users may contact ClashRecruit with privacy-related questions.</>
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
            <a
              href="https://discord.gg/9zTNTfVhBD"
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
          <>ClashRecruit is an unofficial fan-made service and is not affiliated with, endorsed by, sponsored by, or specifically approved by Supercell. Clash of Clans and related names, marks, and assets are the property of Supercell. Use of Supercell-related content is intended to comply with Supercell's Fan Content Policy.</>
        ]
      }
    ]
  },
  terms: {
    title: "Terms of Service",
    eyebrow: "Legal",
    intro: "Last Updated: June 6, 2026",
    sections: [
      {
        title: "Overview",
        body: [
          <>ClashRecruit is a web application that helps Clash of Clans players and clans connect for recruitment purposes.</>,
          <>By accessing or using ClashRecruit, you agree to these Terms of Service.</>,
          <>ClashRecruit is an unofficial fan-made project and is not affiliated with, endorsed by, sponsored by, or approved by Supercell.</>
        ]
      },
      {
        title: "Eligibility",
        body: [
          <>ClashRecruit is intended for general use by Clash of Clans players.</>,
          <>You are responsible for ensuring that your use of the service complies with the laws of your jurisdiction.</>,
          <>The service is not specifically directed toward children, but may be used where permitted under applicable law.</>
        ]
      },
      {
        title: "No Accounts",
        body: [
          <>ClashRecruit does not require user accounts or registration.</>,
          <>The service operates using session identifiers, player tags, and listing ownership tokens to manage functionality.</>,
          <>You are responsible for maintaining access to any identifiers associated with your listings.</>
        ]
      },
      {
        title: "User Content (Clan Listings)",
        body: [
          <>Users may create, edit, and delete clan recruitment listings.</>,
          <>By submitting a listing, you grant ClashRecruit permission to display the listing publicly on the platform and store and process the listing as required for service functionality.</>,
          <>You are responsible for the content you submit, including its accuracy and legality.</>,
          <>ClashRecruit does not guarantee the accuracy, availability, or reliability of user-generated content.</>
        ]
      },
      {
        title: "Prohibited Use",
        body: [
          <>You agree not to use the service for unlawful purposes, attempt to disrupt or damage the service, use bots, scrapers, or automated tools without permission, bypass rate limits or security protections, submit misleading, abusive, or harmful content, impersonate others, or misrepresent clans or identities.</>,
          <>ClashRecruit may restrict or remove access for violations of these rules.</>
        ]
      },
      {
        title: "Third-Party Services",
        body: [
          <>ClashRecruit relies on third-party services, including Supercell (Clash of Clans API) and MongoDB Atlas (database hosting).</>,
          <>These services operate under their own terms and policies.</>,
          <>ClashRecruit is not responsible for the availability, performance, or actions of third-party services.</>
        ]
      },
      {
        title: "Service Availability",
        body: [
          <>ClashRecruit is provided on an <strong>"as is"</strong> and <strong>"as available"</strong> basis.</>,
          <>The service may be modified, suspended, or discontinued at any time without notice.</>,
          <>No guarantees are made regarding uptime, reliability, or continued availability.</>
        ]
      },
      {
        title: "Data and Privacy",
        body: [
          <>Your use of ClashRecruit is also governed by the Privacy Policy.</>,
          <>By using the service, you acknowledge that data such as player tags, clan listings, and session identifiers may be collected and processed as described in the Privacy Policy.</>
        ]
      },
      {
        title: "Termination",
        body: [
          <>ClashRecruit reserves the right to restrict or remove access to the service at its discretion, including for violations of these Terms, abuse or misuse of the platform, or security or operational concerns.</>
        ]
      },
      {
        title: "Limitation of Liability",
        body: [
          <>To the maximum extent permitted by law, ClashRecruit is not liable for any damages or losses resulting from use or inability to use the service, reliance on user-generated content, third-party service failures, data loss, or unauthorized access.</>
        ]
      },
      {
        title: "Changes to the Terms",
        body: [
          <>ClashRecruit may update these Terms of Service at any time.</>,
          <>Continued use of the service after changes are posted constitutes acceptance of the updated Terms.</>
        ]
      },
      {
        title: "Contact",
        body: [
          <>
            For questions regarding these Terms, contact ClashRecruit by email at{" "}
            <a href="mailto:clashrecruitsupport@gmail.com">
              clashrecruitsupport@gmail.com
            </a>{" "}
            or through our{" "}
            <a
              href="https://discord.gg/9zTNTfVhBD"
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
        title: "Fan Content Disclaimer",
        body: [
          <>ClashRecruit is a fan-made project.</>,
          <>Clash of Clans and related assets are the property of Supercell. This project is intended to comply with Supercell's Fan Content Policy.</>
        ]
      }
    ]
  }
};

function sectionId(title) {
  return title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
}

function LegalPage({ page }) {
  const content = legalPages[page];

  usePageTitle(`${content.title} | ClashRecruit`);

  return (
    <div className="static-page static-page--legal">
      <section className="static-page__hero">
        <span className="static-page__eyebrow">{content.eyebrow}</span>
        <h1>{content.title}</h1>
        <p>{content.intro}</p>
      </section>

      <section className="static-page__content" aria-label={`${content.title} content`}>
        {content.sections.map((section) => (
          <article className="static-page__section" id={sectionId(section.title)} key={sectionId(section.title)}>
            <h2>{section.title}</h2>
            {section.body.map((paragraph, index) => (
              <p key={`${section.title}-${index}`}>{paragraph}</p>
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

export default LegalPage;
