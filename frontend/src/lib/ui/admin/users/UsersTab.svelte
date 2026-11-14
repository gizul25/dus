<script lang="ts">
	import DataTable from '../table/DataTable.svelte';
	import AddUserDialog from './AddUserDialog.svelte';
	import { columns } from './columns.js';
	import DeleteUserDialog from './DeleteUserDialog.svelte';
	import { setContext } from 'svelte';
	import EditUserDialog from './EditUserDialog.svelte';
	import { Button } from '#lib/components/ui/button/index.js';
	import { createUser, deleteUser, getUsers, updateUser, type User } from '#lib/api/admin/users.js';

	let data: User[] | null = $state(null);

	let editingUser: User | null = $state(null);
	let createDialogIsOpen = $state(false);
	let deleteDialogIsOpen = $state(false);
	let editDialogIsOpen = $state(false);

	function openCreateNewUser() {
		console.log('openCreateNewUser');
		editingUser = {
			firstName: '',
			lastName: '',
			email: '',
			password: '',
			role: 'user'
		};
		createDialogIsOpen = true;
	}

	function openEditUserDetails(id: string) {
		console.log('openEditUserDetails', id);
		editingUser = data!.find((u) => u.id === id);
		editDialogIsOpen = true;
	}

	function openDeleteUser(id: string) {
		console.log('openDeleteUser', id);
		editingUser = data!.find((u) => u.id === id);
		deleteDialogIsOpen = true;
	}

	async function createNewUser(user: User) {
		await createUser(user);
		data = await getUsers();
		return true;
	}

	async function onEditUser(newUser: User) {
		await updateUser(newUser);
		data = await getUsers();
		return true;
	}

	async function onDelete() {
		await deleteUser(editingUser!.id);
		data = await getUsers();
	}

	$effect(async () => {
		data = await getUsers();
	});

	setContext('actionContext', {
		openCreateNewUser,
		openEditUserDetails,
		openDeleteUser
	});
</script>

{#if data !== null}
	<AddUserDialog bind:user={editingUser} bind:isOpen={createDialogIsOpen} {createNewUser} />
	<DeleteUserDialog bind:isOpen={deleteDialogIsOpen} {onDelete} />
	<EditUserDialog bind:user={editingUser} bind:isOpen={editDialogIsOpen} onSubmit={onEditUser} />
	<DataTable searchText="Filter emails..." searchColumn="email" {data} {columns}>
		{#snippet headerChildren()}
			<Button variant="outline" onclick={openCreateNewUser}>Add user</Button>
		{/snippet}
	</DataTable>
{:else}
	<p>Loading...</p>
{/if}
