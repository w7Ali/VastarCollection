document.addEventListener('DOMContentLoaded', function () {
    function fetchCompanyData() {
      // Fetching data from the API
      fetch('/api/company/')
        .then(response => response.json())
        .then(data => {
          // Update "See it first" section
          document.getElementById('see-it-first').innerHTML = `
            <h3>SEE IT FIRST</h3>
            <form style="display: flex; flex-direction: column; align-items: center;">
              <input maxlength="100" required type="email" placeholder="Enter your email address" style="padding: 8px; margin-bottom: 10px; width: 80%;" />
              <button type="button" style="padding: 10px 20px; background-color: #333; color: white; border: none; cursor: pointer;">JOIN</button>
            </form>
          `;
  
          // Update "Policy" section
          document.getElementById('policy').innerHTML = `
            <h3>Policy</h3>
            <a href="/privacy">Privacy</a>
            <a href="/terms-conditions">Terms & Conditions</a>
            <a href="/refund">Refund Policy</a>
          `;
  
          // Update "About Us" section
          document.getElementById('about-us').innerHTML = `
            <h3>About Us</h3>
            <p>
              Address: ${data.office_address}, ${data.area},<br>
              ${data.city}, ${data.state},<br>
              ${data.pin_code}, ${data.country}
            </p>
          `;
  
          // Update "Contact Us" section
          document.getElementById('contact-us').innerHTML = `
            <h3>Contact Us</h3>
            <p>Phone No: ${data.office_number_1}</p>
            <p>Email: ${data.subscription_email}</p>
          `;
  
          // Update copyright
          document.getElementById('copyright-info').innerHTML = `
            Copyright &copy; ${new Date().getFullYear()} || Designed and Developed By CodeCraft
          `;
        })
        .catch(error => console.error('Error fetching company data:', error));
    }
  
    fetchCompanyData();
  });
  