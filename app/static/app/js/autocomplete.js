
$(document).ready(function () {

    // Function to display suggestions
    function displaySuggestions(suggestions) {
        const suggestionsBox = $('#suggestions');
        suggestionsBox.empty(); // Clear existing suggestions

        if (suggestions.length === 0) {
            suggestionsBox.hide();
            return;
        }

        suggestions.forEach(suggestion => {
            const item = $('<div class="suggestion-item"></div>');
            item.text(suggestion.label);
            item.on('click', function () {
                $('#search').val(suggestion.label);
                window.location.href = `/product-detail/${suggestion.id}`;
                suggestionsBox.hide();
            });
            suggestionsBox.append(item);
        });

        suggestionsBox.show();
    }

    // Initialize autocomplete search
    $('#search').on('input', function () {
        const searchTerm = $(this).val().toLowerCase();

        if (searchTerm.length < 2) {
            $('#suggestions').hide();
            return;
        }

        $.ajax({
            url: '/api/search/',
            type: 'GET',
            data: {
                name: searchTerm
            },
            success: function (data) {
                const matches = data.map(product => ({
                    label: product.title,
                    value: product.title,
                    id: product.id
                }));
                displaySuggestions(matches);
            },
            error: function (error) {
                console.log('Error fetching products:', error);
            }
        });
    });

    // Hide suggestions box when clicking outside
    $(document).on('click', function (e) {
        if (!$(e.target).closest('#search').length) {
            $('#suggestions').hide();
        }
    });

    // Adjust the position of the suggestions box
    $('#search').on('focus', function () {
        $('#suggestions').show();
    });

});

