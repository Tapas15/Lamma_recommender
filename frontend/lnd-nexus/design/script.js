// L&D Nexus - Professional Redesign
// Main JavaScript File

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');
    
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            navLinks.classList.toggle('active');
            this.classList.toggle('active');
        });
    }
    
    // Testimonial slider functionality
    const testimonialSlider = document.querySelector('.testimonials-slider');
    const testimonialCards = document.querySelectorAll('.testimonial-card');
    const dots = document.querySelectorAll('.dot');
    
    if (testimonialSlider && testimonialCards.length > 0 && dots.length > 0) {
        let currentSlide = 0;
        
        // Function to update slider position
        function updateSlider() {
            testimonialSlider.style.transform = `translateX(-${currentSlide * 100}%)`;
            
            // Update active dot
            dots.forEach((dot, index) => {
                dot.classList.toggle('active', index === currentSlide);
            });
        }
        
        // Add click event to dots
        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => {
                currentSlide = index;
                updateSlider();
            });
        });
        
        // Auto-rotate testimonials every 5 seconds
        setInterval(() => {
            currentSlide = (currentSlide + 1) % testimonialCards.length;
            updateSlider();
        }, 5000);
    }
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            
            if (target) {
                e.preventDefault();
                
                window.scrollTo({
                    top: target.offsetTop - 100,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add animation on scroll
    const animateElements = document.querySelectorAll('.feature-card, .professional-card, .job-card, .resource-card, .pricing-card');
    
    function checkScroll() {
        animateElements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if (elementTop < windowHeight - 100) {
                element.classList.add('animate');
            }
        });
    }
    
    // Initial check
    checkScroll();
    
    // Check on scroll
    window.addEventListener('scroll', checkScroll);
});
