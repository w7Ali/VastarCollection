<script>
  $(document).ready(function() {
    // Fetch company information using AJAX
    $.ajax({
      url: '/api/company/',
      type: 'GET',
      success: function (data) {
        // Update 'SEE IT FIRST' section with Font Awesome icon
        $('#see-it-first').html(`
          <div class="max-sm:mb-3">
            <h3><i class="fas fa-bell"></i> SEE IT FIRST</h3>
            <form>
              <input
                maxlength="100"
                required
                type="email"
                placeholder="Enter your email address"
                name="email"
                class="email"/><button type="button" class="btn btn-dark">
                JOIN
              </button>
            </form>
            <div>
              <a href="#" style="color: black">
                <h5><u>PRIVACY POLICY</u></h5>
              </a>
            </div>
          </div>
        `);

        // Update 'About Us' section with Font Awesome icon
        $('#about-us').html(`
          <h3><i class="fas fa-building"></i> About Us</h3>
          <div>
            <h5><i class="fas fa-map-marker-alt"></i> Address: ${data.office_address}, ${data.area}, ${data.city}, ${data.state}, ${data.pin_code}, ${data.country}</h5>
          </div>
        `);

        // Update 'Contact Us' section with Font Awesome icon
        $('#contact-us').html(`
          <h3><i class="fas fa-phone"></i> Contact Us</h3>
          <div>
            <h5><i class="fas fa-phone-alt"></i> Phone No: ${data.office_number_1}</h5>
          </div>
        `);

        // Update copyright information
        $('#copyright-info').html(`
          Copyright &copy; ${new Date().getFullYear()} || Designed By CodeCraft ||
        `);
      },
      error: function (error) {
        console.log('Error fetching company data:', error);
      }
    })});
</script>