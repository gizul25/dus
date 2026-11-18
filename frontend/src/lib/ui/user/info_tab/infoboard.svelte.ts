import type { CurrentUser, Desk, MetricKey } from './types';
import { metrics } from './metrics';

const POLL_INTERVAL_MS = 5_000;

class Infoboard {
    loading = $state(true);
    errorMessage = $state('');
    currentUser = $state<CurrentUser | null>(null);
    desks = $state<Desk[]>([]);
    selectedIds = $state<string[]>([]);
    activeMetrics = $state<MetricKey[]>(['avgSitMin', 'avgStandMin', 'temperature']);

    private seeded = false;
    private pollTimer: ReturnType<typeof setTimeout> | null = null;

    selectedDesks = $derived(this.desks.filter((d) => this.selectedIds.includes(d.id)));
    maxByMetric = $derived.by(() => {
        const out = {} as Record<MetricKey, number>;
        for (const m of metrics) out[m.key] = Math.max(1, ...this.desks.map((d) => d[m.key]));
        return out;
    });

    toggleRow = (id: string) => {
        this.selectedIds = this.selectedIds.includes(id)
            ? this.selectedIds.filter((x) => x !== id)
            : [...this.selectedIds, id];
    };

    toggleAll = (checked: boolean) => {
        this.selectedIds = checked ? this.desks.map((d) => d.id) : [];
    };

    toggleMetric = (key: MetricKey) => {
        this.activeMetrics = this.activeMetrics.includes(key)
            ? this.activeMetrics.filter((k) => k !== key)
            : [...this.activeMetrics, key];
    };

    setActiveMetrics = (keys: MetricKey[]) => {
        this.activeMetrics = keys;
    };

    async load() {
        this.stopPolling();
        this.loading = true;
        this.errorMessage = '';
        const result = await this.fetchInfoboard();
        if (result) {
            this.applyData(result);
            this.startPolling();
        } else if (!this.errorMessage) {
            this.errorMessage = 'Could not load dashboard data.';
        }
        this.loading = false;
    }

    async refresh() {
        if (document.visibilityState === 'hidden') return;
        try {
            const result = await this.fetchInfoboard();
            if (result) {
                this.applyData(result);
            }
        } catch { }
    }

    startPolling = () => {
        this.stopPolling();
        const tick = async () => {
            await this.refresh();
            this.pollTimer = setTimeout(tick, POLL_INTERVAL_MS);
        };
        this.pollTimer = setTimeout(tick, POLL_INTERVAL_MS);
    };

    stopPolling = () => {
        if (this.pollTimer) {
            clearTimeout(this.pollTimer);
            this.pollTimer = null;
        }
    };

    handleVisibility = () => {
        if (document.visibilityState === 'visible') {
            this.refresh();
            this.startPolling();
        } else {
            this.stopPolling();
        }
    };

    private async fetchInfoboard(): Promise<{ me: any; desks: any[] } | null> {
        try {
            const [meRes, desksRes] = await Promise.all([
                fetch('/api/infoboard/me', { credentials: 'include' }),
                fetch('/api/infoboard/desks', { credentials: 'include' }),
            ]);
            if (meRes.status === 401 || desksRes.status === 401) {
                this.errorMessage = 'Session expired. Please log in again.';
                return null;
            }
            if (!meRes.ok || !desksRes.ok) {
                return null;
            }
            return { me: await meRes.json(), desks: await desksRes.json() };
        } catch {
            return null;
        }
    }

    private applyData({ me, desks: deskList }: { me: any; desks: any[] }) {
        this.currentUser = {
            name: me.name,
            standingMin: me.standing_min,
            sittingMin: me.sitting_min,
            deskId: me.desk_id,
        };
        this.desks = (deskList as any[]).map((d) => ({
            id: d.id,
            occupied: d.occupied,
            avgSitMin: d.avg_sit_min,
            avgStandMin: d.avg_stand_min,
            temperature: d.temperature,
            errors: d.errors,
            warnings: d.warnings,
        }));

        const live = new Set(this.desks.map((d) => d.id));
        this.selectedIds = this.selectedIds.filter((id) => live.has(id));

        if (!this.seeded && this.desks.length > 0) {
            this.selectedIds = this.desks.slice(0, 3).map((d) => d.id);
            this.seeded = true;
        }
    }
}

export const infoboard = new Infoboard();