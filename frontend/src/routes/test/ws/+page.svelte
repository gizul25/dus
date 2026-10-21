<script>
    let text = $state("");

	var ws = new WebSocket('ws://localhost:7000/ws');
	ws.onmessage = function (event) {
        console.log('onmessage', event)
	};

	function sendMessage() {
		ws.send(text);
	}
</script>

<input bind:value={text} />
<button onclick={sendMessage}>Send message</button>