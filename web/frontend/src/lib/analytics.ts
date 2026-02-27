type EventParamValue = string | number | boolean;

export type EventParams = Record<string, EventParamValue>;

const INTERNAL_DOMAIN = 'jippylong12.xyz';
const MAILTO_PREFIX = 'mailto:';

let lastTrackedPagePath = '';

declare global {
    interface Window {
        dataLayer?: unknown[];
        gtag?: (...args: unknown[]) => void;
    }
}

const getDataAttribute = (element: HTMLElement, key: string): string | undefined => {
    let current: HTMLElement | null = element;

    while (current) {
        const value = current.dataset[key];
        if (value) {
            return value;
        }
        current = current.parentElement;
    }

    return undefined;
};

const getDestinationHost = (url: string): string => {
    if (!url) {
        return '';
    }

    if (url.startsWith(MAILTO_PREFIX)) {
        return 'mailto';
    }

    try {
        const parsed = new URL(url, window.location.href);
        return parsed.hostname;
    } catch {
        return '';
    }
};

const resolveLinkKind = (anchor: HTMLAnchorElement): string => {
    const explicitKind = getDataAttribute(anchor, 'gaKind');
    if (explicitKind) {
        return explicitKind;
    }

    const href = anchor.getAttribute('href')?.trim() ?? '';
    if (href.startsWith(MAILTO_PREFIX)) {
        return 'mailto';
    }

    const destinationHost = getDestinationHost(href);
    if (!destinationHost) {
        return 'unknown';
    }

    return isInternalDomain(destinationHost) ? 'internal' : 'external';
};

const handleDelegatedAnchorClick = (event: MouseEvent): void => {
    const target = event.target;
    if (!(target instanceof Element)) {
        return;
    }

    const anchor = target.closest('a[href]');
    if (!(anchor instanceof HTMLAnchorElement)) {
        return;
    }

    const href = anchor.getAttribute('href')?.trim() ?? '';
    const destinationHost = getDestinationHost(href);
    const textLabel = anchor.textContent?.trim() ?? '';
    const section = getDataAttribute(anchor, 'gaSection') ?? 'unassigned';
    const itemName = getDataAttribute(anchor, 'gaItem') ?? (textLabel || 'unassigned');
    const uiLabel = getDataAttribute(anchor, 'gaLabel') ?? (anchor.getAttribute('aria-label') ?? (textLabel || 'unassigned'));
    const linkKind = resolveLinkKind(anchor);

    trackEvent('portfolio_link_click', {
        section,
        item_name: itemName,
        link_kind: linkKind,
        destination_url: sanitizeDestinationUrl(href),
        destination_host: destinationHost || 'unknown',
        is_internal_domain: isInternalDomain(destinationHost),
        ui_label: uiLabel,
    });
};

export const trackEvent = (name: string, params: EventParams = {}): void => {
    if (typeof window === 'undefined' || typeof window.gtag !== 'function') {
        return;
    }

    window.gtag('event', name, params);
};

export const sanitizeDestinationUrl = (url: string): string => {
    if (!url) {
        return '';
    }

    if (url.startsWith(MAILTO_PREFIX)) {
        return url;
    }

    try {
        const parsed = new URL(url, window.location.href);
        return `${parsed.origin}${parsed.pathname}`;
    } catch {
        return url.split('#')[0].split('?')[0];
    }
};

export const isInternalDomain = (host: string): boolean => {
    if (!host) {
        return false;
    }

    const normalizedHost = host.toLowerCase().replace(/\.$/, '');
    return normalizedHost === INTERNAL_DOMAIN || normalizedHost.endsWith(`.${INTERNAL_DOMAIN}`);
};

export const trackPageView = (pathWithSearch: string): void => {
    if (!pathWithSearch || pathWithSearch === lastTrackedPagePath) {
        return;
    }

    lastTrackedPagePath = pathWithSearch;

    trackEvent('page_view', {
        page_path: pathWithSearch,
        page_location: `${window.location.origin}${pathWithSearch}`,
    });
};

export const installDelegatedLinkTracking = (): (() => void) => {
    if (typeof document === 'undefined') {
        return () => {};
    }

    document.addEventListener('click', handleDelegatedAnchorClick);
    return () => {
        document.removeEventListener('click', handleDelegatedAnchorClick);
    };
};
