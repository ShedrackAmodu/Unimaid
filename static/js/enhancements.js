/**
 * Enhanced Main JavaScript
 * Ramat Library Unimaid - Modern improvements to main.js
 * Includes better error handling, event delegation, and performance optimization
 */

(function ($) {
  'use strict';

  // ========================================
  // 1. Utility Functions
  // ========================================

  /**
   * Debounce function to limit function calls during rapid events
   */
  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  /**
   * Throttle function to limit function calls over time
   */
  function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }

  /**
   * Check if element is in viewport
   */
  function isInViewport(el) {
    const rect = el.getBoundingClientRect();
    return (
      rect.top >= 0 &&
      rect.left >= 0 &&
      rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
      rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
  }

  // ========================================
  // 2. Sticky Header
  // ========================================
  const stickyHeaderInit = function() {
    const $header = $('#sticky-header');
    const $backTop = $('#back-top');
    
    if (!$header.length) return;

    $(window).on('scroll', throttle(function () {
      const scroll = $(window).scrollTop();
      
      if (scroll < 400) {
        $header.removeClass('sticky');
        $backTop.fadeOut(300);
      } else {
        $header.addClass('sticky');
        $backTop.fadeIn(300);
      }
    }, 100));
  };

  // ========================================
  // 3. Mobile Menu
  // ========================================
  const mobileMenuInit = function() {
    const menu = $('ul#navigation');
    
    if (!menu.length) return;
    
    try {
      menu.slicknav({
        prependTo: '.mobile_menu',
        closedSymbol: '+',
        openedSymbol: '-'
      });
    } catch (e) {
      console.warn('SlickNav plugin not available:', e);
    }
  };

  // ========================================
  // 4. Carousel Initialization
  // ========================================
  const carouselsInit = function() {
    // Slider Active
    if ($('.slider_active').length) {
      try {
        $('.slider_active').owlCarousel({
          loop: true,
          margin: 0,
          items: 1,
          autoplay: true,
          navText: ['<i class="flaticon-left-arrow"></i>', '<i class="flaticon-right-arrow"></i>'],
          nav: true,
          dots: false,
          autoplayHoverPause: true,
          autoplaySpeed: 800,
          responsive: {
            0: { items: 1, nav: false },
            767: { items: 1, nav: false },
            992: { items: 1, nav: false },
            1200: { items: 1, nav: false },
            1600: { items: 1, nav: true }
          }
        });
      } catch (e) {
        console.warn('Owl Carousel not available:', e);
      }
    }

    // Brand Active
    if ($('.brand-active').length) {
      try {
        $('.brand-active').owlCarousel({
          loop: true,
          margin: 30,
          items: 1,
          autoplay: true,
          nav: false,
          dots: false,
          autoplayHoverPause: true,
          autoplaySpeed: 800,
          responsive: {
            0: { items: 1, nav: false },
            767: { items: 4 },
            992: { items: 7 }
          }
        });
      } catch (e) {
        console.warn('Brand Carousel not available:', e);
      }
    }

    // Project Active
    if ($('.project-active').length) {
      try {
        $('.project-active').owlCarousel({
          loop: true,
          margin: 30,
          items: 1,
          navText: ['<i class="Flaticon flaticon-left-arrow"></i>', '<i class="Flaticon flaticon-left-arrow"></i>'],
          nav: true,
          dots: false,
          responsive: {
            0: { items: 1, nav: false },
            767: { items: 1, nav: false },
            992: { items: 2, nav: false },
            1200: { items: 1 },
            1501: { items: 2 }
          }
        });
      } catch (e) {
        console.warn('Project Carousel not available:', e);
      }
    }

    // Details Active
    if ($('.details_active').length) {
      try {
        $('.details_active').owlCarousel({
          loop: true,
          margin: 0,
          items: 1,
          navText: ['<i class="ti-angle-left"></i>', '<i class="ti-angle-right"></i>'],
          nav: true,
          dots: false,
          responsive: {
            0: { items: 1, nav: false },
            767: { items: 1, nav: false },
            992: { items: 1, nav: false },
            1200: { items: 1 }
          }
        });
      } catch (e) {
        console.warn('Details Carousel not available:', e);
      }
    }
  };

  // ========================================
  // 5. Isotope Grid Filter
  // ========================================
  const isotopeInit = function() {
    if (!$('.grid').length) return;
    
    try {
      const $grid = $('.grid').isotope({
        itemSelector: '.grid-item',
        percentPosition: true,
        masonry: { columnWidth: 1 }
      });

      $('.portfolio-menu').on('click', 'button', function () {
        const filterValue = $(this).attr('data-filter');
        $grid.isotope({ filter: filterValue });
      });

      $('.portfolio-menu button').on('click', function (event) {
        $(this).siblings('.active').removeClass('active');
        $(this).addClass('active');
        event.preventDefault();
      });
    } catch (e) {
      console.warn('Isotope plugin not available:', e);
    }
  };

  // ========================================
  // 6. WOW Animation
  // ========================================
  const wowInit = function() {
    try {
      new WOW().init();
    } catch (e) {
      console.warn('WOW plugin not available:', e);
    }
  };

  // ========================================
  // 7. Counter Up Animation
  // ========================================
  const counterInit = function() {
    if (!$('.counter').length) return;
    
    try {
      $('.counter').counterUp({
        delay: 10,
        time: 10000
      });
    } catch (e) {
      console.warn('CounterUp plugin not available:', e);
    }
  };

  // ========================================
  // 8. Magnificent Popup
  // ========================================
  const magnificPopupInit = function() {
    try {
      // Image popup
      $('.popup-image').magnificPopup({
        type: 'image',
        gallery: { enabled: true }
      });

      $('.img-pop-up').magnificPopup({
        type: 'image',
        gallery: { enabled: true }
      });

      // Video popup
      $('.popup-video').magnificPopup({
        type: 'iframe'
      });

      // Form popup
      $('.popup-with-form').magnificPopup({
        type: 'inline',
        preloader: false,
        focus: '#name',
        callbacks: {
          beforeOpen: function() {
            this.st.focus = $(window).width() < 700 ? false : '#name';
          }
        }
      });
    } catch (e) {
      console.warn('Magnificent Popup plugin not available:', e);
    }
  };

  // ========================================
  // 9. Smooth Scroll
  // ========================================
  const smoothScrollInit = function() {
    try {
      $.scrollIt({
        upKey: 38,
        downKey: 40,
        easing: 'linear',
        scrollTime: 600,
        activeClass: 'active',
        topOffset: 0
      });

      $.scrollUp({
        scrollName: 'scrollUp',
        topDistance: '4500',
        topSpeed: 300,
        animation: 'fade',
        animationInSpeed: 200,
        animationOutSpeed: 200,
        scrollText: '<i class="fa fa-angle-double-up"></i>',
        activeOverlay: false
      });
    } catch (e) {
      console.warn('Scroll plugins not available:', e);
    }
  };

  // ========================================
  // 10. Nice Select
  // ========================================
  const niceSelectInit = function() {
    if (document.getElementById('default-select') && typeof $ !== 'undefined') {
      try {
        $('select').niceSelect();
      } catch (e) {
        console.warn('Nice Select plugin not available:', e);
      }
    }
  };

  // ========================================
  // 11. Search Toggle
  // ========================================
  const searchToggleInit = function() {
    const $searchBox = $('#search_input_box');
    
    if (!$searchBox.length) return;
    
    $searchBox.hide();

    $('#search, #search_1').on('click', function () {
      $searchBox.slideToggle(300);
      $('#search_input').focus();
    });

    $('#close_search').on('click', function () {
      $searchBox.slideUp(300);
    });

    // Close search on ESC key
    $(document).on('keydown', function(e) {
      if (e.keyCode === 27) {
        $searchBox.slideUp(300);
      }
    });
  };

  // ========================================
  // 12. Mailchimp Integration
  // ========================================
  const mailchimpInit = function() {
    if ($('#mc_embed_signup').length) {
      try {
        $('#mc_embed_signup').find('form').ajaxChimp();
      } catch (e) {
        console.warn('AjaxChimp not available:', e);
      }
    }
  };

  // ========================================
  // 13. Contact Form Validation
  // ========================================
  const contactFormInit = function() {
    try {
      // Auto-initialize jQuery validation if plugin exists
      if ($.fn.validate) {
        $('form').validate({
          errorElement: 'span',
          errorClass: 'form-error',
          onfocusout: function(element) {
            $(element).valid();
          }
        });
      }
    } catch (e) {
      console.warn('Form validation not available:', e);
    }
  };

  // ========================================
  // 14. Performance Monitoring
  // ========================================
  const performanceMonitor = function() {
    if (window.performance && window.performance.timing) {
      window.addEventListener('load', function() {
        const perf = window.performance.timing;
        const pageLoadTime = perf.loadEventEnd - perf.navigationStart;
        console.log('Page Load Time: ' + pageLoadTime + 'ms');
      });
    }
  };

  // ========================================
  // 13. Theme Switcher
  // ========================================
  const themeSwitcherInit = function() {
    const themeToggle = $('#theme-toggle');
    const themeDropdown = $('#theme-dropdown');
    const themeOptions = $('.theme-option');
    const resetThemeBtn = $('#reset-theme');

    if (!themeToggle.length) return;

    // Toggle dropdown
    themeToggle.on('click', function(e) {
      e.stopPropagation();
      themeDropdown.toggleClass('active');
    });

    // Close dropdown when clicking outside
    $(document).on('click', function(e) {
      if (!$(e.target).closest('.theme-switcher').length) {
        themeDropdown.removeClass('active');
      }
    });

    // Theme selection
    themeOptions.on('click', function() {
      const selectedTheme = $(this).data('theme');

      // Remove active class from all options
      themeOptions.removeClass('active');
      // Add active class to selected option
      $(this).addClass('active');

      // Apply theme
      applyTheme(selectedTheme);

      // Close dropdown
      themeDropdown.removeClass('active');

      // Show success notification
      showNotification('Theme changed successfully!', 'success');
    });

    // Reset theme
    resetThemeBtn.on('click', function() {
      // Remove active class from all options
      themeOptions.removeClass('active');
      // Add active to light theme (default)
      $('[data-theme="light"]').addClass('active');

      // Reset to default theme
      applyTheme('light');

      // Close dropdown
      themeDropdown.removeClass('active');

      // Show notification
      showNotification('Theme reset to default!', 'info');
    });

    // Load saved theme on page load
    loadSavedTheme();
  };

  // Apply theme function
  const applyTheme = function(theme) {
    // Remove existing theme data attribute
    document.documentElement.removeAttribute('data-theme');

    // Apply new theme if not light (light is default)
    if (theme !== 'light') {
      document.documentElement.setAttribute('data-theme', theme);
    }

    // Save to localStorage
    localStorage.setItem('selectedTheme', theme);

    // Update active state in theme switcher
    $('.theme-option').removeClass('active');
    $(`.theme-option[data-theme="${theme}"]`).addClass('active');
  };

  // Load saved theme
  const loadSavedTheme = function() {
    const savedTheme = localStorage.getItem('selectedTheme') || 'light';
    applyTheme(savedTheme);
  };

  // ========================================
  // 14. Notification System
  // ========================================
  const showNotification = function(message, type = 'info', duration = 3000) {
    // Remove existing notifications
    $('.notification').remove();

    // Create notification element
    const notification = $(`
      <div class="notification ${type}" role="alert">
        ${message}
      </div>
    `);

    // Add to body
    $('body').append(notification);

    // Auto remove after duration
    setTimeout(() => {
      notification.fadeOut(300, function() {
        $(this).remove();
      });
    }, duration);
  };

  // ========================================
  // 15. Enhanced Form Validation
  // ========================================
  const enhancedFormValidation = function() {
    // Enhanced form validation with better feedback
    $('form').on('submit', function(e) {
      const form = $(this);
      const submitBtn = form.find('button[type="submit"]');

      // Add loading state
      submitBtn.addClass('loading').prop('disabled', true);

      // Basic validation
      let isValid = true;
      form.find('input[required], select[required], textarea[required]').each(function() {
        if (!$(this).val().trim()) {
          $(this).addClass('is-invalid');
          isValid = false;
        } else {
          $(this).removeClass('is-invalid').addClass('is-valid');
        }
      });

      if (!isValid) {
        e.preventDefault();
        submitBtn.removeClass('loading').prop('disabled', false);
        showNotification('Please fill in all required fields.', 'error');
      } else {
        // Show loading message
        showNotification('Submitting form...', 'info', 1000);
      }
    });

    // Real-time validation
    $('input, select, textarea').on('blur', function() {
      const field = $(this);
      if (field.prop('required') && !field.val().trim()) {
        field.addClass('is-invalid');
      } else {
        field.removeClass('is-invalid').addClass('is-valid');
      }
    });
  };

  // ========================================
  // 16. Enhanced Search
  // ========================================
  const enhancedSearchInit = function() {
    const searchInputs = $('input[name="q"], input[placeholder*="search"]');

    searchInputs.each(function() {
      const searchInput = $(this);
      const searchForm = searchInput.closest('form');
      let searchTimeout;

      // Debounced search suggestions (if needed)
      searchInput.on('input', function() {
        clearTimeout(searchTimeout);
        const query = $(this).val();

        if (query.length > 2) {
          searchTimeout = setTimeout(() => {
            // Add loading state to search
            searchInput.addClass('loading');
            setTimeout(() => searchInput.removeClass('loading'), 500);
          }, 300);
        }
      });

      // Enhanced search form submission
      searchForm.on('submit', function(e) {
        const query = searchInput.val().trim();
        if (!query) {
          e.preventDefault();
          showNotification('Please enter a search term.', 'warning');
          searchInput.focus();
        }
      });
    });
  };

  // ========================================
  // 17. Accessibility Enhancements
  // ========================================
  const accessibilityInit = function() {
    // Enhanced keyboard navigation
    $('.theme-option, .theme-toggle-btn').on('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        $(this).click();
      }

      if (e.key === 'Escape') {
        $('#theme-dropdown').removeClass('active');
        $('#theme-toggle').focus();
      }
    });

    // Skip to main content link
    if (!$('#skip-to-main').length) {
      $('body').prepend('<a href="#main-content" id="skip-to-main" class="sr-only">Skip to main content</a>');
    }

    // Add main content landmark if not present
    if (!$('#main-content').length) {
      $('.container').first().attr('id', 'main-content');
    }
  };

  // ========================================
  // 18. Performance Enhancements
  // ========================================
  const performanceEnhancements = function() {
    // Lazy loading for images
    const lazyImages = $('img[data-src]');
    if (lazyImages.length && 'IntersectionObserver' in window) {
      const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src;
            img.classList.add('loaded');
            observer.unobserve(img);
          }
        });
      });

      lazyImages.each(function() {
        imageObserver.observe(this);
      });
    }

    // Debounce scroll events
    let scrollTimeout;
    $(window).on('scroll', function() {
      clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(() => {
        // Handle scroll-based features
        const scrollTop = $(window).scrollTop();

        // Add scrolled class for additional styling
        if (scrollTop > 100) {
          $('body').addClass('scrolled');
        } else {
          $('body').removeClass('scrolled');
        }
      }, 100);
    });
  };

  // ========================================
  // 19. Initialization on Document Ready
  // ========================================
  $(document).ready(function() {
    // Initialize all components
    stickyHeaderInit();
    mobileMenuInit();
    carouselsInit();
    isotopeInit();
    wowInit();
    counterInit();
    magnificPopupInit();
    smoothScrollInit();
    niceSelectInit();
    searchToggleInit();
    mailchimpInit();
    contactFormInit();

    // New enhancements
    themeSwitcherInit();
    enhancedFormValidation();
    enhancedSearchInit();
    accessibilityInit();
    performanceEnhancements();
    performanceMonitor();

    console.log('Ramat Library - All enhanced components initialized');
  });

  // ========================================
  // 16. Error Handling
  // ========================================
  window.addEventListener('error', function(event) {
    console.error('Global error caught:', event.error);
  });

  window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
  });

})(jQuery);
