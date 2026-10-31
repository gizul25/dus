<script lang="ts">
	import { Button } from '#lib/components/ui/button/index.js';
	import { setContext } from 'svelte';
	import DataTable from '#lib/ui/admin/table/DataTable.svelte';
	import AddDeskDialog from './AddDeskDialog.svelte';
	import DeleteDeskDialog from './DeleteDeskDialog.svelte';
	import EditDeskDialog from './EditDeskDialog.svelte';
	import { columns, type Desk } from './columns.js';

	let data: Desk[] = $state([
		{
			id: '728ed52f',
			name: "Desk 1"
		},
		{
			id: '489e1d42',
			name: "Desk 2"
		},
		// ...[...Array(25).keys()].map((_) => ({
		// 	id: '489e1d42',
		// 	name: "Desk1 2"
		// }))
	]);

	let editingDesk: Desk = $state({
		name: '',
	});
	let createDialogIsOpen = $state(false);
	let deleteDialogIsOpen = $state(false);
	let editDialogIsOpen = $state(false);

	function openCreateNewDesk() {
		console.log('openCreateNewDesk');
		editingDesk = {
			name: '',
		};
		createDialogIsOpen = true;
	}

	function openEditDeskDetails(id: string) {
		console.log('openEditDeskDetails', id);
		editingDesk = data.find((u) => u.id === id);
		editDialogIsOpen = true;
	}

	function openDeleteDesk(id: string) {
		console.log('openDeleteDesk', id);
		editingDesk = data.find((u) => u.id === id);
		deleteDialogIsOpen = true;
	}

	function createNewDesk(desk: Desk) {
		data = [
			...data,
			{
				...desk,
				id: '127312391'
			}
		];
		return true;
	}

	function onEditDesk(newDesk) {
		let deskEntry = data.find((u) => u.id === newDesk.id);
		deskEntry = newDesk;
		data = [...data];
		return true;
	}

	function onDelete() {
		data = data.filter((u) => u.id !== editingDesk.id);
	}

	setContext('actionContext', {
		openCreateNewDesk,
		openEditDeskDetails,
		openDeleteDesk
	});
</script>

<AddDeskDialog bind:desk={editingDesk} bind:isOpen={createDialogIsOpen} {createNewDesk} />
<DeleteDeskDialog bind:isOpen={deleteDialogIsOpen} {onDelete} />
<EditDeskDialog bind:desk={editingDesk} bind:isOpen={editDialogIsOpen} onSubmit={onEditDesk} />
<DataTable searchText="Filter desks..." searchColumn="name" {data} {columns}>
	{#snippet headerChildren()}
		<Button variant="outline" onclick={openCreateNewDesk}>Add desk</Button>
	{/snippet}
</DataTable>