<script lang="ts">
  import { onMount } from 'svelte';

  /* ---------------------------------------------------------------- */
  /*  Types                                                           */
  /* ---------------------------------------------------------------- */
  type MetricKey = 'avgSitMin' | 'avgStandMin' | 'temperature' | 'errors' | 'warnings';

  interface Desk {
    id: string;
    occupied: boolean;
    avgSitMin: number;
    avgStandMin: number;
    temperature: number;
    errors: number;
    warnings: number;
  }

  interface CurrentUser {
    name: string;
    standingMin: number;
    sittingMin: number;
    deskId: string | null;
  }

  interface MetricDef {
    key: MetricKey;
    label: string;
    short: string;
    color: string;
    format: (v: number) => string;
  }

  /* ---------------------------------------------------------------- */
  /*  Formatters & metric definitions (unchanged)                     */
  /* ---------------------------------------------------------------- */
  const fmtDuration = (min: number) =>
    `${Math.floor(min / 60)}h ${String(Math.round(min % 60)).padStart(2, '0')}m`;
  const fmtTemp = (v: number) => `${v.toFixed(1)} °C`;
  const fmtInt = (v: number) => String(Math.round(v));

  const metrics: MetricDef[] = [
    { key: 'avgSitMin',   label: 'Avg. sitting time',  short: 'Ø Sit',   color: 'var(--chart-1)', format: fmtDuration },
    { key: 'avgStandMin', label: 'Avg. standing time', short: 'Ø Stand', color: 'var(--chart-2)', format: fmtDuration },
    { key: 'temperature', label: 'Temperature',        short: 'Temp',    color: 'var(--chart-3)', format: fmtTemp },
    { key: 'errors',      label: 'Errors',             short: 'Errors',  color: 'var(--chart-4)', format: fmtInt },
    { key: 'warnings',    label: 'Warnings',           short: 'Warn',    color: 'var(--chart-5)', format: fmtInt }
  ];
  const metricMap = Object.fromEntries(metrics.map((m) => [m.key, m])) as Record<MetricKey, MetricDef>;

  /* ---------------------------------------------------------------- */
  /*  State                                                           */
  /* ---------------------------------------------------------------- */
  let loading = $state(true);
  let errorMessage = $state('');
  let currentUser = $state<CurrentUser | null>(null);
  let desks = $state<Desk[]>([]);

  let selectedIds = $state<string[]>([]);
  let activeMetrics = $state<MetricKey[]>(['avgSitMin', 'avgStandMin', 'temperature']);

  let headerCheckbox = $state<HTMLInputElement | null>(null);
  let seeded = $state(false);

  /* ---------------------------------------------------------------- */
  /*  Derived                                                         */
  /* ---------------------------------------------------------------- */
  const allSelected = $derived(desks.length > 0 && selectedIds.length === desks.length);
  const someSelected = $derived(selectedIds.length > 0 && !allSelected);
  const selectedDesks = $derived(desks.filter((d) => selectedIds.includes(d.id)));

  const maxByMetric = $derived.by(() => {
    const out = {} as Record<MetricKey, number>;
    for (const m of metrics) out[m.key] = Math.max(1, ...desks.map((d) => d[m.key]));
    return out;
  });

  const initials = $derived(
    (currentUser?.name ?? '?')
      .split(' ').map((p) => p[0]).join('').slice(0, 2).toUpperCase()
  );
  const totalTracked = $derived((currentUser?.standingMin ?? 0) + (currentUser?.sittingMin ?? 0));
  const standShare = $derived(
    totalTracked > 0 ? ((currentUser?.standingMin ?? 0) / totalTracked) * 100 : 0
  );
  const donutCircumference = 2 * Math.PI * 40; // r=40 in the SVG below

  /* header checkbox indeterminate state */
  $effect(() => {
    if (headerCheckbox) headerCheckbox.indeterminate = someSelected;
  });

  /* seed chart selection the first time data arrives */
  $effect(() => {
    if (!seeded && desks.length > 0) {
      selectedIds = desks.slice(0, 3).map((d) => d.id);
      seeded = true;
    }
  });

  /* ---------------------------------------------------------------- */
  /*  Data fetch — same style as handleLogin() in the login page      */
  /* ---------------------------------------------------------------- */
  async function loadDashboard() {
    loading = true;
    errorMessage = '';
    try {
      const [meRes, desksRes] = await Promise.all([
        fetch('/api/dashboard/me',    { credentials: 'include' }),
        fetch('/api/dashboard/desks', { credentials: 'include' })
      ]);

      if (meRes.status === 401 || desksRes.status === 401) {
        errorMessage = 'Session expired. Please log in again.';
        return;
      }
      if (!meRes.ok || !desksRes.ok) {
        errorMessage = 'Could not load dashboard data.';
        return;
      }

      const me = await meRes.json();
      const deskList = await desksRes.json();

      currentUser = {
        name: me.name,
        standingMin: me.standing_min,
        sittingMin: me.sitting_min,
        deskId: me.desk_id
      };
      desks = (deskList as any[]).map((d) => ({
        id: d.id,
        occupied: d.occupied,
        avgSitMin: d.avg_sit_min,
        avgStandMin: d.avg_stand_min,
        temperature: d.temperature,
        errors: d.errors,
        warnings: d.warnings
      }));
    } catch (err) {
      console.error('Dashboard load failed', err);
      errorMessage = 'Network error while loading dashboard.';
    } finally {
      loading = false;
    }
  }

  onMount(loadDashboard);

  /* ---------------------------------------------------------------- */
  /*  Actions                                                         */
  /* ---------------------------------------------------------------- */
  function toggleRow(id: string) {
    selectedIds = selectedIds.includes(id)
      ? selectedIds.filter((x) => x !== id)
      : [...selectedIds, id];
  }

  function toggleAll(event: Event) {
    const checked = (event.currentTarget as HTMLInputElement).checked;
    selectedIds = checked ? desks.map((d) => d.id) : [];
  }

  function toggleMetric(key: MetricKey) {
    activeMetrics = activeMetrics.includes(key)
      ? activeMetrics.filter((k) => k !== key)
      : [...activeMetrics, key];
  }
