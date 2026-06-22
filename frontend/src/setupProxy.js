const { createProxyMiddleware } = require("http-proxy-middleware");

const apiProxyTarget = process.env.API_PROXY_TARGET || "http://127.0.0.1:5000";

const apiPathPrefixes = [
  "/clash_locations",
  "/database_count",
  "/logout",
  "/recruitee",
  "/recruiter",
  "/saved-clans",
  "/session-state",
];

const shouldProxy = (pathname, req) => {
  if (pathname === "/" && req.method !== "GET") {
    return true;
  }

  return apiPathPrefixes.some((prefix) => pathname.startsWith(prefix));
};

module.exports = function setupProxy(app) {
  app.use(
    createProxyMiddleware(shouldProxy, {
      target: apiProxyTarget,
      changeOrigin: true,
    }),
  );
};
