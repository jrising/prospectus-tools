#' Extract a polynomial model
#'
#' Identify a polynomial model for use in DMAS after uploadingit with
#' dmas.put.model.
#' @param apikey API Key provided by DMAS
#' @param coeffs list of coefficients, e.g. c('lin', 'quad', 'cub')
#' @param lowbound lower bound
#' @param highbound upper bound
#' @param infoid An InfoID (gcp or from the DMAS spreadsheet)
#' @param id ID returned by dmas.put.model (or NA for last)
#' @export
dmas.extract.polynomial <- function(apikey, coeffs, lowbound, highbound, infoid, id=NA) {
    if (is.na(id)) {
        print("id not provided; using last result")
        id <- DMAS_LAST_RESULT
    }

    coeffs2 <- gsub("#", "%23", coeffs)

    dmas.urlstr <- sprintf("extract_estimate_polynomial?apikey=%s&coeffs=%s&lowbound=%f&highbound=%f&infoid=%s&id=%s", apikey, paste(coeffs2, collapse=','), lowbound, highbound, infoid, id)

    dmas.get.api(dmas.urlstr, as.model=T)
}
