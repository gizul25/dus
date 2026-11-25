<script lang="ts">
    import * as Select from '#lib/components/ui/select/index.js';


	const statuses = [
		{ value: "online", label: "Online" },
		{ value: "do-not-disturb", label: "Do not disturb" },
		{ value: "away", label: "Away" },
		{ value: "offline", label: "Offline" },
	];

	let value = $state("");

</script>

<Select.Root type="single">
 <Select.Trigger class="w-[180px]">
  <Select.Value placeholder="Select a theme" />
 </Select.Trigger>
 <Select.Content>
    {#each statuses as status (status.value)}
				<Select.Item value={status.value} label={status.label}>
					{status.label}
				</Select.Item>
			{/each}
 </Select.Content>
</Select.Root>