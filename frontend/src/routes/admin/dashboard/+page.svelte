<script lang="ts">
	import * as Tabs from '#lib/components/ui/tabs/index.js';
	import DesksTab from '#lib/ui/admin/DesksTab.svelte';
	import IssuesTab from '#lib/ui/admin/IssuesTab.svelte';
	import MapTab from '#lib/ui/admin/MapTab.svelte';

	import UsersTab from '#lib/ui/admin/users/UsersTab.svelte';

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

<Tabs.Root value="users" class="w-full">
	<Tabs.List variant="line">
		{#each tabs as tab (tab.value)}
			<Tabs.Trigger value={tab.value}>{tab.title}</Tabs.Trigger>
		{/each}
	</Tabs.List>
	{#each tabs as tab (tab.value)}
		<Tabs.Content value={tab.value}>
			<tab.component />
		</Tabs.Content>
	{/each}
</Tabs.Root>
