<script lang="ts">
	import { Button } from '#lib/components/ui/button/index.js';
	import { setContext } from 'svelte';
	import DataTable from '#lib/ui/admin/table/DataTable.svelte';
	import AddDeskDialog from './AddDeskDialog.svelte';
	import DeleteDeskDialog from './DeleteDeskDialog.svelte';
	import EditDeskDialog from './EditDeskDialog.svelte';
	import { columns } from './columns.js';
	import { createDesk, deleteDesk, getDesks, updateDesk, type Desk } from '#lib/api/admin/desks.js';

	let data: Desk[] | null = $state(null);

	let editingDesk: Desk | null = $state(null);
	let createDialogIsOpen = $state(false);
	let deleteDialogIsOpen = $state(false);
	let editDialogIsOpen = $state(false);

	function openCreateNewDesk() {
		console.log('openCreateNewDesk');
		editingDesk = {
			name: ''
		};
		createDialogIsOpen = true;
	}

	function openEditDeskDetails(id: string) {
		console.log('openEditDeskDetails', id, data);
		editingDesk = data!.find((u) => u.id === id);
		editDialogIsOpen = true;
	}

	function openDeleteDesk(id: string) {
		console.log('openDeleteDesk', id);
		editingDesk = data!.find((u) => u.id === id);
		deleteDialogIsOpen = true;
	}

	async function createNewDesk(desk: Desk) {
		await createDesk(desk);
		data = await getDesks();
		return true;
	}

	async function onEditDesk(newDesk: Desk) {
		await updateDesk(newDesk);
		data = await getDesks();
		return true;
	}

	async function onDelete() {
		await deleteDesk(editingDesk!.id);
		data = await getDesks();
	}

	$effect(async () => {
		data = await getDesks();
	})

	setContext('actionContext', {
		openCreateNewDesk,
		openEditDeskDetails,
		openDeleteDesk
	});
</script>

{#if data !== null}
	<AddDeskDialog bind:desk={editingDesk} bind:isOpen={createDialogIsOpen} {createNewDesk} />
	<DeleteDeskDialog bind:isOpen={deleteDialogIsOpen} {onDelete} />
	<EditDeskDialog bind:desk={editingDesk} bind:isOpen={editDialogIsOpen} onSubmit={onEditDesk} />
	<DataTable searchText="Filter desks..." searchColumn="name" {data} {columns}>
		{#snippet headerChildren()}
			<Button variant="outline" onclick={openCreateNewDesk}>Add desk</Button>
		{/snippet}
	</DataTable>
{:else}
	<p>Loading...</p>
{/if}
