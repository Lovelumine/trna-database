export type EvidenceSource = {
  ref: string;
  title: string;
  type: string;
  table: string;
  ensureId: string;
  pmid: string;
  doi: string;
  url: string;
  snippet: string;
};

const valueFor = (source: Record<string, unknown>, keys: string[]) => {
  for (const key of keys) {
    const value = source[key];
    if (value !== undefined && value !== null && String(value).trim()) {
      return String(value).trim();
    }
  }
  return '';
};

const safeSourceUrl = (value: string) => {
  const trimmed = String(value || '').trim();
  if (/^https?:\/\//i.test(trimmed)) return trimmed;
  if (/^\/(?!\/)/.test(trimmed)) return trimmed;
  return '';
};

const cleanPmid = (value: string) => {
  const match = String(value || '').match(/\d{5,9}/);
  return match?.[0] || '';
};

const cleanDoi = (value: string) => String(value || '')
  .trim()
  .replace(/^https?:\/\/(?:dx\.)?doi\.org\//i, '')
  .replace(/^doi:\s*/i, '');

export const normalizeEvidenceSources = (raw: unknown): EvidenceSource[] => {
  if (!Array.isArray(raw)) return [];
  return raw
    .filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === 'object')
    .map((source, index) => {
      const sourceRef = valueFor(source, ['source_id', 'ref', 'id']);
      const table = valueFor(source, ['table', 'table_name', 'dataset']);
      const ensureId = valueFor(source, ['ENSURE_ID', 'ensure_id', 'ensureId']);
      const pmid = cleanPmid(valueFor(source, ['PMID', 'pmid']));
      const doi = cleanDoi(valueFor(source, ['DOI', 'doi']));
      const explicitUrl = safeSourceUrl(valueFor(source, ['url', 'href', 'link']));
      const fallbackTitle = ensureId || (pmid ? `PMID ${pmid}` : '') || doi || table || `Source ${index + 1}`;
      return {
        ref: /^S\d+$/i.test(sourceRef) ? sourceRef.toUpperCase() : `S${index + 1}`,
        title: valueFor(source, ['title', 'label', 'name', 'citation']) || fallbackTitle,
        type: valueFor(source, ['type', 'source_type', 'kind']),
        table,
        ensureId,
        pmid,
        doi,
        url: explicitUrl,
        snippet: valueFor(source, ['excerpt', 'snippet', 'summary', 'content', 'text', 'evidence'])
      };
    });
};

const safeDomPart = (value: string | number) => String(value || 'message')
  .toLowerCase()
  .replace(/[^a-z0-9_-]+/g, '-');

export const evidenceTargetId = (messageId: string | number, ref: string) =>
  `evidence-${safeDomPart(messageId)}-${safeDomPart(ref)}`;

export const linkEvidenceCitations = (
  markdown: string,
  messageId: string | number,
  sources: EvidenceSource[]
) => {
  if (!markdown || !sources.length) return markdown;
  return markdown.replace(/\[S(\d+)\]/gi, (token, rawIndex) => {
    const index = Number(rawIndex) - 1;
    const source = sources[index];
    if (!source) return token;
    const directHref = evidenceLinks(source)[0]?.href;
    if (directHref) {
      const markdownHref = directHref.replace(/\(/g, '%28').replace(/\)/g, '%29');
      return `[[${source.ref}]](${markdownHref} "Open ${source.ref} source")`;
    }
    return `[[${source.ref}]](#${evidenceTargetId(messageId, source.ref)} "View ${source.ref} evidence")`;
  });
};

export const evidenceLinks = (source: EvidenceSource) => {
  const links: Array<{ label: string; href: string; external: boolean }> = [];
  if (source.table && source.ensureId) {
    links.push({
      label: source.ensureId,
      href: `/expanded/${encodeURIComponent(source.ensureId)}`,
      external: false
    });
  }
  if (source.pmid) {
    links.push({
      label: `PMID ${source.pmid}`,
      href: `https://pubmed.ncbi.nlm.nih.gov/${encodeURIComponent(source.pmid)}/`,
      external: true
    });
  }
  if (source.doi) {
    links.push({
      label: 'DOI',
      href: `https://doi.org/${encodeURI(source.doi)}`,
      external: true
    });
  }
  if (source.url && !links.some((link) => link.href === source.url)) {
    links.push({
      label: source.table ? 'Open table record' : 'Open source',
      href: source.url,
      external: /^https?:\/\//i.test(source.url)
    });
  }
  return links;
};

export const handleEvidenceReferenceClick = (event: MouseEvent) => {
  const element = event.target instanceof Element ? event.target : null;
  const anchor = element?.closest('a[href^="#evidence-"]') as HTMLAnchorElement | null;
  if (!anchor) return false;
  const targetId = decodeURIComponent(anchor.getAttribute('href')?.slice(1) || '');
  const target = targetId ? document.getElementById(targetId) : null;
  if (!target) return false;
  event.preventDefault();
  const details = target.closest('details');
  if (details) details.open = true;
  target.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  return true;
};
