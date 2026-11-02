<script>
    import { goto } from '$app/navigation'
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
</main>

