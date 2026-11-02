<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	let user = $state(null);
	let errorMessage = $state('');

	onMount(async () => {
		try {
			const response = await fetch('http://localhost:8000/auth/me', { credentials: 'include' });

			const data = await response.json();

			if (!response.ok) {
				errorMessage = data.detail || 'Could not authenticate';
				return;
			}

			user = data;
		} catch (error) {
			errorMessage = 'Could not connect to the server';
		}
	});

	async function handleLogout() {
		try {
			const response = await fetch('http://localhost:8000/auth/logout', {
				method: 'POST',
				credentials: 'include'
			});

			if (!response.ok) {
				errorMessage = 'Logout unsuccessful';
				return;
			}

			await goto('/login');
		} catch (error) {
			errorMessage = 'Could not connect to the server';
		}
	}
</script>

<main>
	<h1>My Page</h1>
	{#if user}
		<p>Welcome, {user.fname} {user.lname}!</p>
		<p>Role: {user.role}</p>
	{:else if errorMessage}
		<p>{errorMessage}</p>
	{:else}
		<p>loading</p>
	{/if}

	<button onclick={handleLogout}>Logout</button>
</main>
