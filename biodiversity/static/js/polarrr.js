function getallJSONbyID(COLUMN,URLSTR) {
    var items = []

    ///// IF YOU CHANGE THE LOCATION OF THE HIDDEN ID COLUMN, DON'T FORGET TO CHANGE THE COLUMN NUMBER    
    var myTable = $("#myTable").DataTable()
    var searData = myTable.rows({ search: 'applied' }).column(COLUMN, { search: 'applied' }).data()

    for (var i = 0; i < searData.length; i++) {
        items.push(searData[i])
    }

    searchURL = '/pola3r/'.concat(URLSTR).concat('/?id=').concat(items)
    window.open(searchURL)

}



