<script lang="ts">
	import * as Tabs from '#lib/components/ui/tabs/index.js';
	import IssuesTab from '#lib/ui/admin/IssuesTab.svelte';
	import MapTab from '#lib/ui/admin/MapTab.svelte';

	import UsersTab from '#lib/ui/admin/users/UsersTab.svelte';
	import DesksTab from '#lib/ui/admin/desks/DesksTab.svelte';

	const tabs = [
		{
			value: 'users',
			title: 'Users',
			component: UsersTab
		},
		{
			value: 'desks',
			title: 'Desks',
			component: DesksTab
		},
		{
			value: 'issues',
			title: 'Issues',
			component: IssuesTab
		},
		{
			value: 'map',
			title: 'Map',
			component: MapTab
		}
	];
</script>

<Tabs.Root value="users">
	<Tabs.List variant="line">
		{#each tabs as tab (tab.value)}
			<Tabs.Trigger value={tab.value}>{tab.title}</Tabs.Trigger>
		{/each}
	</Tabs.List>
	{#each tabs as tab (tab.value)}
		<Tabs.Content value={tab.value} class="p-4">
			<tab.component />
		</Tabs.Content>
	{/each}
</Tabs.Root>
