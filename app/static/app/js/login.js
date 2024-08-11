document.getElementById('logout-link')?.addEventListener('click', function (event) {
    event.preventDefault();
    fetch("{% url 'logout' %}", {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}',
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'csrfmiddlewaretoken': '{{ csrf_token }}',
        }),
    }).then(response => {
        if (response.ok) {
            window.location.href = "{% url 'login' %}";
        } else {
            console.error('Logout request failed');
        }
    }).catch(error => {
        console.error('Error during logout request:', error);
    });
});