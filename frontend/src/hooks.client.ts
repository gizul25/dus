import type { HandleClientError } from '@sveltejs/kit';
import { installGlobalErrorHandlers, sendError } from '#lib/telemetry';

installGlobalErrorHandlers();

export const handleError: HandleClientError = ({ error, status, message }) => {
	const err = error instanceof Error ? error : null;
	sendError({
		message: err?.message ?? message ?? 'SvelteKit client error',
		stack: err?.stack ?? null,
		source: 'sveltekit',
		context: { status }
	});
	return { message: 'An unexpected error occurred.' };
};