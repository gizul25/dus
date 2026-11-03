<script>
    import { goto } from '$app/navigation'
    import * as Card from '#lib/components/ui/card/index.ts';
    import { Input } from '#lib/components/ui/input/index.ts';
    import { Label } from '#lib/components/ui/label/index.ts';
    import { Checkbox } from '#lib/components/ui/checkbox/index.ts';
    import { Button } from '#lib/components/ui/button/index.ts';
	import { Description } from '#lib/components/ui/alert-dialog/index.ts';

    let email = $state('');
    let password = $state('');
    let rememberMe = $state(false);
    let errorMessage = $state('');


    async function handleLogin(event) {
        event.preventDefault();
        errorMessage = '';

        try {
            const response = await fetch('http://localhost:8000/auth/login', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    password: password,
                    remember_me: rememberMe
                    })
            });

            const data = await response.json();

            if (!response.ok) {
                errorMessage = data.detail || "Login unsuccessful";
                return;
            }

            console.log('Login successful', data)
            await goto('/test/login');
        }

        catch (error) {
            errorMessage = error.message;
            console.error('Error:', error);

            // errorMessage = "Could not connect to the server";
            // console.error(error);
        }
    }
    
</script>

<main class="flex min-h-screen items-center justify-center">
    <Card.Root class="w-full max-w-md">
        <Card.Header>
            <Card.Title>
                Log In
            </Card.Title>
            <Card.Description>
                Enter your credentials
            </Card.Description>
        </Card.Header>
        <Card.Content>
            <form onsubmit={handleLogin}>
                <Label for="email">Email</Label>
                <Input id="email" type="email" required bind:value={email} />

                <Label for="password">Password</Label>
                <Input id="password" type="password" required bind:value={password} />

                
                <Label for="rememberMe"> 
                    <Checkbox id="rememberMe" bind:checked={rememberMe} />
                    Remember me
                </Label>

                <Button type="submit">Login</Button>


            </form>
        </Card.Content>
    </Card.Root>
</main>

<!-- 
<main>
    <h1 class="text-3xl">Login</h1>

    {#if errorMessage}
        <p class="error">{errorMessage}</p>
    {/if}

    <form onsubmit={handleLogin}>
        <label for="email">Email</label>
        <input id="email" type="email" required bind:value={email} />

        <label for="password">Password</label>
        <input id="password" type="password" required bind:value={password}/>

        <input type="checkbox" id="rememberMe" name="rememberMe" bind:checked={rememberMe}/>
        <label for="rememberMe">Remember Me</label>

        <button type="submit">Login</button>

    </form>
</main> -->