</script>

<svelte:head>
  <title>Desk usage overview</title>
</svelte:head>

<div class="min-h-screen bg-background p-6 text-foreground">
  {#if loading}
    <div class="flex min-h-[60vh] items-center justify-center">
      <p class="text-sm text-muted-foreground">Loading dashboard…</p>
    </div>
  {:else if errorMessage}
    <div
      class="mx-auto mt-16 max-w-md rounded-xl border border-border bg-card p-6 text-center text-card-foreground shadow-sm"
    >
      <p class="mb-4 text-sm text-destructive">{errorMessage}</p>
      <div class="flex justify-center gap-3">
        <button
          type="button"
          onclick={loadDashboard}
          class="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:opacity-90"
        >
          Retry
        </button>
        <a
          href="/"
          class="rounded-md border border-border px-4 py-2 text-sm hover:bg-muted"
        >
          Log in
        </a>
      </div>
    </div>
  {:else if currentUser}
    <!-- ─────────────────────  CURRENT USER  ───────────────────── -->
    <section
      class="mb-5 flex flex-wrap items-center gap-5 rounded-xl border border-border bg-card p-5 text-card-foreground shadow-sm md:gap-8"
    >
      <div class="flex min-w-56 flex-1 items-center gap-3">
        <div class="grid h-12 w-12 shrink-0 place-items-center rounded-full bg-primary text-sm font-bold text-primary-foreground">
          {initials}
        </div>
        <div>
          <h1 class="text-lg font-semibold leading-tight">{currentUser.name}</h1>
          <p class="mt-0.5 text-xs text-muted-foreground">Personal desk usage · today</p>
        </div>
      </div>

      <div class="flex flex-wrap gap-3">
        <div class="flex min-w-28 flex-col gap-1 rounded-lg border border-border bg-muted/50 px-3.5 py-2.5">
          <span class="text-[10px] uppercase tracking-widest text-muted-foreground">Standing time</span>
          <span class="text-lg font-semibold tabular-nums text-chart-2">{fmtDuration(currentUser.standingMin)}</span>
        </div>
        <div class="flex min-w-28 flex-col gap-1 rounded-lg border border-border bg-muted/50 px-3.5 py-2.5">
          <span class="text-[10px] uppercase tracking-widest text-muted-foreground">Sitting time</span>
          <span class="text-lg font-semibold tabular-nums text-chart-1">{fmtDuration(currentUser.sittingMin)}</span>
        </div>
        <div class="flex min-w-28 flex-col gap-1 rounded-lg border border-border bg-muted/50 px-3.5 py-2.5">
          <span class="text-[10px] uppercase tracking-widest text-muted-foreground">Current desk</span>
          <span class="text-lg font-semibold tabular-nums" class:text-muted-foreground={!currentUser.deskId}>
            {currentUser.deskId ?? 'none'}
          </span>
        </div>
      </div>

      <!-- donut + legend -->
      <div class="flex w-full items-center justify-center gap-6 md:justify-start">
        <div class="relative flex shrink-0 items-center justify-center">
          <svg viewBox="0 0 100 100" class="h-32 w-32 -rotate-90">
            <circle cx="50" cy="50" r="40" fill="none" stroke="var(--chart-1)" stroke-width="14" />
            <circle
              cx="50" cy="50" r="40" fill="none"
              stroke="var(--chart-2)" stroke-width="14"
              stroke-dasharray={`${(standShare / 100) * donutCircumference} ${donutCircumference}`}
              class="transition-[stroke-dasharray] duration-300"
            />
          </svg>
          <div class="pointer-events-none absolute inset-0 flex flex-col items-center justify-center text-center">
            <span class="text-base font-bold tabular-nums leading-none">{standShare.toFixed(0)}%</span>
            <span class="mt-1 text-[9px] uppercase tracking-widest text-muted-foreground">standing</span>
          </div>
        </div>

        <div class="flex flex-col gap-2 text-xs">
          <div class="flex items-center gap-2">
            <span class="h-2.5 w-2.5 rounded-sm bg-chart-2"></span>
            <span class="text-muted-foreground">Standing</span>
            <span class="font-semibold tabular-nums">{fmtDuration(currentUser.standingMin)}</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="h-2.5 w-2.5 rounded-sm bg-chart-1"></span>
            <span class="text-muted-foreground">Sitting</span>
            <span class="font-semibold tabular-nums">{fmtDuration(currentUser.sittingMin)}</span>
          </div>
          <div class="mt-1 flex items-center gap-2 border-t border-border pt-2">
            <span class="text-muted-foreground">Total</span>
            <span class="font-semibold tabular-nums">{fmtDuration(totalTracked)}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ─────────────  TABLE + COLUMN CHART  ───────────── -->
    <div class="grid grid-cols-1 gap-5 lg:grid-cols-[1.65fr_1fr]">
      <!-- Desks table -->
      <section class="rounded-xl border border-border bg-card p-5 text-card-foreground shadow-sm">
        <header class="mb-3 flex items-baseline justify-between gap-3">
          <h2 class="text-sm font-semibold">Desks in the system</h2>
          <span class="text-xs tabular-nums text-muted-foreground">{selectedIds.length} / {desks.length} selected</span>
        </header>

        <div class="overflow-x-auto">
          <table class="w-full border-collapse text-[13px]">
            <thead>
              <tr class="border-b border-border">
                <th class="w-8 px-1 py-2 text-left">
                  <input
                    type="checkbox"
                    class="h-3.5 w-3.5 cursor-pointer accent-primary"
                    bind:this={headerCheckbox}
                    checked={allSelected}
                    onchange={toggleAll}
                    aria-label="Select all desks"
                  />
                </th>
                <th class="whitespace-nowrap px-2 py-2 text-left text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">Desk</th>
                <th class="whitespace-nowrap px-2 py-2 text-left text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">Occupation</th>
                {#each metrics as m (m.key)}
                  <th class="whitespace-nowrap px-2 py-2 text-right text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
                    <label class="inline-flex cursor-pointer select-none items-center gap-1.5" title="Show “{m.label}” in the chart">
                      <input
                        type="checkbox"
                        class="h-3.5 w-3.5 cursor-pointer accent-primary"
                        checked={activeMetrics.includes(m.key)}
                        onchange={() => toggleMetric(m.key)}
                      />
                      <span>{m.short}</span>
                    </label>
                  </th>
                {/each}
              </tr>
            </thead>

            <tbody>
              {#each desks as desk (desk.id)}
                <tr
                  class="border-b border-border/60 transition-colors hover:bg-muted/40 {desk.id === currentUser.deskId
                    ? 'bg-primary/5 shadow-[inset_3px_0_0_var(--primary)]'
                    : ''}"
                >
                  <td class="px-1 py-2">
                    <input
                      type="checkbox"
                      class="h-3.5 w-3.5 cursor-pointer accent-primary"
                      checked={selectedIds.includes(desk.id)}
                      onchange={() => toggleRow(desk.id)}
                      aria-label={`Select ${desk.id}`}
                    />
                  </td>
                  <td class="whitespace-nowrap px-2 py-2 font-semibold tabular-nums">{desk.id}</td>
                  <td class="whitespace-nowrap px-2 py-2">
                    {#if desk.occupied}
                      <span class="inline-block rounded-full border border-destructive/30 bg-destructive/15 px-2.5 py-1 text-[10px] font-bold tracking-wider text-destructive">OCCUPIED</span>
                    {:else}
                      <span class="inline-block rounded-full border border-emerald-500/30 bg-emerald-500/15 px-2.5 py-1 text-[10px] font-bold tracking-wider text-emerald-600 dark:text-emerald-400">FREE</span>
                    {/if}
                  </td>
                  {#each metrics as m (m.key)}
                    <td class="whitespace-nowrap px-2 py-2 text-right tabular-nums text-foreground/80">
                      {m.format(desk[m.key])}
                    </td>
                  {/each}
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </section>

      <!-- Column chart -->
      <section class="rounded-xl border border-border bg-card p-5 text-card-foreground shadow-sm">
        <header class="mb-3 flex items-baseline justify-between gap-3">
          <h2 class="text-sm font-semibold">Comparison</h2>
          <span class="text-xs tabular-nums text-muted-foreground">{selectedDesks.length} desk(s)</span>
        </header>

        {#if selectedDesks.length === 0}
          <p class="my-8 text-center text-[13px] text-muted-foreground">Select at least one desk in the table to visualize it.</p>
        {:else if activeMetrics.length === 0}
          <p class="my-8 text-center text-[13px] text-muted-foreground">Select at least one topic in the table header.</p>
        {:else}
          <div class="px-1 pt-2">
            <div
              class="flex h-64 items-stretch gap-3.5 pb-0.5"
              style="background-image: repeating-linear-gradient(to top, color-mix(in oklch, var(--border) 60%, transparent) 0 1px, transparent 1px 25%)"
            >
              {#each selectedDesks as desk (desk.id)}
                <div class="flex min-w-0 flex-1 flex-col gap-2">
                  <div class="flex min-h-0 flex-1 items-end justify-center gap-1">
                    {#each activeMetrics as key (key)}
                      {@const metric = metricMap[key]}
                      {@const h = Math.max(2, (desk[key] / maxByMetric[key]) * 100)}
                      <div
                        class="min-w-1 max-w-[18px] flex-1 rounded-t-[4px] transition-[height] duration-300"
                        style={`height:${h}%;background:${metric.color}`}
                        title={`${desk.id} · ${metric.label}: ${metric.format(desk[key])}`}
                      ></div>
                    {/each}
                  </div>
                  <span
                    class="text-center text-[11px] tabular-nums text-muted-foreground {desk.id === currentUser.deskId
                      ? 'font-bold text-primary'
                      : ''}"
                  >{desk.id}</span>
                </div>
              {/each}
            </div>
          </div>
        {/if}

        <div class="mt-4 flex flex-wrap gap-1.5 border-t border-border pt-3.5">
          {#each metrics as m (m.key)}
            <button
              type="button"
              class="inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] transition-colors {activeMetrics.includes(m.key)
                ? 'border-border bg-muted text-foreground'
                : 'border-border/60 text-muted-foreground hover:border-border'}"
              onclick={() => toggleMetric(m.key)}
            >
              <span
                class="h-2 w-2 rounded-full transition-opacity"
                class:opacity-30={!activeMetrics.includes(m.key)}
                style={`background:${m.color}`}
              ></span>
              {m.label}
            </button>
          {/each}
        </div>
      </section>
    </div>
  {/if}
</div>