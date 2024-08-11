document.addEventListener('DOMContentLoaded', function () {

    // Function to display products in the container
    function displayProducts(products) {
        const productContainer = document.getElementById('search');
        productContainer.innerHTML = '';

        products.forEach(product => {
            const productElement = document.createElement('div');
            productElement.className = 'product';
            productElement.innerHTML = `
                <div class="card mt-5" style="width: 18rem;">
                    <img src="media/${product.product_image}" class="card-img-top" alt="${product.title}" />
                    <div class="card-body">
                        <h4>${product.title}</h4>
                        <p class="card-title">${product.description}</p>
                        <h4 class="card-text">Price: ${product.selling_price}</h4>
                    </div>
                </div>
            `;
            productContainer.appendChild(productElement);
        });
    }

    // Function to initialize autocomplete search
    function initializeAutocompleteSearch() {
        console.log("Initializing autocomplete search...");

        $("#search").autocomplete({
            source: function (request, response) {
                const searchTerm = request.term.toLowerCase();
                const minPrice = $('#min_price').val(); // Assuming you have a field for minimum price
                const maxPrice = $('#max_price').val(); // Assuming you have a field for maximum price

                $.ajax({
                    url: '/api/search/',
                    type: 'GET',
                    data: {
                        name: searchTerm,
                        min_price: minPrice,
                        max_price: maxPrice
                    },
                    success: function (data) {
                        console.log("Data from /api/search:", data);

                        const matches = data.map(product => ({
                            label: product.title,
                            value: product.title,
                            id: product.id // Pass the product id
                        }));

                        response(matches);
                    },
                    error: function (error) {
                        console.log('Error fetching products:', error);
                    }
                });
            },
            minLength: 2,
            select: function (event, ui) {
                console.log("Selected:", ui.item.value);

                const selectedProductId = ui.item.id;
                if (selectedProductId) {
                    const url = `/product-detail/${selectedProductId}`;
                    window.location.href = url;
                }
            }
        });
    }

    // Initialize autocomplete search
    initializeAutocompleteSearch();
});
