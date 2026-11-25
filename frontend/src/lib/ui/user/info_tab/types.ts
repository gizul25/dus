export type SessionStatus = 
	| 'online' 
	| 'away' 
	| 'do not disturb';

export type Timeframe = 
	| 'today' 
	| 'week' 
	| 'month' 
	| 'all';

export type MetricKey =
	| 'timeUsedMin'
	| 'uniqueUsers'
	| 'temperature'
	| 'humidity'
	| 'light'
	| 'errors'
	| 'warnings';

export interface Desk {
	id: string;
	occupied: boolean;
	timeUsedMin: number;
	uniqueUsers: number;
	temperature: number;
	humidity: number;
	light: number;
	errors: number;
	warnings: number;
}

export interface CurrentUser {
	name: string;
	standingMin: number;
	sittingMin: number;
	deskId: string | null;
	status: SessionStatus | null;
	sessionStartedAt: string | null;
}

export interface MetricDef {
	key: MetricKey;
	label: string;
	short: string;
	color: string;
	format: (v: number) => string;
}