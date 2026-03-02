export const WAR_FREQUENCY_OPTIONS = [
    { value: "always", label: "Always" },
    { value: "moreThanOncePerWeek", label: "More than once per week" },
    { value: "oncePerWeek", label: "Once per week" },
    { value: "lessThanOncePerWeek", label: "Less than once per week" },
    { value: "never", label: "Never" },
];

const WAR_FREQUENCY_LABELS = Object.fromEntries(
    [
        ...WAR_FREQUENCY_OPTIONS,
        { value: "unknown", label: "unknown" },
    ].map(({ value, label }) => [value, label]),
);

export function formatWarFrequency(value) {
    if (!value) return "unknown";
    return WAR_FREQUENCY_LABELS[value] ?? "unknown";
}
