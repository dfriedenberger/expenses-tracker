$(document).ready(function () {

    fetchExpenses();
    
    // Fetch expenses from the backend
    function fetchExpenses() {
        $.get('/currencies/', function (currency_list) {
            $.get('/tags/', function (tags) {
                $.get('/expenses/', function (data) {
                    renderExpenses(data, tags, currency_list);
                })
            })
        })
    }

    // Render expenses list
    function renderExpenses(expenses, tags, currency_list) {
        const expensesList = $('#expenses-list');
        expensesList.empty();

        let expenseSource = $("#expense-template").html();
        let expenseTemplate = Handlebars.compile(expenseSource);

        expenses.forEach(expense => {

            //Map Tag-Id to Tag-Name
            expense.tag_categories = []
            expense.tag_tags       = []
            expense.tag_persons    = []
            expense.tag_locations  = []
            expense.tag_vacations  = []
            expense.tag_unknowns    = []

            expense.tags.forEach(tag => {
                let tag_config = tags.find(x => x.id === tag)
                console.log(tag, tag_config)

                if(!tag_config)
                {
                    console.log("Tag not found", tag)
                    expense.tag_unknowns.push(tag)
                    return
                }
                if (tag_config.tag_type == "category")
                    expense.tag_categories.push(tag_config.name)
                if (tag_config.tag_type == "person")
                    expense.tag_persons.push(tag_config.name)
                if (tag_config.tag_type == "tag")
                    expense.tag_tags.push(tag_config.name)
                if (tag_config.tag_type == "location")
                    expense.tag_locations.push(tag_config.name)
                if (tag_config.tag_type == "vacation")
                    expense.tag_vacations.push(tag_config.name)
            })

           
            console.log(expense.tag_unknowns)

            //Map date
            const date = new Date(expense.date);
            expense.date = date.toLocaleDateString("de-DE", { 
                weekday: "short", 
                day: "numeric", 
                month: "numeric", 
                year: "numeric"
            });

            //Map currency
            // get symbol of iso4217 currency
            if(expense.currency)
                expense.symbol_currency = currency_list.filter((c) => c.iso4217 == expense.currency).map((c) => c.symbol)[0];

            var html = expenseTemplate(expense);
            expensesList.append(html);
        });
    }

    //form

    //Currency
    function currency_calculate(price, currency, currencyList) {
        cur = currencyList.find(c => c.iso4217 === currency)
        if(cur) {
            return cur.factor * price
        }
        return undefined
    }

    function currency_init_list() {


        return new Promise((resolve, reject) => {
            $.get('/currencies/', function (data) {
                $('#currency').empty();
                data.forEach(currency => {
                    $('#currency').append($('<option>', {value: currency.iso4217, text:currency.symbol + ' - ' + currency.name}));
                })
                resolve(data);
            }).fail(function (error) {
                reject(error);
            });
          });

    }

    $(document).on('click', '#currency-form', function (ev) {
        ev.preventDefault()
        $("#currency-form-group").slideToggle()
    })


    $(document).on('click', '#convert-currency', function (ev) {
        ev.preventDefault()
        price_currency = $("#price_currency").val()
        currency = $("#currency").val()

        $.get('/currencies/', function (currencyList) {
            price_eur = currency_calculate(price_currency, currency, currencyList)
            // console.log(price_currency, currency, "=>" , price_eur)

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
    
            let last_tag_type = undefined
            data.forEach(tag => {

                if (last_tag_type && last_tag_type != tag.tag_type)
                    tagList.append("<hr />");
                last_tag_type = tag.tag_type

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
        "vacation" : {
            "enable_class": "btn-danger",
            "disable_class": "btn-outline-danger",
            "enable_icon": "bi-shield-minus",
            "disable_icon": "bi-shield-plus"
        },
    }

    function tag_enable(tag) {
        tag_type = $("#"+tag).data("tag-typ")
        config = tag_configuration[tag_type]

        $("#"+tag).removeClass(config["disable_class"])
        $("#"+tag).addClass(config["enable_class"])
        $("#"+tag).find(".bi").removeClass(config["disable_icon"])
        $("#"+tag).find(".bi").addClass(config["enable_icon"])
        $("#"+tag).data("enabled", true)
    }

    function tag_disable(tag) {
        tag_type = $("#"+tag).data("tag-typ")
        config = tag_configuration[tag_type]

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
    $(document).on('click', '.btn-new', async function () {

        $("#expenseModalLabel").text("Neue Ausgabe")

        $("#title").val("")
        $("#price").val("")

        const todayISO = new Date().toISOString().split('T')[0];
        $("#date").val(todayISO)

        tags_set_value([])

        await currency_init_list()
        $("#currency").val("")
        $("#price_currency").val("")
        $("#currency-form-group").hide(0)
        
        $('#confirm-save-btn').removeData( "id" );
        $('#expenseModal').modal('show');

    })

    // Handle edit button click
    $(document).on('click', '.btn-edit', function () {
        const expenseId = $(this).closest('.expense-item').data('id');

        $.ajax({
            url: `/expenses/${expenseId}`,
            type: 'GET',
            success: async function (data) {
                console.log(data)
                $("#expenseModalLabel").text("Bearbeiten")
                $("#title").val(data.title)
                $("#price").val(data.price)
                $("#date").val(data.date)

                tags_set_value(data.tags)
                currency_list = await currency_init_list()
                $("#currency").val(data.currency)
                $("#price_currency").val(data.price_currency)
                $("#currency-form-group").hide(0)

                $('#confirm-save-btn').data('id', expenseId);
                $('#expenseModal').modal('show');
            }
        });

    });

    //handle New tag Button
    $(document).on('click', '.btn-new-tag', async function () {

        $("#tagModalLabel").text("Neuer Tag")

        $("#tag-name").val("")
        $("#tag-id").val("")

        //handle input in field name
        $('#tag-name').on('input', function() {
            let n  = $(this).val()
            $("#tag-id").val(n.toLowerCase().replace(/ /g, "_"))
        })

        $("#tag-type").val("vacation")
        $('#tagModal').modal('show');

    })

    //handle save tag Button
    $('#tag-form').on('submit', function (e) {
        e.preventDefault();
        const tag = {
            name: $('#tag-name').val(),
            id: $('#tag-id').val(),
            tag_type: $('#tag-type').val(),
        };

        $.ajax({
            type: "POST",  
            url: "/tags/",
            data: JSON.stringify(tag),  
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data){
                $('#tagModal').modal('hide');
            },
        });

    })

    //Statistics
    $(document).on('click', '.btn-statistic-week', function () {
        year = $(this).data("year")
        week = $(this).data("week")

        console.log(year, week)

        if(year && week)
        {
            get_statistic_week(year, week)
            return
        }
        $.get('/util/kw/', function (data) {
            get_statistic_week(data.year, data.week)

        })
    })
   

    $(document).on('click', '.btn-statistic-month', function () {
        year = $(this).data("year")
        month = $(this).data("month")

        console.log(year, month)

        if(year && month)
        {
            get_statistic_month(year, month)
            return
        }
        $.get('/util/month/', function (data) {
            get_statistic_month(data.year, data.month)
        })
    })

    $(document).on('click', '.btn-statistic-vacation', function () {
        year = $(this).data("year")
        console.log(year)

        if(year)
        {
            get_statistic_vacation(year)
            return
        }
        $.get('/util/month/', function (data) {
            get_statistic_vacation(data.year)
        })
        get_statistic_vacation()
    })

    let weekChart;
    function get_statistic_week(year, week) {

        $.get('/statistic/week/', { year: year, week: week }, function (statistic) {

                const ctx = document.getElementById('statistic-week-chart').getContext('2d');
    
                $("#statistic-week-title").text(statistic.title)
                $("#statistic-week-subtitle").text(statistic.subtitle)
                $("#statistic-next-week").data("year",statistic.next_week_year)
                $("#statistic-next-week").data("week",statistic.next_week)
                $("#statistic-last-week").data("year",statistic.last_week_year)
                $("#statistic-last-week").data("week",statistic.last_week)

                let l = statistic.data.length

                let data_ist = Array(l)
                let data_rest = Array(l)
                let data_oversized = Array(l)

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


                if (weekChart) {
                    weekChart.destroy();
                }
    
                weekChart = new Chart(ctx, {
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
                        onClick: function(_,i) {
                            if(i.length > 0) {
                                category_id = i[0].index
                                //dataset_ix = i[0].datasetIndex
                                open_statistic_category(category_id, 'week')
                            }
                    
                        }
                    }
                });
      

            
                //statistic details
                create_statistic_categories($('#statistic-week-details'), 'week', statistic, "Wöchentliches Budget")
        
        })
        $('#statisticWeekModal').modal('show');
    }

    let monthChart;
    function get_statistic_month(year, month) {
        console.log("get_statistic_month", year, month);
        $.get('/statistic/month/', { year: year, month: month }, function (statistic) {
            console.log(statistic)

            const ctx = document.getElementById('statistic-month-chart').getContext('2d');

            $("#statistic-month-title").text(statistic.title)
            $("#statistic-next-month").data("year",statistic.next_month_year)
            $("#statistic-next-month").data("month",statistic.next_month)
            $("#statistic-last-month").data("year",statistic.last_month_year)
            $("#statistic-last-month").data("month",statistic.last_month)

            if (monthChart) {
                monthChart.destroy();
            }

            // statistic.data summieren und summe runden
            let summe = 0;
            for(var i = 0;i < statistic.data.length;i++)
                summe += statistic.data[i];
            summe = Math.round(summe * 100) / 100;



            let sparen = statistic.limit - summe;
            if(sparen < 0)
                sparen = 0; 

            sparen = Math.round(sparen * 100) / 100;
            let data = statistic.data.slice()
            data.push(sparen)

            let labels = statistic.labels.slice()
            labels.push("Sparen")

            let COLORS = ['#1E90FF', '#32CD32', '#FF6347', '#FFA500', '#8A2BE2', '#FFD700', '#00CED1', '#FF69B4', '#ADFF2F', '#FF4500'];
            let colors = COLORS.slice(statistic.data.length)
            colors.push("#aaaaaa") //grau für sparen

            monthChart = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: colors,
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(tooltipItem) {
                                    return tooltipItem.label + ': ' + tooltipItem.raw + ' €';
                                }
                            }
                        }
                    },
                    onClick: function(_,i) {
                        if(i.length > 0) {
                            category_id = i[0].index
                            open_statistic_category(category_id,'month')
                        }
                
                    }
                }
            });

            //table
            const statisticTable = $('#statistic-month-table');
            statisticTable.empty();

            for(var i = 0;i < statistic.labels.length;i++) {
                var row = $('<tr>');
                row.append($('<td>').text(statistic.labels[i]));
                row.append($('<td>').text(statistic.data[i] + ' €'));
                statisticTable.append(row);
            }   
            var row = $('<tr>');
            row.append($('<td>').html($('<strong>').text("Summe")));
            row.append($('<td>').text(summe + ' €'));
            statisticTable.append(row);

            $("#statistic-month-budget").text(statistic.limit + ' €');

            $("#statistic-month-sparen").text(sparen + ' €');   

            //statistic details
            create_statistic_categories($('#statistic-month-details'), 'month', statistic, "Monatliches Budget")

            $('#statisticMonthModal').modal('show');

        })
    }

    function get_statistic_vacation(year) {
        console.log("get_statistic_vacation", )
    }




    //util functions for weekly statistic
    let open_statistic_category_index = -1

    function create_statistic_categories(statisticDetails, statisticClass, statistic, limittext) {

        let l = statistic.data.length

        statisticDetails.empty();

        let expenseSource = $("#expense-short-template").html();
        let expenseTemplate = Handlebars.compile(expenseSource);
        let expenseSourceSum = $("#expense-sum-template").html();
        let expenseTemplateSum = Handlebars.compile(expenseSourceSum);
        for(var i = 0;i < l;i++) {

            console.log(statistic.labels[i], statistic.expenses[i])
            statisticDetails.append("<div id='statistic-category-"+statisticClass+"-"+i+"' style='display:none'><h5>"+statistic.labels[i]+"</h5></div>")
            statistic.expenses[i].forEach(expense => {                    
                //Map date
                const date = new Date(expense.date);
                expense.date = date.toLocaleDateString("de-DE", { 
                    weekday: "short", 
                    day: "numeric", 
                    month: "numeric", 
                    year: "numeric"
                });

                console.log(expense)

                var html = expenseTemplate(expense);
                $("#statistic-category-"+statisticClass+"-"+i).append(html);
            });

            var html = expenseTemplateSum({"sum" : statistic.data[i], "limit": statistic.limits[i], "limittext" : limittext })
            $("#statistic-category-"+statisticClass+"-"+i).append(html);
        }
        open_statistic_category_index = -1
    }


    function open_statistic_category(i, statisticClass) {

        console.log("open_statistic_category", i, open_statistic_category_index)
        if(open_statistic_category_index == i)
            return;
        
        $("#statistic-category-"+statisticClass+"-"+i).slideDown();


        if(open_statistic_category_index >= 0) {
            $("#statistic-category-"+statisticClass+"-"+open_statistic_category_index).slideUp();
        }
        open_statistic_category_index = i


    }


});
