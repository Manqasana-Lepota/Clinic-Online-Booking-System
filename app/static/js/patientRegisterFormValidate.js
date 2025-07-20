document.addEventListener('DOMContentLoaded', () => {
    const dobInput = document.querySelector('input[name="DateOfBirth"]');
    const ageInput = document.querySelector('input[name="age"]');
    const nationalIdInput = document.querySelector('input[name="national_id"]');
    const contactInput = document.querySelector('input[name="contact"]');
   

    // Calculate age based on DOB and set Age input
    function calculateAge(dobValue) {
      const dob = new Date(dobValue);
      const today = new Date();

      let age = today.getFullYear() - dob.getFullYear();
      const m = today.getMonth() - dob.getMonth();

      if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) {
        age--;
      }

      return age >= 0 ? age : '';
    }

    // Format DOB as YYMMDD for National ID prefix
    function formatDOBtoYYMMDD(dateStr) {
      const date = new Date(dateStr);
      if (isNaN(date)) return '';
      const year = date.getFullYear().toString().slice(-2);
      const month = ('0' + (date.getMonth() + 1)).slice(-2);
      const day = ('0' + date.getDate()).slice(-2);
      return year + month + day;
    }

    // When DOB changes, update Age and National ID prefix
    dobInput.addEventListener('change', () => {
      // Update Age
      ageInput.value = calculateAge(dobInput.value);

      // Update National ID first 6 digits
      const prefix = formatDOBtoYYMMDD(dobInput.value);
      if (prefix) {
        let suffix = nationalIdInput.value.slice(6) || '';
        suffix = suffix.replace(/\D/g, '').slice(0, 7);
        nationalIdInput.value = prefix + suffix;
      } else {
        nationalIdInput.value = '';
      }
    });

    // Prevent editing first 6 digits of National ID manually
    nationalIdInput.addEventListener('keydown', (e) => {
      if (nationalIdInput.selectionStart < 6) {
        if (e.key !== 'Backspace' && e.key !== 'Delete' && !e.ctrlKey && !e.metaKey) {
          e.preventDefault();
        }
      }
    });

    // Allow only digits in National ID and max length 13
    nationalIdInput.addEventListener('input', () => {
      let val = nationalIdInput.value;
      val = val.replace(/\D/g, '');
      const fixedPart = val.slice(0, 6);
      const userPart = val.slice(6, 13);
      nationalIdInput.value = fixedPart + userPart;
    });

    contactInput.addEventListener('input', () => {
      // Remove non-digit characters
      let val = contactInput.value.replace(/\D/g, '');
      // Limit to max 10 digits
      if (val.length > 10) val = val.slice(0, 10);
      contactInput.value = val;
    });
  });
  