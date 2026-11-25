<script lang="ts">
	import HealthTimerCard from "../../../../lib/ui/user/dashboard/health_timer/HealthTimerCard.svelte";
	import HeightControlCard from "../../../../lib/ui/user/dashboard/heigh_control/HeightControlCard.svelte";
	import MiniMapCard from "../../../../lib/ui/user/dashboard/mini_map/MiniMapCard.svelte";
	import MySessionCard from "../../../../lib/ui/user/dashboard/my_session/MySessionCard.svelte";
</script>

<div class="grid h-full grid-cols-1 md:grid-cols-2 lg:grid-cols-[1.5fr_1.5fr_2fr] lg:grid-rows-[auto_1fr] gap-4">
	<div><MySessionCard /></div>
	<div><HealthTimerCard /></div>
	<div class="md:col-span-2 lg:col-span-1 lg:row-span-2"><HeightControlCard /></div>
	<div class="md:col-span-2"><MiniMapCard /></div>
</div>