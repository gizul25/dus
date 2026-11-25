<script lang="ts">
	import * as Dialog from '#lib/components/ui/dialog/index.js';
	import * as Field from '#lib/components/ui/field/index.js';
	import { Button, buttonVariants } from '#lib/components/ui/button/index.js';
	import { Input } from '#lib/components/ui/input/index.js';
	import { Label } from '#lib/components/ui/label/index.js';


    let { open = $bindable() } = $props();
	async function onSubmit() {
        // change profile
	}
</script>

<Dialog.Root bind:open>
	<form>
		<Dialog.Content class="sm:max-w-sm">
			<Dialog.Header>
				<Dialog.Title>Edit profile</Dialog.Title>
			</Dialog.Header>
			<Field.Group>
				<Field.Field>
					<Label for="profile-name">Profile name</Label>
					<Input id="profile-name" type="string" />
				</Field.Field>
				<Field.Field>
					<Label for="profile-height">Profile height</Label>
					<Input id="profile-height" type="number" />
				</Field.Field>
			</Field.Group>
			<Dialog.Footer>
				<Dialog.Close type="button" class={buttonVariants({ variant: 'outline' })}>
					Cancel
				</Dialog.Close>
				<Button type="submit" onclick={onSubmit}>Save</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</form>
</Dialog.Root>
