
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

              $('#policy').html(`
                <h3>Policy</h3>
                <div class="d-flex flex-column">
                      <div class="d-flex align-items-center mb-2">
                       <i class="fas fa-user-shield"></i>
                        <h6>
                         <a href="/privacy" style="text-decoration:none;color:black;">Conditions</a><br>
                        </h6>
                        </div>
                    <div class="d-flex align-items-center">
                      <i class="fas fa-file-contract"></i>
                    <h6>
                        <a href="/terms-conditions" style="text-decoration:none;color:black;">Privacy</a>
                    </h6>
                    </div>
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
                  Copyright &copy; ${new Date().getFullYear()} || Designed and Developed By CodeCraft 
              `);
          },
          error: function (error) {
              console.log('Error fetching company data:', error);
          }
      });
  }
  fetchCompanyData();
});
