<script lang="ts">
	import DeskDataTable from './DeskDataTable.svelte';
	import { columns, type Desk } from './columns.js';

	export const data: Desk[] = [
		{
			id: '728ed52f',
		},
		{
			id: '489e1d42',
		},
		...[...Array(25).keys()].map((_) => ({
			id: '489e1d42',
		}))
	];
</script>

<DeskDataTable {data} {columns} />
