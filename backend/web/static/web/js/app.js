(function () {
    // let pageSize = document.getElementById('pageSize')
    // let paginationForm = document.getElementById('paginationForm')
    // pageSize.addEventListener('change', function (e) {
    //     console.log(e.target.value)
    //     paginationForm.submit()
    // })

    function autoSubmit(e) {
        let el = e.target
        let form = el.closest('form')
        if (form) {
            form.submit()
        }
    }
})();