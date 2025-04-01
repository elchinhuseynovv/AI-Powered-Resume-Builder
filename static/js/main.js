// Form validation
function validateForm(formData) {
    const errors = [];
    
    // Required fields
    const requiredFields = ['name', 'email', 'phone', 'job_title', 'company', 'education', 'experience', 'skills'];
    requiredFields.forEach(field => {
      if (!formData.get(field)) {
        errors.push(`${field.replace('_', ' ')} is required`);
      }
    });
    
    // Email validation
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(formData.get('email'))) {
      errors.push('Invalid email format');
    }
    
    // Phone validation
    const phoneDigits = formData.get('phone').replace(/\D/g, '');
    if (phoneDigits.length < 10) {
      errors.push('Phone number must have at least 10 digits');
    }
    
    return errors;
  }
  
  // Resume preview
  function updatePreview(formData) {
    const previewElement = document.getElementById('resume-preview');
    if (!previewElement) return;
    
    const data = Object.fromEntries(formData.entries());
    const skills = data.skills.split(',').map(skill => skill.trim());
    
    previewElement.innerHTML = `
      <div class="resume-section">
        <h1 class="text-2xl font-bold">${data.name}</h1>
        <p class="text-gray-600">${data.email} | ${data.phone}</p>
        <p class="text-gray-600">${data.job_title}</p>
      </div>
      
      <div class="resume-section">
        <h2 class="resume-section-title">Education</h2>
        <p>${data.education}</p>
      </div>
      
      <div class="resume-section">
        <h2 class="resume-section-title">Experience</h2>
        <p>${data.experience}</p>
      </div>
      
      <div class="resume-section">
        <h2 class="resume-section-title">Skills</h2>
        <div class="flex flex-wrap gap-2">
          ${skills.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
        </div>
      </div>
    `;
  }