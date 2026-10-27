<script lang="ts" generics="TData extends RowData">
    import { type ColumnDef, type RowData } from '@tanstack/svelte-table';
    import { type DataTableFeatures } from '#lib/ui/admin/table/data-table-features.js';
	import DataTable from '#lib/ui/admin/table/DataTable.svelte';

	type DataTableProps<TData extends RowData> = {
		columns: ColumnDef<DataTableFeatures, TData>[];
		data: TData[];
	};

	let { data, columns }: DataTableProps<TData> = $props();
</script>

<DataTable searchText="Filter emails..." searchColumn="email" {data} {columns} />