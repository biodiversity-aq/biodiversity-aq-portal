# This R Script demonstrates how to parse the POLA3R spreadsheet 
# to a joined data frame that can be used for analysis in R. 
# Author:  Grant Humphries
# Date: March 31, 2020

require(tidyverse)
require(readxl)

# We use the tidyverse library (version 1.3.0 in R 3.6.3)
# We also use the readxl package 1.3.1

setwd('PATH.TO.WHERE.YOUR.WORKBOOK.IS.FOUND')  #E.G., "C:/temp"

Workbook <- "POLA3R_project_metadata_2020-03-29.xlsx"

Worksheets <- Workbook %>% excel_sheets()

DAT <- sapply(Worksheets,function(x) readxl::read_excel(Workbook,sheet=x))

#### All of the data sheets are now found in the DAT variable
#### They can be accessed by doing the following in your console or script:

##  e.g.  DAT$Sequences 

#################################

## The data sheets can be merged for analysis if you need to link data across worksheets

MERGED <- full_join(DAT$`Project metadata`,DAT$Sequences,by=c('project_name'))

## A tibble: 4 x 32
#project_name start_date          end_date            EML_URL abstract geome associated_media
#<chr>        <dttm>              <dttm>              <lgl>   <lgl>    <chr> <lgl>           
#  1 Test         2020-03-25 00:00:00 2020-03-27 00:00:00 NA      NA       "{\"~ NA              
#2 Test         2020-03-25 00:00:00 2020-03-27 00:00:00 NA      NA       "{\"~ NA              
#3 Test         2020-03-25 00:00:00 2020-03-27 00:00:00 NA      NA       "{\"~ NA              
#4 Test         2020-03-25 00:00:00 2020-03-27 00:00:00 NA      NA       "{\"~ NA              

## For more join methods, please refer to the DPLYR documentation:
##    https://dplyr.tidyverse.org/reference/join.html



#############################################################################################











