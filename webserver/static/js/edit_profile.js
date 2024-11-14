document.getElementById('edit-profile-btn')?.addEventListener('click', function() {
        var form = document.getElementById('bio-form');
        if (form.style.display === 'none') {
                form.style.display = 'block';
        } else {
                form.style.display = 'none';
        }
});