<script lang="ts">
	import * as Sidebar from '#lib/components/ui/sidebar/index.js';
	import * as DropdownMenu from '#lib/components/ui/dropdown-menu/index.js';
	import { goto } from '$app/navigation';
	import PasswordChangeDialog from './PasswordChangeDialog.svelte';
	import SidebarGroupContent from '#lib/components/ui/sidebar/sidebar-group-content.svelte';
    import { RiDashboardLine, RiMap2Line, RiBarChartBoxLine, RiErrorWarningLine, RiUser3Line } from "remixicon-svelte";

	let errorMessage = $state('');
	let passwordDialogOpen = $state(false);
	let { user } = $props();

	async function handleLogout() {
		try {
			const response = await fetch('/api/auth/logout', {
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

<Sidebar.Root collapsible="icon" variant="inset">
	<Sidebar.Header />
		<Sidebar.Content>
			<Sidebar.Group>
				<Sidebar.Menu>

					<Sidebar.MenuItem>
						<Sidebar.MenuButton>
							{#snippet child({ props })}
								<a href="/dashboard" {...props}>
									<RiDashboardLine />
									<span>Dashboard</span>
								</a>
							{/snippet}
						</Sidebar.MenuButton>
					</Sidebar.MenuItem>

					<Sidebar.MenuItem>
						<Sidebar.MenuButton>
							{#snippet child({ props })}
								<a href="/map" {...props}>
									<RiMap2Line />
									<span>Map</span>
								</a>
							{/snippet}
						</Sidebar.MenuButton>
					</Sidebar.MenuItem>

					<Sidebar.MenuItem>
						<Sidebar.MenuButton>
							{#snippet child({ props })}
								<a href="/statistics" {...props}>
									<RiBarChartBoxLine />
									<span>Statistics</span>
								</a>
							{/snippet}
						</Sidebar.MenuButton>
					</Sidebar.MenuItem>

					<Sidebar.MenuItem>
						<Sidebar.MenuButton>
							{#snippet child({ props })}
								<a href="/issues" {...props}>
									<RiErrorWarningLine />
									<span>Issues</span>
								</a>
							{/snippet}
						</Sidebar.MenuButton>
					</Sidebar.MenuItem>

				</Sidebar.Menu>
			</Sidebar.Group>
		</Sidebar.Content>


	<Sidebar.Footer>
		<DropdownMenu.Root>
			<DropdownMenu.Trigger>
				{#snippet child({ props })}
					<Sidebar.MenuButton {...props}>
						<RiUser3Line />
                        <span>{user.first_name} {user.last_name}</span>
					</Sidebar.MenuButton>
				{/snippet}
			</DropdownMenu.Trigger>
			<DropdownMenu.Content>
				<DropdownMenu.Group>
					<DropdownMenu.Item onclick={() => (passwordDialogOpen = true)}>Change password</DropdownMenu.Item>
					<DropdownMenu.Item onclick={handleLogout} variant="destructive">Log out</DropdownMenu.Item>
				</DropdownMenu.Group>
			</DropdownMenu.Content>
		</DropdownMenu.Root>
	</Sidebar.Footer>
</Sidebar.Root>

<PasswordChangeDialog bind:open={passwordDialogOpen} />
