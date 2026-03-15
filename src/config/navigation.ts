export type SiteNavItem = {
  path: string;
  label: string;
};

export type SiteToolItem = {
  path: string;
  label: string;
  href?: string;
};

export const APP_PATHS = {
  home: '/',
  disease: '/CodingVariationDisease',
  therapeutics: '/tRNAtherapeutics',
  natural: '/naturalsuptRNA',
  elements: '/tRNAElements',
  expanded: '/expanded/:key',
  about: '/about',
  help: '/help',
  helpEntry: '/help.html',
  download: '/download',
  ai: '/AIYingying',
  audio: '/audio',
  blast: '/blast',
  admin: '/admin',
  adminLogin: '/admin/login',
  adminWorkspace: '/admin/workspace',
  adminEngineered: '/admin/engineered-sup-trna',
} as const;

export const PRIMARY_NAV_ITEMS: SiteNavItem[] = [
  { path: APP_PATHS.home, label: 'Home' },
  { path: APP_PATHS.disease, label: 'Mutation-induced Disease' },
  { path: APP_PATHS.natural, label: 'Natural sup-tRNA' },
  { path: APP_PATHS.therapeutics, label: 'Engineered sup-tRNA' },
  { path: APP_PATHS.elements, label: 'tRNA Elements' },
  { path: APP_PATHS.blast, label: 'Blast Search' },
  { path: APP_PATHS.ai, label: 'AI Assistant' },
];

export const SECONDARY_NAV_ITEMS: SiteToolItem[] = [
  { path: APP_PATHS.download, label: 'Download' },
  { path: APP_PATHS.help, label: 'Help', href: APP_PATHS.helpEntry },
  { path: APP_PATHS.about, label: 'About' },
];

export const HELP_EXTERNAL_ROUTE_PATHS = [
  ...PRIMARY_NAV_ITEMS.map((item) => item.path),
  ...SECONDARY_NAV_ITEMS.filter((item) => item.path !== APP_PATHS.help).map((item) => item.path),
  APP_PATHS.audio,
  APP_PATHS.admin,
  APP_PATHS.adminLogin,
  APP_PATHS.adminWorkspace,
  APP_PATHS.adminEngineered,
];

export const MAIN_PREFETCH_ROUTE_PATHS = [
  APP_PATHS.disease,
  APP_PATHS.therapeutics,
  APP_PATHS.natural,
  APP_PATHS.elements,
  APP_PATHS.about,
  APP_PATHS.download,
];
