export const defaultBuilderBaseLeagueOptions = [
  { value: 0, label: "No Builder Base Requirement" },
  { value: 1, label: "Wood V" },
  { value: 2, label: "Wood IV" },
  { value: 3, label: "Wood III" },
  { value: 4, label: "Wood II" },
  { value: 5, label: "Wood I" },
  { value: 6, label: "Clay V" },
  { value: 7, label: "Clay IV" },
  { value: 8, label: "Clay III" },
  { value: 9, label: "Clay II" },
  { value: 10, label: "Clay I" },
  { value: 11, label: "Stone V" },
  { value: 12, label: "Stone IV" },
  { value: 13, label: "Stone III" },
  { value: 14, label: "Stone II" },
  { value: 15, label: "Stone I" },
  { value: 16, label: "Copper V" },
  { value: 17, label: "Copper IV" },
  { value: 18, label: "Copper III" },
  { value: 19, label: "Copper II" },
  { value: 20, label: "Copper I" },
  { value: 21, label: "Brass III" },
  { value: 22, label: "Brass II" },
  { value: 23, label: "Brass I" },
  { value: 24, label: "Iron III" },
  { value: 25, label: "Iron II" },
  { value: 26, label: "Iron I" },
  { value: 27, label: "Steel III" },
  { value: 28, label: "Steel II" },
  { value: 29, label: "Steel I" },
  { value: 30, label: "Titanium III" },
  { value: 31, label: "Titanium II" },
  { value: 32, label: "Titanium I" },
  { value: 33, label: "Platinum III" },
  { value: 34, label: "Platinum II" },
  { value: 35, label: "Platinum I" },
  { value: 36, label: "Emerald III" },
  { value: 37, label: "Emerald II" },
  { value: 38, label: "Emerald I" },
  { value: 39, label: "Ruby III" },
  { value: 40, label: "Ruby II" },
  { value: 41, label: "Ruby I" },
  { value: 42, label: "Diamond" }
];

export const builderBaseLeagueOptions = defaultBuilderBaseLeagueOptions;

export function normalizeBuilderBaseLeagueOptions(options) {
  return Array.isArray(options) && options.length > 0
    ? options
    : defaultBuilderBaseLeagueOptions;
}

const builderBaseLeagueLabels = new Map(
  defaultBuilderBaseLeagueOptions.map((option) => [option.value, option.label])
);

export function formatBuilderBaseLeague(value) {
  const leagueId = Number(value);
  return builderBaseLeagueLabels.get(leagueId) || "Unknown";
}
