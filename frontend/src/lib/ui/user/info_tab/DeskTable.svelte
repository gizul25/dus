<script lang="ts">
	import * as Card from '#lib/components/ui/card';
	import * as Table from '#lib/components/ui/table';
	import { Checkbox } from '#lib/components/ui/checkbox';
	import type { Desk, MetricKey } from './types';
	import { metrics } from './metrics';

	interface Props {
		desks: Desk[];
		currentDeskId: string | null;
		selectedIds: string[];
		activeMetrics: MetricKey[];
		onToggleRow: (id: string) => void;
		onToggleAll: (checked: boolean) => void;
		onToggleMetric: (key: MetricKey) => void;
	}
	let {
		desks,
		currentDeskId,
		selectedIds,
		activeMetrics,
		onToggleRow,
		onToggleAll,
		onToggleMetric
	}: Props = $props();

	const allSelected = $derived(desks.length > 0 && selectedIds.length === desks.length);
	const someSelected = $derived(selectedIds.length > 0 && !allSelected);
</script>

<Card.Root>
	<Card.Header>
		<div class="flex items-baseline justify-between gap-3">
			<Card.Title class="text-sm">Desks in the system</Card.Title>
			<span class="text-xs tabular-nums text-muted-foreground">
				{selectedIds.length} / {desks.length} selected
			</span>
		</div>
	</Card.Header>

	<Card.Content>
		<Table.Root>
			<Table.Header>
				<Table.Row>
					<Table.Head class="w-8">
						<Checkbox
							checked={allSelected}
							indeterminate={someSelected}
							onCheckedChange={(c) => onToggleAll(c === true)}
							aria-label="Select all desks"
						/>
					</Table.Head>
					<Table.Head class="whitespace-nowrap text-[10px] font-semibold uppercase tracking-widest">
						Desk
					</Table.Head>
					<Table.Head class="whitespace-nowrap text-[10px] font-semibold uppercase tracking-widest">
						Occupation
					</Table.Head>
					{#each metrics as m (m.key)}
						<Table.Head
							class="whitespace-nowrap text-right text-[10px] font-semibold uppercase tracking-widest"
						>
							<label
								class="inline-flex cursor-pointer select-none items-center gap-1.5"
								title="Show “{m.label}” in the chart"
							>
								<Checkbox
									checked={activeMetrics.includes(m.key)}
									onCheckedChange={() => onToggleMetric(m.key)}
								/>
								<span>{m.short}</span>
							</label>
						</Table.Head>
					{/each}
				</Table.Row>
			</Table.Header>

			<Table.Body>
				{#each desks as desk (desk.id)}
					<Table.Row
						class={desk.id === currentDeskId
							? 'bg-primary/5 shadow-[inset_3px_0_0_var(--primary)]'
							: ''}
					>
						<Table.Cell>
							<Checkbox
								checked={selectedIds.includes(desk.id)}
								onCheckedChange={() => onToggleRow(desk.id)}
								aria-label={`Select ${desk.id}`}
							/>
						</Table.Cell>
						<Table.Cell class="whitespace-nowrap font-semibold tabular-nums">
							{desk.id}
						</Table.Cell>
						<Table.Cell class="whitespace-nowrap">
							{#if desk.occupied}
								<span
									class="inline-block rounded-full border border-destructive/30 bg-destructive/15 px-2.5 py-1 text-[10px] font-bold tracking-wider text-destructive"
								>
									OCCUPIED
								</span>
							{:else}
								<span
									class="inline-block rounded-full border border-emerald-500/30 bg-emerald-500/15 px-2.5 py-1 text-[10px] font-bold tracking-wider text-emerald-600 dark:text-emerald-400"
								>
									FREE
								</span>
							{/if}
						</Table.Cell>
						{#each metrics as m (m.key)}
							<Table.Cell class="whitespace-nowrap text-right tabular-nums text-foreground/80">
								{m.format(desk[m.key])}
							</Table.Cell>
						{/each}
					</Table.Row>
				{/each}
			</Table.Body>
		</Table.Root>
	</Card.Content>
</Card.Root>
