$(document).ready(function () {

    fetchExpenses();
    
    // Fetch expenses from the backend
    function fetchExpenses() {
        $.get('/tags/', function (tags) {
            $.get('/expenses/', function (data) {
                renderExpenses(data, tags);
            })
        })
    }

    // Render expenses list
    function renderExpenses(expenses, tags) {
        const expensesList = $('#expenses-list');
        expensesList.empty();

        var expenseSource = $("#expense-template").html();
        var expenseTemplate = Handlebars.compile(expenseSource);

        expenses.forEach(expense => {

            //Map Tag-Id to Tag-Name
            expense.tag_categories = []
            expense.tag_tags       = []
            expense.tag_persons    = []
            expense.tag_locations    = []

            expense.tags.forEach(tag => {
                let tag_config = tags.find(x => x.id === tag)

                if (tag_config.tag_typ == "category")
                    expense.tag_categories.push(tag_config.name)
                if (tag_config.tag_typ == "person")
                    expense.tag_persons.push(tag_config.name)
                if (tag_config.tag_typ == "tag")
                    expense.tag_tags.push(tag_config.name)
                if (tag_config.tag_typ == "location")
                    expense.tag_locations.push(tag_config.name)
            })

           
            //Map date
            const date = new Date(expense.date);
            expense.date = date.toLocaleDateString("de-DE", { 
                weekday: "short", 
                day: "numeric", 
                month: "numeric", 
                year: "numeric"
            });

            var html = expenseTemplate(expense);
            expensesList.append(html);
        });
    }

    //form

    //Currency
    function currency_calculate(price, currency, currencyList) {
        cur = currencyList.find(c => c.shortcut === currency)
        if(cur) {
            return cur.factor * price
        }
        return undefined
    }

    function currency_init_list() {

        $.get('/currency/', function (data) {
            
            $('#currency').empty();
            data.forEach(currency => {
                $('#currency').append($('<option>', {value: currency.shortcut, text:currency.shortcut + ' - ' + currency.name}));
            })
        })
    }

    $(document).on('click', '#currency-form', function (ev) {
        ev.preventDefault()
        $("#currency-form-group").slideToggle()
    })

    $(document).on('click', '#convert-currency', function (ev) {
        ev.preventDefault()
        price_currency = $("#price_currency").val()
        currency = $("#currency").val()

        $.get('/currency/', function (currencyList) {
            price_eur = currency_calculate(price_currency, currency, currencyList)
            console.log(price_currency, currency, "=>" , price_eur)

            $("#price").val(price_eur)
            $("#currency-form-group").slideUp()
        })
      
    })
    //Tags
    function tags_set_value(tags) {

        $.get('/tags/', function (data) {
            
            const tagList = $('#tags');
            tagList.empty();

            var source = $("#tags-template").html();
            var template = Handlebars.compile(source);
    
            let last_tag_typ = undefined
            data.forEach(tag => {

                if (last_tag_typ && last_tag_typ != tag.tag_typ)
                    tagList.append("<hr />");
                last_tag_typ = tag.tag_typ

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

    var tag_configuration = {
        "category" : {
            "enable_class": "btn-primary",
            "disable_class": "btn-outline-primary",
            "enable_icon": "bi-shield-minus" ,
            "disable_icon": "bi-shield-plus"
        },
        "person" : {
            "enable_class": "btn-success",
            "disable_class": "btn-outline-success",
            "enable_icon": "bi-person-fill-dash",
            "disable_icon": "bi-person-fill-add"
        },
        "tag" : {
            "enable_class": "btn-info",
            "disable_class": "btn-outline-info",
            "enable_icon": "bi-shield-minus" ,
            "disable_icon": "bi-shield-plus"
        },
        "location" : {
            "enable_class": "btn-warning",
            "disable_class": "btn-outline-warning",
            "enable_icon": "bi-house-dash-fill",
            "disable_icon": "bi-house-add-fill"
        },
    }

    function tag_enable(tag) {
        tag_typ = $("#"+tag).data("tag-typ")
        config = tag_configuration[tag_typ]

        $("#"+tag).removeClass(config["disable_class"])
        $("#"+tag).addClass(config["enable_class"])
        $("#"+tag).find(".bi").removeClass(config["disable_icon"])
        $("#"+tag).find(".bi").addClass(config["enable_icon"])
        $("#"+tag).data("enabled", true)
    }

    function tag_disable(tag) {
        tag_typ = $("#"+tag).data("tag-typ")
        config = tag_configuration[tag_typ]

        $("#"+tag).removeClass(config["enable_class"])
        $("#"+tag).addClass(config["disable_class"])
        $("#"+tag).find(".bi").removeClass(config["enable_icon"])
        $("#"+tag).find(".bi").addClass(config["disable_icon"])
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
            date: $('#date').val(),
            tags: tags_getValues(),
            currency: undefined,
            price_currency: undefined
        };

        price_currency = $('#price_currency').val()
        if (price_currency)
        {
            expense.currency = $('#currency').val()
            expense.price_currency = price_currency
        }

        
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

        const todayISO = new Date().toISOString().split('T')[0];
        $("#date").val(todayISO)

        tags_set_value([])

        currency_init_list()
        $("#currency").val("")

        $('#confirm-save-btn').removeData( "id" );
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
                $("#date").val(data.date)

                tags_set_value(data.tags)
                currency_init_list()
                $("#currency").val(data.currency)
                $("#price_currency").val(data.price_currency)

                $('#confirm-save-btn').data('id', expenseId);
                $('#expenseModal').modal('show');
            }
        });

    });


    //Statistics
    let myChart;
    $(document).on('click', '.btn-statistic', function () {
        year = $(this).data("year")
        week = $(this).data("week")

        console.log(year, week)

        if(year && week)
        {
            get_statistic(year, week)
            return
        }
        $.get('/util/kw/', function (data) {
            get_statistic(data.year, data.week)

        })
    })
   


    function get_statistic(year, week) {

        $.get('/statistic/', { year: year, week: week }, function (statistic) {

                const ctx = document.getElementById('myChart').getContext('2d');
    
                $("#statistic-title").text(statistic.title)
                $("#statistic-subtitle").text(statistic.subtitle)
                $("#statistic-next-week").data("year",statistic.next_week_year)
                $("#statistic-next-week").data("week",statistic.next_week)
                $("#statistic-last-week").data("year",statistic.last_week_year)
                $("#statistic-last-week").data("week",statistic.last_week)

                l = statistic.data.length
                data_ist = Array(l)
                data_rest = Array(l)
                data_oversized = Array(l)
                for(var i = 0;i < l;i++)
                {
                    if(statistic.data[i] <= statistic.limits[i]) 
                    {
                        data_ist[i] = statistic.data[i];
                        data_rest[i] = statistic.limits[i] - statistic.data[i];
                        data_oversized[i] = 0
                    }
                    else
                    {
                        data_ist[i] = statistic.limits[i];
                        data_rest[i] = 0;
                        data_oversized[i] = statistic.data[i] - statistic.limits[i];
                    }
                }
                
              

                const data = {
                    labels: statistic.labels,
                    datasets: [
                        {
                            label: 'Im Limit',
                            data: data_ist,
                            backgroundColor: 'rgb(80, 180, 60)', // Weicheres Grün
                            borderColor: 'rgb(39, 87, 30)',
                        },
                        {
                            label: 'Verfügbar',
                            data: data_rest,
                            backgroundColor: 'rgba(80, 180, 60, 0.22)', // Weicheres Grün
                            borderColor: 'rgba(46, 102, 35, 0.22)',
                        },
                        {
                            label: 'Überschritten',
                            data: data_oversized,
                            backgroundColor: 'rgb(220, 100, 60)', // Weniger grelles Rot
                            borderColor: 'rgb(135, 62, 37)',
                        },
                    ]
                };


                if (myChart) {
                    myChart.destroy();
                }
    
                myChart = new Chart(ctx, {
                    type: 'bar',
                    data: data,
                    options: {
                        scales: {
                            x: {
                                stacked: true
                            },
                            y: {
                                stacked: true,
                                //min: 100,
                                suggestedMax: statistic.suggestedMax // Empfohlener Maximalwert der Y-Achse
                            }
                        },
                        responsive: true,
                    }
                });
      



        })
        $('#statisticModal').modal('show');
    }



});
