<script lang="ts">
 import type { ComponentProps } from "svelte";
 import ArrowUpDownIcon from "remixicon-svelte/icons/arrow-up-down-line";
 import { Button } from "#lib/components/ui/button/index.js";
 
 let { variant = "ghost", ...restProps }: ComponentProps<typeof Button> =
  $props();
</script>
 
<Button {variant} {...restProps}>
 Email
 <ArrowUpDownIcon class="ms-2 size-4" />
</Button>