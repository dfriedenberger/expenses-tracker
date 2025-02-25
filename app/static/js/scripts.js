$(document).ready(function () {

    fetchExpenses();
    
    // Fetch expenses from the backend
    function fetchExpenses() {
        $.get('/tags/', function (tags) {
            $.get('/currency/', function (currency) {
                $.get('/expenses/', function (data) {
                    renderExpenses(data, tags, currency);
                })
            })
        })
    }

    //Utils
    function calculate(price, currency, currencyList) {
        cur = currencyList.find(c => c.shortcut === currency)
        if(cur) {
            return cur.factor * price
        }
        return undefined
    }


    // Render expenses list
    function renderExpenses(expenses, tags, currency) {
        const expensesList = $('#expenses-list');
        expensesList.empty();

        var expenseSource = $("#expense-template").html();
        var expenseTemplate = Handlebars.compile(expenseSource);

        expenses.forEach(expense => {

            //Map Tag-Id to Tag-Name
            tag_names = []
            expense.tags.forEach(tag => {
                tag_name = tags.find(x => x.id === tag).name;
                tag_names.push(tag_name)
            })
            expense.tags = tag_names
           
            //Map date
            const date = new Date(expense.date);
            expense.date = date.toLocaleDateString("de-DE", { 
                weekday: "short", 
                day: "numeric", 
                month: "numeric", 
                year: "numeric"
            });


            //Map Currency
            if(expense.currency != "€")
            {
                expense.price_eur = calculate(expense.price, expense.currency, currency)
            }


            var html = expenseTemplate(expense);
            expensesList.append(html);
        });
    }

    //form

    //Currency
    function currency_init_list() {

        $.get('/currency/', function (data) {
            
            const currencyList = $('#currency-list');
            currencyList.empty();

            var source = $("#currency-template").html();
            var template = Handlebars.compile(source);
    
            data.forEach(currency => {
                var html = template(currency);
                currencyList.append(html);
            });
        })
    }

    $(document).on('click', '#currency', function (ev) {
        ev.preventDefault()
        $("#currency-list").slideToggle()
    })

    $(document).on('click', '.currency', function (ev) {
        ev.preventDefault()
        currency = $(this).data('currency')

        console.log(currency)
        $("#currency").val(currency)
        $("#currency-list").slideUp()

    })
    //Tags
    function tags_set_value(tags) {

        $.get('/tags/', function (data) {
            
            const tagList = $('#tags');
            tagList.empty();

            var source = $("#tags-template").html();
            var template = Handlebars.compile(source);
    
            data.forEach(tag => {
                var html = template(tag);
                tagList.append(html);

                if(tags.includes(tag.id))
                {
                    tag_enable(tag.id)
                }
                else
                {
                    tag_disable(tag.id)
                }

            });


        });

    }

    function tag_is_enabled(tag) {
        return $("#"+tag).data("enabled")
    }

    function tag_enable(tag) {
        $("#"+tag).removeClass("btn-outline-primary")
        $("#"+tag).addClass("btn-primary")
        $("#"+tag).find(".bi").removeClass("bi-shield-plus")
        $("#"+tag).find(".bi").addClass("bi-shield-minus")
        $("#"+tag).data("enabled", true)
    }

    function tag_disable(tag) {
        $("#"+tag).removeClass("btn-primary")
        $("#"+tag).addClass("btn-outline-primary")
        $("#"+tag).find(".bi").removeClass("bi-shield-minus")
        $("#"+tag).find(".bi").addClass("bi-shield-plus")
        $("#"+tag).data("enabled", false)
    }

    function tags_getValues() {
        tags = []
        $("#tags").children().each(function() {
            tag = $(this).attr('id')
            if(tag_is_enabled(tag))
            {
                tags.push(tag)
            }
        })
        return tags
    }

    $(document).on('click', '.tag', function () {
        tag = $(this).attr('id')

        if(tag_is_enabled(tag))
        {
            tag_disable(tag)
        }
        else
        {
            tag_enable(tag)
        }

    })
   
  
    // Handle form submission for new or edited expense
    $('#expense-form').on('submit', function (e) {
        e.preventDefault();
        const expense = {
            title: $('#title').val(),
            price: $('#price').val(),
            currency: $('#currency').val(),
            date: $('#date').val(),
            tags: tags_getValues()
        };
        
        var url = "/expenses/";
        var type = "POST"
        var expenseId = $('#confirm-save-btn').data('id');
        console.log("expenseId",expenseId)

        if(expenseId)
        {
            expense.id = expenseId;
            type = "PUT"
            url = `/expenses/${expenseId}`;
        }


        $.ajax({
            type: type,
            url: url,
            data: JSON.stringify(expense),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data){
                fetchExpenses();
                $('#expenseModal').modal('hide');
            },
            failure: function(errMsg) {
                alert(errMsg);
            }
        });

    });


    //Close Button
    $(document).on('click', '.close-modal', function () {
        $(this).closest('.modal').modal('hide')
    })

    // Handle delete button click
    $(document).on('click', '.btn-delete', function () {
        const expenseId = $(this).closest('.expense-item').data('id');
        $('#confirm-delete-btn').data('id', expenseId);
        $('#confirmDeleteModal').modal('show');
    });

    // Confirm delete action
    $('#confirm-delete-btn').on('click', function () {
        const expenseId = $(this).data('id');

        $.ajax({
            url: `/expenses/${expenseId}`,
            type: 'DELETE',
            success: function () {
                fetchExpenses();
                $('#confirmDeleteModal').modal('hide');
            }
        });
    });

    // Handle new button click
    $(document).on('click', '.btn-new', function () {

        $("#expenseModalLabel").text("Neue Ausgabe")

        $("#title").val("")
        $("#price").val("")
        $("#currency").val("€")

        const todayISO = new Date().toISOString().split('T')[0];
        $("#date").val(todayISO)

        tags_set_value([])

        currency_init_list()

        $('#confirm-save-btn').data('id', undefined);
        $('#expenseModal').modal('show');

    })

    // Handle edit button click
    $(document).on('click', '.btn-edit', function () {
        const expenseId = $(this).closest('.expense-item').data('id');

        $.ajax({
            url: `/expenses/${expenseId}`,
            type: 'GET',
            success: function (data) {
                console.log(data)
                $("#expenseModalLabel").text("Bearbeiten")
                $("#title").val(data.title)
                $("#price").val(data.price)
                $("#currency").val(data.currency)
                $("#date").val(data.date)

                tags_set_value(data.tags)
                currency_init_list()

                $('#confirm-save-btn').data('id', expenseId);
                $('#expenseModal').modal('show');
            }
        });

    });

});
