export const defaultLeagueOptions = [
  { value: 0, label: "Unranked" },
  { value: 1, label: "Skeleton 1" },
  { value: 2, label: "Skeleton 2" },
  { value: 3, label: "Skeleton 3" },
  { value: 4, label: "Barbarian 4" },
  { value: 5, label: "Barbarian 5" },
  { value: 6, label: "Barbarian 6" },
  { value: 7, label: "Archer 7" },
  { value: 8, label: "Archer 8" },
  { value: 9, label: "Archer 9" },
  { value: 10, label: "Wizard 10" },
  { value: 11, label: "Wizard 11" },
  { value: 12, label: "Wizard 12" },
  { value: 13, label: "Valkyrie 13" },
  { value: 14, label: "Valkyrie 14" },
  { value: 15, label: "Valkyrie 15" },
  { value: 16, label: "Witch 16" },
  { value: 17, label: "Witch 17" },
  { value: 18, label: "Witch 18" },
  { value: 19, label: "Golem 19" },
  { value: 20, label: "Golem 20" },
  { value: 21, label: "Golem 21" },
  { value: 22, label: "P.E.K.K.A 22" },
  { value: 23, label: "P.E.K.K.A 23" },
  { value: 24, label: "P.E.K.K.A 24" },
  { value: 25, label: "Electro Titan 25" },
  { value: 26, label: "Electro Titan 26" },
  { value: 27, label: "Electro Titan 27" },
  { value: 28, label: "Dragon 28" },
  { value: 29, label: "Dragon 29" },
  { value: 30, label: "Dragon 30" },
  { value: 31, label: "Electro Dragon 31" },
  { value: 32, label: "Electro Dragon 32" },
  { value: 33, label: "Electro Dragon 33" },
  { value: 34, label: "Legend League 1" },
  { value: 35, label: "Legend League 2" },
  { value: 36, label: "Legend League 3" }
];

export const leagueOptions = defaultLeagueOptions;

export function normalizeLeagueOptions(options) {
  return Array.isArray(options) && options.length > 0
    ? options
    : defaultLeagueOptions;
}
