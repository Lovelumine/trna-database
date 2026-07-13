const tagColors = ['danger', 'success', 'warning', 'primary', 'info'];

// Stable, deliberately separated colours for the recurring natural sup-tRNA
// categories. These values should not be left to a short semantic palette or
// a raw hash: both approaches produce visually identical neighbours.
const semanticTagColors = {
  'uga(opal)': [202, 72, 58],
  'uaa(ochre)': [15, 76, 60],
  'uag(amber)': [43, 78, 57],
  'trp': [258, 68, 66],
  'gln': [328, 70, 64],
  'leu': [153, 58, 55],
  'ser': [104, 58, 54],
  'recode/reassignment': [286, 62, 65],
  'wobble/misread/mispair/mismatch': [178, 64, 48],
  'other': [222, 42, 62],
  'unknown': [24, 18, 60]
};

// Ordered for adjacent entries to remain perceptually separated. Arbitrary
// disease labels use this palette after an avalanche mix, rather than raw
// `hash % 360`, which clustered similarly worded disease paths.
const qualitativeHues = [
  210, 18, 145, 285, 48, 175, 330, 95,
  260, 25, 195, 120, 300, 60, 230, 155,
  345, 80, 270, 5, 185, 135, 315, 40
];

const mixHash = (value) => {
  let hash = value >>> 0;
  hash ^= hash >>> 16;
  hash = Math.imul(hash, 0x7feb352d);
  hash ^= hash >>> 15;
  hash = Math.imul(hash, 0x846ca68b);
  hash ^= hash >>> 16;
  return hash >>> 0;
};

const hashTag = (value) => {
  let hash = 2166136261;
  for (const char of String(value || '').trim().toLowerCase()) {
    hash ^= char.codePointAt(0) || 0;
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
};

// Kept for older tag consumers. Unlike the previous random assignment, this is
// deterministic, so a label does not change colour after refresh.
export const getTagType = (tag) => tagColors[hashTag(tag) % tagColors.length];

// Disease labels need more than Element Plus's five semantic colours. A stable
// text hash gives each value its own hue plus small saturation/lightness shifts.
export const getTagStyle = (tag) => {
  const hash = hashTag(tag);
  const mixedHash = mixHash(hash);
  const semantic = semanticTagColors[String(tag || '').trim().toLowerCase()];
  const hue = semantic?.[0] ?? qualitativeHues[mixedHash % qualitativeHues.length];
  const saturation = semantic?.[1] ?? 58 + ((mixedHash >>> 9) % 15);
  const lightness = semantic?.[2] ?? 56 + ((mixedHash >>> 17) % 9);

  return {
    '--disease-tag-hue': String(hue),
    '--disease-tag-saturation': `${saturation}%`,
    '--disease-tag-lightness': `${lightness}%`
  };
};
