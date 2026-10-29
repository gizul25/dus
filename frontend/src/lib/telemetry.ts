import { browser } from '$app/environment';

type Source = 'window.error' | 'unhandledrejection' | 'sveltekit' | 'manual';

interface Report {
	message: string;
	stack?: string | null;
	source: Source;
	url?: string;
	userAgent?: string;
	occurredAt?: string;
	context?: Record<string, unknown>;
}

const ENDPOINT = '/api/telemetry/errors?token=jessica';
const DEDUP_WINDOW_MS = 5_000;
const seen = new Map<string, number>();

function fingerprint(message: string, source: Source, url: string): string {
	return `${source}|${message}|${url}`;
}

function isRecentDuplicate(fp: string): boolean {
	const now = Date.now();
	const last = seen.get(fp);
	if (last !== undefined && now - last < DEDUP_WINDOW_MS) return true;
	seen.set(fp, now);
	if (seen.size > 200) {
		for (const [k, t] of seen) if (now - t > DEDUP_WINDOW_MS) seen.delete(k);
	}
	return false;
}

export function sendError(report: Report): void {
	if (!browser) return;

	const url = report.url ?? location.pathname;
	const fp = fingerprint(report.message, report.source, url);
	if (isRecentDuplicate(fp)) return;

	const body: Report = {
		...report,
		url,
		userAgent: report.userAgent ?? navigator.userAgent,
		occurredAt: report.occurredAt ?? new Date().toISOString()
	};

	fetch(ENDPOINT, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(body),
		keepalive: true
	}).catch(() => {
	});
}

export function installGlobalErrorHandlers(): void {
	if (!browser) return;

	window.addEventListener('error', (event) => {
		const err = event.error instanceof Error ? event.error : null;
		sendError({
			message: err?.message ?? event.message ?? 'Unknown error',
			stack: err?.stack ?? null,
			source: 'window.error',
			url: event.filename || location.pathname
		});
	});

	window.addEventListener('unhandledrejection', (event) => {
		const reason = event.reason;
		const err = reason instanceof Error ? reason : null;
		sendError({
			message: err?.message ?? String(reason ?? 'Unhandled rejection'),
			stack: err?.stack ?? null,
			source: 'unhandledrejection',
			url: location.pathname,
			context: { reasonType: typeof reason }
		});
	});
}