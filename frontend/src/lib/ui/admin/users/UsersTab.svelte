<script lang="ts">
	import DataTable from './DataTable.svelte';
	import { columns, type User } from './columns.js';

	export const data: User[] = [
		{
			id: '728ed52f',
			firstName: 'Real',
			lastName: 'Name',
			email: 'rn@example.com'
		},
		{
			id: '489e1d42',
			firstName: 'Banger',
			lastName: 'Lastname',
			email: 'banger@gmail.com'
		},
		...[...Array(25).keys()].map((_) => ({
			id: '489e1d42',
			firstName: 'Purely',
			lastName: 'Surely',
			email: 'psurely@gmail.com'
		}))
	];
</script>

<DataTable {data} {columns} />
