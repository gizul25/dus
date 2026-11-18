<script lang="ts">
  export interface ChartSeries {
    key: string;
    label: string;
    color: string;
    format: (v: number) => string;
  }
  export interface ChartGroup {
    id: string;
    label: string;
    highlight?: boolean;
    values: Record<string, number>;
  }

  interface Props {
    groups: ChartGroup[];
    series: ChartSeries[];
    max: Record<string, number>;
    height?: string;
    minBarHeightPercent?: number;
    maxBarWidth?: number;
  }
  let {
    groups,
    series,
    max,
    height = '16rem',
    minBarHeightPercent = 2,
    maxBarWidth = 18,
  }: Props = $props();
</script>

<div class="px-1 pt-2">
  <div
    class="flex items-stretch gap-3.5 pb-0.5"
    style={`height:${height};background-image:repeating-linear-gradient(to top, color-mix(in oklch, var(--border) 60%, transparent) 0 1px, transparent 1px 25%)`}
  >
    {#each groups as group (group.id)}
      <div class="flex min-w-0 flex-1 flex-col gap-2">
        <div class="flex min-h-0 flex-1 items-end justify-center gap-1">
          {#each series as s (s.key)}
            {@const v = group.values[s.key] ?? 0}
            {@const h = Math.max(minBarHeightPercent, (v / (max[s.key] || 1)) * 100)}
            <div
              class="min-w-1 flex-1 rounded-t-[4px] transition-[height] duration-300"
              style={`max-width:${maxBarWidth}px;height:${h}%;background:${s.color}`}
              title={`${group.label} · ${s.label}: ${s.format(v)}`}
            />
          {/each}
        </div>
        <span
          class="text-center text-[11px] tabular-nums text-muted-foreground {group.highlight ? 'font-bold text-primary' : ''}"
        >
          {group.label}
        </span>
      </div>
    {/each}
  </div>
</div>