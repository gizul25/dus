<script lang="ts" generics="TData extends RowData">
	import { type ColumnDef, type RowData, createTable, FlexRender } from '@tanstack/svelte-table';
	import * as Table from '#lib/components/ui/table/index.js';
	import { Input } from '#lib/components/ui/input/index.js';
	import { features, type DataTableFeatures } from './data-table-features.js';
	import { Button } from '#lib/components/ui/button/index.js';
	import * as DropdownMenu from '#lib/components/ui/dropdown-menu/index.js';
	import * as Field from "#lib/components/ui/field/index.js";
	import * as Pagination from "#lib/components/ui/pagination/index.js";
	import * as Select from "#lib/components/ui/select/index.js";

	type DataTableProps<TData extends RowData> = {
		columns: ColumnDef<DataTableFeatures, TData>[];
		data: TData[];
	};

	let { data, columns }: DataTableProps<TData> = $props();

	const table = createTable({
		features,
		get data() {
			return data;
		},
		columns
	});

	const pagination = $derived(table.atoms.pagination.get());
	const rowsPerPage = ['5', '10', '25', '50', '100'];

	function getPageSize() {
		return pagination.pageSize;
	}

	function setPageSize(newPageSize: number) {
		table.setPageSize(newPageSize)
	}

	function getPage() {
		return pagination.pageIndex + 1;
	}

	function setPage(newPage: number) {
		table.setPageIndex(newPage - 1);
	}
</script>

<div>
	<div class="flex items-center gap-x-4 py-4">
		<Input
			placeholder="Filter emails..."
			value={(table.getColumn('email')?.getFilterValue() as string) ?? ''}
			onchange={(e) => table.getColumn('email')?.setFilterValue(e.currentTarget.value)}
			oninput={(e) => table.getColumn('email')?.setFilterValue(e.currentTarget.value)}
			class="max-w-sm"
		/>
		<Field.Field orientation="horizontal" class="ms-auto w-fit">
			<Field.Label for="select-rows-per-page">Rows per page</Field.Label>
			<Select.Root type="single" bind:value={getPageSize, setPageSize}>
				<Select.Trigger class="w-20" id="select-rows-per-page">
					<Select.Value />
				</Select.Trigger>
				<Select.Content align="start">
					<Select.Group>
						{#each rowsPerPage as rows (rows)}
							<Select.Item value={rows} label={rows}>{rows}</Select.Item>
						{/each}
					</Select.Group>
				</Select.Content>
			</Select.Root>
		</Field.Field>
		<DropdownMenu.Root>
			<DropdownMenu.Trigger>
				{#snippet child({ props })}
					<Button {...props} variant="outline">Columns</Button>
				{/snippet}
			</DropdownMenu.Trigger>
			<DropdownMenu.Content align="end">
				{#each table.getAllColumns().filter((col) => col.getCanHide()) as column (column.id)}
					<DropdownMenu.CheckboxItem
						class="capitalize"
						bind:checked={() => column.getIsVisible(), (v) => column.toggleVisibility(!!v)}
					>
						{column.id}
					</DropdownMenu.CheckboxItem>
				{/each}
			</DropdownMenu.Content>
		</DropdownMenu.Root>
	</div>
	<div class="rounded-md border">
		<Table.Root>
			<Table.Header>
				{#each table.getHeaderGroups() as headerGroup (headerGroup.id)}
					<Table.Row>
						{#each headerGroup.headers as header (header.id)}
							<Table.Head colspan={header.colSpan}>
								{#if !header.isPlaceholder}
									<FlexRender {header} />
								{/if}
							</Table.Head>
						{/each}
					</Table.Row>
				{/each}
			</Table.Header>
			<Table.Body>
				{#each table.getRowModel().rows as row (row.id)}
					<Table.Row data-state={row.getIsSelected() && 'selected'}>
						{#each row.getVisibleCells() as cell (cell.id)}
							<Table.Cell>
								<FlexRender {cell} />
							</Table.Cell>
						{/each}
					</Table.Row>
				{:else}
					<Table.Row>
						<Table.Cell colspan={columns.length} class="h-24 text-center">No results.</Table.Cell>
					</Table.Row>
				{/each}
			</Table.Body>
		</Table.Root>
	</div>
	<div class="flex items-center justify-between space-x-2 py-4">
		
		<Pagination.Root
			count={table.getRowCount()}
			bind:page={getPage, setPage}
			perPage={pagination.pageSize}
		>
			{#snippet children({ pages, currentPage })}
				<Pagination.Content>
					<Pagination.Item>
						<Pagination.Previous />
					</Pagination.Item>
					{#each pages as page (page.key)}
						{#if page.type === 'ellipsis'}
							<Pagination.Item>
								<Pagination.Ellipsis />
							</Pagination.Item>
						{:else}
							<Pagination.Item>
								<Pagination.Link {page} isActive={currentPage === page.value}>
									{page.value}
								</Pagination.Link>
							</Pagination.Item>
						{/if}
					{/each}
					<Pagination.Item>
						<Pagination.Next />
					</Pagination.Item>
				</Pagination.Content>
			{/snippet}
		</Pagination.Root>
	</div>
</div>
