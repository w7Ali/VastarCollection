// main.js

document.addEventListener('DOMContentLoaded', function () {
    // Common function to fetch company data
    function fetchCompanyData() {
        $.ajax({
            url: '/api/company/',
            type: 'GET',
            success: function (data) {
                // Update footer sections with company data
                $('#see-it-first').html(`
                    <div class="row">
                        <div class="col-12">
                            <h3><i class="fas fa-bell"></i> SEE IT FIRST</h3>
                            <form style="display: flex;">
                                <input maxlength="100" required type="email" placeholder="Enter your email address" name="email" class="email"/>
                                <button type="button" class="btn btn-dark">JOIN</button>
                            </form>
                        </div>
                    </div>
                `);

                $('#about-us').html(`
                    <h3>About Us</h3>
                    <div class="d-flex gap-2">
                        <div><i class="fas fa-map-marker-alt"></i></div>
                        <h6>
                            Address: ${data.office_address}, ${data.area},<br>
                            ${data.city}, ${data.state},<br>
                            ${data.pin_code}, ${data.country}
                        </h6>
                    </div>
                `);

                $('#contact-us').html(`
                    <h3>Contact Us</h3>
                    <div class="d-flex flex-column">
                        <div class="d-flex align-items-center mb-2">
                            <i class="fas fa-phone-alt me-2"></i>
                            <h6 class="mb-0">Phone No: ${data.office_number_1}</h6>
                        </div>
                        <div class="d-flex align-items-center">
                            <i class="fas fa-envelope me-2"></i>
                            <h6 class="mb-0">Email: ${data.subscription_email}</h6>
                        </div>
                    </div>
                `);
                

                $('#copyright-info').html(`
                    Copyright &copy; ${new Date().getFullYear()} || Designed By CodeCraft ||
                `);
            },
            error: function (error) {
                console.log('Error fetching company data:', error);
            }
        });
    }

    // Common function to initialize autocomplete search
    function initializeAutocompleteSearch() {
        let allProducts = window.allProducts || []; // Ensure allProducts is available
        $("#search").autocomplete({
            source: function (request, response) {
                var searchTerm = request.term.toLowerCase();
                var matches = [];
                $.each(allProducts, function (index, product) {
                    if (product.fields.title.toLowerCase().indexOf(searchTerm) !== -1) {
                        matches.push(product.fields.title);
                    }
                });
                response(matches);
            },
            minLength: 2,
            select: function (event, ui) {
                console.log("Selected:", ui.item.value);

                var selectedProduct = allProducts.find(function (product) {
                    return product.fields.title === ui.item.value;
                });

                if (selectedProduct) {
                    var url = "{% url 'product-detail' 0 %}".replace('0', selectedProduct.pk);
                    window.location.href = url;
                }
            }
        });
    }

    // Call common functions
    fetchCompanyData();
    initializeAutocompleteSearch();

    // Logout functionality
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
});
