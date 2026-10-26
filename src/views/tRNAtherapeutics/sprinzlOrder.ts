/**
 * Sprinzl coordinate order for the Per-Position Alignment Variation chart.
 *
 * The chart used to sort the numeric positions 1..76 and then append every
 * insertion or variable-arm label in whatever order the table returned.  That
 * separated `20a` from `20`, and pulled the variable-arm labels out to the far
 * end of the axis, away from the 45/46 junction they belong to.
 *
 * `sortBySprinzlChain` orders labels the way the molecule is actually read:
 * 5' -> 3' along the Sprinzl path, with an insertion label placed directly after
 * the column it hangs from.  The label list mirrors `SPRINZL_MATCH_ORDER` in
 * LLM-tRNAAlign `APP/backend/domain/alignment/sprinzl_coordinates.py`; keep the
 * two in step when the coordinate frame changes.
 */

export const SPRINZL_MATCH_ORDER: readonly string[] = [
  '1', '2', '3', '4', '5', '6', '7', '8', '9',
  '10', '11', '12', '13', '14', '15', '16', '17', '17a', '18', '19',
  '20', '20a', '20b', '21', '22', '23', '24', '25', '26',
  '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38',
  '39', '40', '41', '42', '43', '44', '45',
  'V11', 'V12', 'V13', 'V14', 'V15', 'V16', 'V17',
  'V1', 'V2', 'V3', 'V4', 'V5',
  'V27', 'V26', 'V25', 'V24', 'V23', 'V22', 'V21',
  '46', '47', '48',
  '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60',
  '61', '62', '63', '64', '65',
  '66', '67', '68', '69', '70', '71', '72', '73', '74', '75', '76',
];

const PARENT_ORDER: readonly string[] = ['-1', ...SPRINZL_MATCH_ORDER];
const PARENT_INDEX = new Map<string, number>(PARENT_ORDER.map((label, index) => [label, index]));
const INSERTION_RE = /^(.+?)i(\d+)$/;

/** `[anchor index, kind, insertion number]`; unknown labels sort last. */
export function sprinzlOrderKey(label: string): [number, number, number] {
  const value = String(label ?? '').trim();
  const insertion = INSERTION_RE.exec(value);
  if (insertion) {
    const anchor = PARENT_INDEX.get(insertion[1]);
    if (anchor !== undefined) return [anchor, 1, Number(insertion[2])];
  }
  const own = PARENT_INDEX.get(value);
  if (own !== undefined) return [own, 0, 0];
  return [PARENT_ORDER.length, 2, 0];
}

export function sortBySprinzlChain<T>(rows: readonly T[], positionOf: (row: T) => string): T[] {
  return [...rows].sort((left, right) => {
    const a = sprinzlOrderKey(positionOf(left));
    const b = sprinzlOrderKey(positionOf(right));
    return a[0] - b[0] || a[1] - b[1] || a[2] - b[2]
      || String(positionOf(left)).localeCompare(String(positionOf(right)));
  });
}


/**
 * Merge every insertion column of one anchor into a single `<anchor>i` column.
 *
 * `37i1 ... 37i33` are not 33 different positions: they are the residues of a
 * handful of engineered tRNAs that the coordinate frame cannot place on a
 * canonical position.  One column per slot makes the axis unreadable and lets a
 * few long sequences dominate the picture.  The merged column sums the series and
 * sits where the first member of that family fell in chain order, which is also
 * how Figure 7 of the SprinzlMap paper counts them.
 */
export function mergeInsertionColumns<T extends { position: string }>(
  rows: readonly T[], seriesKeys: readonly string[]
): T[] {
  const ordered = sortBySprinzlChain(rows, (row) => row.position);
  const merged: T[] = [];
  const emitted = new Set<string>();
  for (const row of ordered) {
    const match = INSERTION_RE.exec(String(row.position));
    if (!match) {
      merged.push(row);
      continue;
    }
    const anchor = match[1];
    const label = anchor + "i";
    if (emitted.has(label)) continue;
    emitted.add(label);
    const totals: Record<string, number> = {};
    for (const key of seriesKeys) {
      totals[key] = ordered.reduce((sum, other) => {
        const g = INSERTION_RE.exec(String(other.position));
        return g && g[1] === anchor
          ? sum + Number((other as Record<string, unknown>)[key] ?? 0)
          : sum;
      }, 0);
    }
    merged.push({ ...row, position: label, ...totals } as T);
  }
  return merged;
}
