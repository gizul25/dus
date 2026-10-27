<script lang="ts">
	import DataTable from '../table/DataTable.svelte';
	import AddUserDialog from './AddUserDialog.svelte';
	import { columns, type User } from './columns.js';
	import DeleteUserDialog from './DeleteUserDialog.svelte';
	import { setContext } from 'svelte';
	import EditUserDialog from './EditUserDialog.svelte';
	import { Button } from '#lib/components/ui/button/index.js';

	let data: User[] = $state([
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
		}
		// ...[...Array(25).keys()].map((_) => ({
		// 	id: '489e1d42',
		// 	firstName: 'Purely',
		// 	lastName: 'Surely',
		// 	email: 'psurely@gmail.com'
		// }))
	]);

	let editingUser: User = $state({
		firstName: '',
		lastName: '',
		email: ''
	});
	let createDialogIsOpen = $state(false);
	let deleteDialogIsOpen = $state(false);
	let editDialogIsOpen = $state(false);

	function openCreateNewUser() {
		console.log('openCreateNewUser');
		editingUser = {
			firstName: '',
			lastName: '',
			email: ''
		};
		createDialogIsOpen = true;
	}

	function openEditUserDetails(id: string) {
		console.log('openEditUserDetails', id);
		editingUser = data.find((u) => u.id === id);
		editDialogIsOpen = true;
	}

	function openDeleteUser(id: string) {
		console.log('openDeleteUser', id);
		editingUser = data.find((u) => u.id === id);
		deleteDialogIsOpen = true;
	}

	function createNewUser(user: User) {
		data = [
			...data,
			{
				...user,
				id: '127312391'
			}
		];
		return true;
	}

	function onEditUser(newUser) {
		let userEntry = data.find((u) => u.id === newUser.id);
		userEntry = newUser;
		data = [...data];
		return true;
	}

	function onDelete() {
		data = data.filter((u) => u.id !== editingUser.id);
	}

	setContext('userContext', {
		openCreateNewUser,
		openEditUserDetails,
		openDeleteUser
	});
</script>

<AddUserDialog bind:user={editingUser} bind:isOpen={createDialogIsOpen} {createNewUser} />
<DeleteUserDialog bind:isOpen={deleteDialogIsOpen} {onDelete} />
<EditUserDialog bind:user={editingUser} bind:isOpen={editDialogIsOpen} onSubmit={onEditUser} />
<DataTable searchText="Filter emails..." searchColumn="email" {data} {columns}>
	{#snippet headerChildren()}
		<Button variant="outline" onclick={openCreateNewUser}>Add user</Button>
	{/snippet}
</DataTable>
