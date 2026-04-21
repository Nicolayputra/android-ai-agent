(function($) {
    "use strict";

    // Preloader
    $(window).on('load', function() {
        $('.preloader').fadeOut('slow');
    });

    // Sidebar Toggle
    $('.side-menu-button').on('click', function() {
        $('.content-sidebar').addClass('active');
    });

    $('.sidebar-close').on('click', function() {
        $('.content-sidebar').removeClass('active');
    });

    // Sticky Header
    $(window).on('scroll', function() {
        if ($(this).scrollTop() > 100) {
            $('.main-header').addClass('sticky-header');
        } else {
            $('.main-header').removeClass('sticky-header');
        }
    });

    // Counter Up
    if($('.count').length){
        $('.count').each(function () {
            $(this).prop('Counter',0).animate({
                Counter: $(this).data('to')
            }, {
                duration: $(this).data('speed'),
                easing: 'swing',
                step: function (now) {
                    $(this).text(Math.ceil(now));
                }
            });
        });
    }

    // Scroll to Top
    $(window).on('scroll', function() {
        if ($(this).scrollTop() > 300) {
            $('.scroll-to-top').fadeIn();
        } else {
            $('.scroll-to-top').fadeOut();
        }
    });

    // Form Submission (Simulated)
    $('.contact-form').on('submit', function(e) {
        e.preventDefault();
        alert('Pesan Anda telah terkirim. Terima kasih!');
        $(this).trigger('reset');
    });

    $('.newsletter-form').on('submit', function(e) {
        e.preventDefault();
        alert('Terima kasih telah mendaftar!');
        $(this).trigger('reset');
    });

})(jQuery);
