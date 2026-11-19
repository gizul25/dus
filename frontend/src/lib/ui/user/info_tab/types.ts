export type MetricKey = 'avgSitMin' | 'avgStandMin' | 'temperature' | 'errors' | 'warnings';

export interface Desk {
    id: string;
    occupied: boolean;
    avgSitMin: number;
    avgStandMin: number;
    temperature: number;
    errors: number;
    warnings: number;
}

export interface CurrentUser {
    name: string;
    standingMin: number;
    sittingMin: number;
    deskId: string | null;
}

export interface MetricDef {
    key: MetricKey;
    label: string;
    short: string;
    color: string;
    format: (v: number) => string;
}