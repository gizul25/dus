<script lang="ts">
    import { Slider } from "#lib/components/ui/slider/index.js";
    import { Button, buttonVariants } from '#lib/components/ui/button/index.js';

    const minHeight = 60;
    const maxHeight = 135;
    const currentHeight = 75;
    let targetHeight = $state(currentHeight);
</script>

<div class="flex flex-col gap-2">
    <div class="flex justify-between">
        <div class="flex-1 text-center">
            <p class="text-sm">Current</p>
            <p class="tabular-nums text-2xl">{currentHeight} cm</p>
        </div>
        <div class="flex-1 text-center">
            <p class="text-sm">Target</p>
            <p class="tabular-nums text-2xl">{targetHeight} cm</p>
        </div>
    </div>
    <div class="px-4">
        <Slider type="single" min={minHeight} max={maxHeight} step={1} bind:value={targetHeight}/>
        <div class="flex justify-between text-xs text-muted-foreground">
            <p>{minHeight}</p>
            <p>{maxHeight}</p>
        </div>
    </div>
    
    <Button class="w-40 self-center">Set Height</Button>
</div>


<!-- When not signed in:
use disabled! -->