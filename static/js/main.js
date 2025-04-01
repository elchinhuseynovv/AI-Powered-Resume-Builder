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
  
  // File handling
  async function downloadFile(timestamp, fileType) {
    try {
      const response = await fetch(`/download/${timestamp}/${fileType}`);
      if (!response.ok) throw new Error('Download failed');
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `resume_${timestamp}.${fileType}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Download error:', error);
      showAlert('Error downloading file', 'error');
    }
  }
  
  // UI feedback
  function showAlert(message, type = 'success') {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} fade-in`;
    alert.textContent = message;
    
    alertContainer.appendChild(alert);
    setTimeout(() => {
      alert.remove();
    }, 5000);
  }
  
  function updateProgress(value) {
    const progressBar = document.querySelector('.progress-bar');
    if (!progressBar) return;
    
    progressBar.style.width = `${value}%`;
  }
  
  // Form submission
  document.getElementById('resumeForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    const errors = validateForm(formData);
    
    if (errors.length > 0) {
      errors.forEach(error => showAlert(error, 'error'));
      return;
    }
    
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.innerHTML = '<div class="spinner"></div>';
    
    try {
      updateProgress(30);
      const response = await fetch('/create_resume', {
        method: 'POST',
        body: formData
      });
      
      updateProgress(60);
      const data = await response.json();
      
      if (data.success) {
        updateProgress(100);
        showAlert('Resume created successfully!');
        displayResults(data);
      } else {
        throw new Error(data.message);
      }
    } catch (error) {
      showAlert(error.message, 'error');
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = originalText;
    }
  });
  
  // Initialize real-time preview
  document.querySelectorAll('#resumeForm input, #resumeForm textarea')?.forEach(input => {
    input.addEventListener('input', (e) => {
      const form = e.target.form;
      if (form) {
        updatePreview(new FormData(form));
      }
    });
  });