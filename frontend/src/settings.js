export const DEFAULT_VALIDITY_PERIOD = 86400;

// Options for fixing resolution on connection
export const SCREEN_SIZES = [
    [640,  480],
    [1024, 768],
    [1280, 1024],
    [1440, 1050],
    [1920, 1080],
    [2560, 1440],
];

export const SETTINGS_LINKS = [
    {url: "/admin/", name: "Administration", tabName: "Admin"},
    {url: "/api/",name: "API Browser", tabName: "API"},
];

// Options for validity period when sharing a ticket
export const VALIDITY_PERIOD_OPTIONS = [
    {key: "15min", value: 15*60, text: "15 minutes"},
    {key: "30min", value: 30*60, text: "30 minutes"},
    {key: "1h", value: 60*60, text: "1 hour"},
    {key: "4h", value: 4*60*60, text: "4 hours"},
    {key: "12h", value: 12*60*60, text: "12 hours"},
    {key: "24h", value: 24*60*60, text: "24 hours"},
    {key: "48h", value: 48*60*60, text: "48 hours"},
];
