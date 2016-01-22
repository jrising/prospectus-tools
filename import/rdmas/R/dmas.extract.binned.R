#' Extract a binned model
#'
#' Identify a binned model for use in DMAS after uploading it with
#' dmas.put.model.
#' @param apikey API Key provided by DMAS
#' @param endpoints list of endpoints, e.g. c('-inf', .2, .4, 'inf')
#' @param coeffs list of coefficients, with 'drop' for the dropped
#'     bin, e.g. c('c1', 'drop', 'c3')
#' @param infoid An InfoID (gcp or from the DMAS spreadsheet)
#' @param id ID returned by dmas.put.model (or NA for last)
#' @export
dmas.extract.binned <- function(apikey, endpoints, coeffs, infoid, id=NA) {
    if (is.na(id)) {
        print("id not provided; using last result")
        id <- DMAS_LAST_RESULT
    }

    dmas.urlstr <- sprintf("extract_estimate_binned?apikey=%s&endpoints=%s&coeffs=%s&infoid=%s&id=%s", apikey, paste(endpoints, collapse=","), paste(coeffs, collapse=","), infoid, id)

    dmas.get.api(dmas.urlstr, as.model=T)
}
