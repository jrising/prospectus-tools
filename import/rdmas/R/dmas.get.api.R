#' Low-level function for accessing the API
#'
#' Clearing-house function for calling the DMAS API
#' @param methodargs The URL string, after the server; eg. test?arg=3
#' @param as.model Should we interpret the result as a model ID?
#' @param quietly Should an OK result be silent?
#' @export

dmas.get.api <- function(methodargs, as.model, quietly=F) {
    ## Change the server for all commands here
    server <- "http://127.0.0.1:8080"
    ## Local: "http://dmas.berkeley.edu"

    dmas.urlstr <- paste0(server, "/api/", methodargs)

    if (!quietly) {
        print(dmas.urlstr)
    }

    ## Repeat the request until we get a non-network error
    con <- url(dmas.urlstr)
    result <- readLines(con, warn=F)
    close(con)

    if (!quietly | result != "OK") {
        print("Response:")
        if (!as.model | substr(result, 1, 6) == "ERROR:") {
            print(result)
            if (substr(result, 1, 6) != "ERROR:") {
                ## Assume this is an ID to be used later
                DMAS_LAST_RESULT <<- result
            }
        }
        else {
            print(paste0(server, "/model/view?id=", result))
        }
    }
}
