function getPOLA3Rdata(COLUMN, URLSTR, FORMAT) {
    var xhttp = new XMLHttpRequest();
    var items = []

        /// This function is a catchall function that will append the ID values as pulled from a column in the filtered data table
        /// If the data to be accessed is the EXCEL format, then set the FORMAT argument to ("EXCEL" or "JSON")

    ///// IF YOU CHANGE THE LOCATION OF THE HIDDEN ID COLUMN, DON'T FORGET TO CHANGE THE COLUMN NUMBER    
    var myTable = $("#myTable").DataTable()
    var searData = myTable.rows({ search: 'applied' }).column(COLUMN, { search: 'applied' }).data()

    for (var i = 0; i < searData.length; i++) {
        items.push(searData[i])
    }

   
    if (FORMAT == "EXCEL") {
        console.log(URLSTR)
        searchURL = URLSTR.concat('?id=').concat(items)
        console.log(searchURL)
        window.open(searchURL, '_parent')
        
    } else if (FORMAT == "JSON") {
        searchURL = URLSTR.concat('?id__in=').concat(items)
        window.open(searchURL)
    }


}

