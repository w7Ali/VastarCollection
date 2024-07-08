// Function to set an address as active
function setActiveAddress(id) {
    if (confirm('Are you sure you want to set this address as active?')) {
      fetch(`/api/address/set-active/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': '{{ csrf_token }}',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ address_id: id })
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          alert('Address set as active successfully.');
          location.reload(); // Reload the page to reflect the active address change
        } else {
          alert('Failed to set address as active.');
        }
      })
      .catch(error => {
        console.error('Error:', error);
        alert('Failed to set address as active.');
      });
    }
  }
  
  
    // Fill the Edit Modal with Address Data
    document.addEventListener('DOMContentLoaded', (event) => {
      const editModal = document.getElementById('editAddressModal');
      editModal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const id = button.getAttribute('data-id');
        const fullName = button.getAttribute('data-full_name');
        const locality = button.getAttribute('data-locality');
        const city = button.getAttribute('data-city');
        const state = button.getAttribute('data-state');
        const zipcode = button.getAttribute('data-zipcode');
  
        const modalTitle = editModal.querySelector('.modal-title');
        modalTitle.textContent = `Edit Address: ${fullName}`;
        const form = editModal.querySelector('form');
        form.setAttribute('action', `/api/address/${id}/update/`);
  
        const fullNameInput = form.querySelector('#id_edit_full_name');
        const localityInput = form.querySelector('#id_edit_locality');
        const cityInput = form.querySelector('#id_edit_city');
        const stateInput = form.querySelector('#id_edit_state');
        const zipcodeInput = form.querySelector('#id_edit_zipcode');
        // const isActiveInput = form.querySelector('#id_edit_is_active');
  
        fullNameInput.value = fullName;
        localityInput.value = locality;
        cityInput.value = city;
        stateInput.value = state;
        zipcodeInput.value = zipcode;
      });
  
      const editForm = document.getElementById('editAddressForm');
      editForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(editForm);
        const id = editForm.getAttribute('action').split('/').slice(-3)[0];
        fetch(`/api/address/${id}/update/`, {
          method: 'PATCH',
          headers: {
            'X-CSRFToken': '{{ csrf_token }}',
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(Object.fromEntries(formData.entries()))
        })
        .then(response => response.json())
        .then(data => {
          if (data.id) {
            location.reload();
          } else {
            alert('Failed to update address');
          }
        })
        .catch(error => console.error('Error:', error));
      });
    });
  
    // Delete Address
    function deleteAddress(id) {
      if (confirm('Are you sure you want to delete this address?')) {
        fetch(`/api/address/${id}/delete/`, {
          method: 'DELETE',
          headers: {
            'X-CSRFToken': '{{ csrf_token }}'
          }
        })
        .then(response => {
          if (response.status === 204) {
            location.reload();
          } else {
            alert('Failed to delete address');
          }
        })
        .catch(error => console.error('Error:', error));
      }
    }